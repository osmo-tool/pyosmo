# TLA+ Investigation for PyOsmo Engine Verification

## Executive Summary

This document investigates whether TLA+ (Temporal Logic of Actions) can help verify the correctness of the PyOsmo model-based testing engine. The investigation covers three dimensions:

1. **Engine Verification**: Using TLA+ to formally verify PyOsmo's internal execution logic
2. **Algorithm Correctness**: Proving properties of step-selection algorithms
3. **Meta-level Relationship**: The conceptual overlap between TLA+ formal methods and PyOsmo's MBT approach

**Verdict**: TLA+ is well-suited for verifying specific critical aspects of PyOsmo's engine, particularly the execution loop state machine, error strategy cascade, and algorithm fairness properties. However, the effort is only justified for the core state machine and algorithm correctness proofs—not for the entire codebase.

---

## 1. Background: What TLA+ Offers

TLA+ is a formal specification language for modeling and verifying systems as state machines. Its model checker (TLC) exhaustively explores all reachable states and checks:

- **Safety Properties (Invariants)**: "Bad things never happen" — a condition that must hold in every reachable state
- **Liveness Properties**: "Good things eventually happen" — something that must occur in every possible execution
- **Fairness**: Guarantees that enabled actions are eventually taken (weak/strong fairness)
- **Action Properties**: Constraints on state *transitions* (pairs of states)

TLA+ excels at finding subtle bugs in state machines, scheduling algorithms, and concurrent systems where the interleaving of operations creates complex emergent behavior.

---

## 2. PyOsmo Engine as a State Machine

### 2.1 The Core Execution State Machine

PyOsmo's `generate()` method (`pyosmo/osmo.py:93-130`) implements a nested state machine:

```
STATES:
  IDLE → SUITE_RUNNING → TEST_RUNNING → STEP_EXECUTING → TEST_RUNNING → ...

TRANSITIONS:
  IDLE           --[generate()]-→  SUITE_RUNNING
  SUITE_RUNNING  --[start_new_test()]-→  TEST_RUNNING
  TEST_RUNNING   --[algorithm.choose()]-→  STEP_EXECUTING
  STEP_EXECUTING --[step completes]-→  TEST_RUNNING
  TEST_RUNNING   --[end_test = true]-→  SUITE_RUNNING
  SUITE_RUNNING  --[end_suite = true]-→  IDLE
  ANY            --[error + raise]-→  ERROR_HANDLING → SUITE_RUNNING or IDLE
```

### 2.2 Key State Variables

| Variable | Type | Transitions |
|----------|------|-------------|
| `history.test_cases` | List | Append-only growth |
| `current_test_case` | Record | Created/stopped per test |
| `current_test_case.steps_log` | List | Append during test |
| `algorithm state` | Varies | Updated per choose() |
| `error count` | Counter | Monotonically increasing |

### 2.3 Why This Matters

The engine has complex control flow with:
- Two-level error handling (test-level and suite-level strategies)
- Lifecycle hooks that can themselves raise exceptions
- End conditions checked at different points in the loop
- History state that must remain consistent across all paths

---

## 3. Specific TLA+ Application Areas

### 3.1 Lifecycle Hook Ordering Invariant (HIGH VALUE)

**Problem**: PyOsmo guarantees a strict execution order for lifecycle hooks:
```
before_suite → (before_test → (before → pre_X → step → post_X → after)* → after_test)* → after_suite
```

**Safety Property to Verify**:
```tla
TypeInvariant ==
  /\ phase \in {"idle", "suite", "test", "step"}
  /\ hook_stack is well-formed (no after without before)

HookOrdering ==
  /\ phase = "step" => last_hook \in {"before", "pre_step"}
  /\ phase = "test" => last_hook \in {"before_test", "after"}
  /\ after_suite_called => before_suite_called
  /\ after_test_called => before_test_called
```

**What TLA+ Would Find**: Whether any error path (exception in a hook, error strategy decision) can violate the hook ordering—e.g., calling `after_test` without `before_test` having completed, or skipping `after_suite` on error.

**Current Risk in Code**: The `try/except BaseException` at `osmo.py:125` catches errors from the inner loop and passes them to `test_suite_error_strategy`. If the strategy doesn't re-raise, execution continues to the next test. But `after_test` is called *before* this catch block (`osmo.py:123`), meaning an error in `after_test` itself would skip to the suite-level handler. This is correct but subtle—TLA+ would verify all such paths.

### 3.2 Error Strategy Cascade (HIGH VALUE)

**Problem**: PyOsmo has a two-level error handling system:
1. Step error → `test_error_strategy.failure_in_test()` (may raise or swallow)
2. If raised → `test_suite_error_strategy.failure_in_suite()` (may raise or continue)

**Properties to Verify**:
```tla
\* Safety: No error is silently lost when AlwaysRaise is configured
ErrorNeverLost ==
  /\ error_strategy = "AlwaysRaise" =>
     (error_occurred => eventually_raised)

\* Safety: AllowCount correctly tracks error counts
AllowCountCorrect ==
  /\ allow_count_strategy =>
     (error_count <= allow_count => test_continues)
  /\ (error_count > allow_count => error_raised)

\* Liveness: Under AlwaysIgnore, suite eventually terminates
IgnoreTerminates ==
  /\ error_strategy = "AlwaysIgnore" =>
     <>(phase = "idle")  \* Suite eventually completes
```

**Current Risk in Code**: The `AllowCount` strategy (`allow_count.py:14-16`) uses `>` comparison:
```python
if history.current_test_case.error_count > self.allow_count:
    raise error
```
This means `allow_count=3` allows exactly 3 errors and raises on the 4th. TLA+ could verify this matches the intended semantics across all orderings of errors and steps.

### 3.3 Algorithm Fairness Properties (HIGH VALUE)

**Problem**: The `BalancingAlgorithm` claims to balance step execution, and `WeightedBalancingAlgorithm` combines weights with history-based balancing.

**Properties to Verify**:

```tla
\* Liveness/Fairness: Every available step is eventually executed
StepFairness ==
  \A s \in AvailableSteps:
    <>(step_count[s] > 0)  \* Every step is eventually taken

\* Safety: BalancingAlgorithm always selects minimum-count step
BalancingCorrect ==
  /\ chosen_step = ArgMin(available_steps, step_count)

\* Safety: Weights are always positive when passed to random.choices
WeightsPositive ==
  /\ \A w \in computed_weights: w > 0

\* Liveness: Under WeightedBalancing, all steps get "fair" share
WeightedFairness ==
  /\ \A s \in Steps:
     <>(step_count[s] / total_steps >= weight[s] / total_weight - epsilon)
```

**Current Risk in Code**: The `WeightedBalancingAlgorithm` (`weighted.py:39-56`) has complex weight normalization:
```python
total_weights = [a - b if a - b != 0 else 0.1 for (a, b) in zip(norm_weights, hist_norm)]
if sum(total_weights) < 0:
    temp_add = (abs(sum(total_weights)) + 0.2) / len(total_weights)
    total_weights = [temp_add + x for x in total_weights]
```
This "rescue negative totals" logic could produce pathological weight distributions. TLA+ could enumerate all possible weight/history combinations to verify weights remain sensible.

### 3.4 End Condition Composition (MEDIUM VALUE)

**Problem**: `And` and `Or` end conditions compose multiple conditions. Their interaction with test vs. suite semantics needs verification.

**Properties to Verify**:
```tla
\* And(Length(5), StepCoverage(100)) terminates iff BOTH are met
AndCorrect ==
  /\ And_terminates <=> (cond1_met /\ cond2_met)

\* Or(Length(5), Time(10s)) terminates when EITHER is met
OrCorrect ==
  /\ Or_terminates <=> (cond1_met \/ cond2_met)

\* Safety: End conditions can never cause infinite loops
\* (except Endless, which is intentional)
NoUnintendedInfiniteLoop ==
  /\ end_condition /= Endless =>
     <>(phase = "idle")
```

**Current Risk in Code**: If `StepCoverage` is used as a suite end condition, it checks `current_test_case` coverage (not cumulative)—meaning a suite could run forever if individual tests never reach the coverage threshold but the test end condition stops them first.

### 3.5 History State Consistency (MEDIUM VALUE)

**Properties to Verify**:
```tla
\* Invariant: At most one test case is "running" at any time
SingleActiveTest ==
  /\ Cardinality({t \in test_cases : t.is_running}) <= 1

\* Invariant: Steps can only be added to running test cases
StepAdditionValid ==
  /\ add_step_called => current_test_case.is_running

\* Monotonicity: Step counts never decrease
MonotonicSteps ==
  /\ total_steps' >= total_steps
  /\ error_count' >= error_count
```

### 3.6 Step Discovery and Guard Resolution (LOW VALUE)

The priority-based guard resolution (`model.py:80-105`) follows a fixed priority:
1. `_osmo_enabled` attribute
2. Inline `_osmo_guard_inline`
3. Decorator `@guard("name")`
4. Naming convention `guard_name()`

**Property**: No two mechanisms can conflict (the first match wins). This is simple enough that TLA+ verification adds limited value—a unit test suffices.

---

## 4. Proposed TLA+ Specifications

### 4.1 Engine State Machine Specification

```tla
---------------------------- MODULE PyOsmoEngine ----------------------------
EXTENDS Naturals, Sequences, FiniteSets

CONSTANTS Steps, MaxSteps, MaxTests, ErrorStrategies

VARIABLES
  phase,           \* "idle" | "suite" | "test" | "step"
  test_count,      \* Number of completed tests
  step_count,      \* Steps in current test
  total_steps,     \* Total steps across all tests
  error_count,     \* Errors in current test
  suite_errors,    \* Total errors across suite
  available,       \* Set of currently available steps
  chosen,          \* Last chosen step
  hook_trace,      \* Sequence of executed hooks
  test_strategy,   \* Current test error strategy
  suite_strategy   \* Current suite error strategy

TypeInvariant ==
  /\ phase \in {"idle", "suite", "test", "step"}
  /\ test_count \in Nat
  /\ step_count \in Nat
  /\ error_count \in Nat

Init ==
  /\ phase = "idle"
  /\ test_count = 0
  /\ step_count = 0
  /\ total_steps = 0
  /\ error_count = 0
  /\ suite_errors = 0
  /\ available = Steps
  /\ chosen = "none"
  /\ hook_trace = <<>>
  /\ test_strategy = "raise"
  /\ suite_strategy = "raise"

StartSuite ==
  /\ phase = "idle"
  /\ phase' = "suite"
  /\ hook_trace' = Append(hook_trace, "before_suite")
  /\ UNCHANGED <<test_count, step_count, total_steps,
                  error_count, suite_errors, available,
                  chosen, test_strategy, suite_strategy>>

StartTest ==
  /\ phase = "suite"
  /\ phase' = "test"
  /\ step_count' = 0
  /\ error_count' = 0
  /\ hook_trace' = Append(hook_trace, "before_test")
  /\ UNCHANGED <<test_count, total_steps, suite_errors,
                  available, chosen, test_strategy, suite_strategy>>

ChooseStep ==
  /\ phase = "test"
  /\ available /= {}
  /\ phase' = "step"
  /\ \E s \in available:
       chosen' = s
  /\ hook_trace' = Append(hook_trace, "before")
  /\ UNCHANGED <<test_count, step_count, total_steps,
                  error_count, suite_errors, available,
                  test_strategy, suite_strategy>>

CompleteStep ==
  /\ phase = "step"
  /\ phase' = "test"
  /\ step_count' = step_count + 1
  /\ total_steps' = total_steps + 1
  /\ hook_trace' = Append(hook_trace, "after")
  /\ UNCHANGED <<test_count, error_count, suite_errors,
                  available, chosen, test_strategy, suite_strategy>>

StepError ==
  /\ phase = "step"
  /\ error_count' = error_count + 1
  /\ suite_errors' = suite_errors + 1
  /\ IF test_strategy = "raise"
     THEN phase' = "suite"  \* Error propagates up
     ELSE phase' = "test"   \* Error swallowed, continue
  /\ step_count' = step_count + 1
  /\ total_steps' = total_steps + 1
  /\ UNCHANGED <<test_count, available, chosen,
                  hook_trace, test_strategy, suite_strategy>>

EndTest ==
  /\ phase = "test"
  /\ step_count >= MaxSteps  \* Simplified end condition
  /\ phase' = "suite"
  /\ test_count' = test_count + 1
  /\ hook_trace' = Append(hook_trace, "after_test")
  /\ UNCHANGED <<step_count, total_steps, error_count,
                  suite_errors, available, chosen,
                  test_strategy, suite_strategy>>

EndSuite ==
  /\ phase = "suite"
  /\ test_count >= MaxTests
  /\ phase' = "idle"
  /\ hook_trace' = Append(hook_trace, "after_suite")
  /\ UNCHANGED <<test_count, step_count, total_steps,
                  error_count, suite_errors, available,
                  chosen, test_strategy, suite_strategy>>

Next ==
  \/ StartSuite
  \/ StartTest
  \/ ChooseStep
  \/ CompleteStep
  \/ StepError
  \/ EndTest
  \/ EndSuite

\* --- PROPERTIES TO CHECK ---

\* Safety: Phase transitions are valid
ValidTransitions ==
  /\ (phase = "idle") => (phase' \in {"idle", "suite"})
  /\ (phase = "suite") => (phase' \in {"suite", "test", "idle"})
  /\ (phase = "test") => (phase' \in {"test", "step", "suite"})
  /\ (phase = "step") => (phase' \in {"test", "suite"})

\* Safety: Steps only increase
MonotonicSteps ==
  /\ total_steps' >= total_steps

\* Liveness: Suite eventually terminates
SuiteTerminates ==
  <>(phase = "idle" /\ test_count >= MaxTests)

\* Safety: Hook ordering
HookOrderingInvariant ==
  /\ Len(hook_trace) > 0 =>
     (Last(hook_trace) = "after_suite" => "before_suite" \in Range(hook_trace))

Spec == Init /\ [][Next]_<<phase, test_count, step_count, total_steps,
                           error_count, suite_errors, available,
                           chosen, hook_trace, test_strategy, suite_strategy>>
        /\ WF_<<phase>>(Next)

=============================================================================
```

### 4.2 Balancing Algorithm Specification

```tla
------------------------ MODULE BalancingAlgorithm --------------------------
EXTENDS Naturals, Sequences, FiniteSets

CONSTANTS Steps, MaxIterations

VARIABLES
  step_counts,    \* Function: Step -> Nat (execution counts)
  available,      \* Set of currently available steps
  chosen,         \* Last chosen step
  iteration       \* Current iteration count

TypeInvariant ==
  /\ \A s \in Steps: step_counts[s] \in Nat
  /\ available \subseteq Steps
  /\ iteration \in Nat

Init ==
  /\ step_counts = [s \in Steps |-> 0]
  /\ available = Steps
  /\ chosen = CHOOSE s \in Steps : TRUE
  /\ iteration = 0

\* Balancing: Choose the step with minimum count
Choose ==
  /\ iteration < MaxIterations
  /\ available /= {}
  /\ LET min_count == CHOOSE c \in {step_counts[s] : s \in available} :
                        \A c2 \in {step_counts[s] : s \in available} : c <= c2
     IN \E s \in available:
          /\ step_counts[s] = min_count
          /\ chosen' = s
          /\ step_counts' = [step_counts EXCEPT ![s] = @ + 1]
  /\ iteration' = iteration + 1
  /\ UNCHANGED available

\* --- PROPERTIES ---

\* Safety: Chosen step always has minimum count (before increment)
BalancingCorrect ==
  /\ available /= {} =>
     \A s \in available:
       step_counts[chosen] - 1 <= step_counts[s]

\* Liveness: All steps eventually get executed
AllStepsExecuted ==
  \A s \in Steps:
    <>(step_counts[s] > 0)

\* Safety: Counts are balanced (max - min <= 1)
BalancedCounts ==
  /\ iteration > Cardinality(Steps) =>
     LET max_c == CHOOSE c \in {step_counts[s] : s \in Steps} :
                    \A c2 \in {step_counts[s] : s \in Steps} : c >= c2
         min_c == CHOOSE c \in {step_counts[s] : s \in Steps} :
                    \A c2 \in {step_counts[s] : s \in Steps} : c <= c2
     IN max_c - min_c <= 1

Spec == Init /\ [][Choose]_<<step_counts, available, chosen, iteration>>
        /\ WF_<<step_counts>>(Choose)

=============================================================================
```

---

## 5. What TLA+ Would Likely Reveal

Based on the code analysis, TLA+ model checking would likely surface these issues:

### 5.1 Confirmed Bugs (Already Found During Investigation)

| # | Issue | Location | Severity |
|---|-------|----------|----------|
| 1 | `StepCoverage` range check inverted | `step_coverage.py:12` | Critical |
| 2 | `StepCoverage.end_suite()` uses per-test coverage, not cumulative | `step_coverage.py:25-32` | Major |
| 3 | `OsmoTestCaseRecord.is_running()` returns True when stopped | `test_case.py:19-20` | Moderate |

### 5.2 Properties TLA+ Would Verify/Refute

| Property | Expected Result | Value |
|----------|----------------|-------|
| Hook ordering never violated | PASS (but worth proving) | High |
| AlwaysRaise never silently drops errors | PASS | High |
| AllowCount(n) raises on exactly the (n+1)th error | PASS (current `>` is correct) | Medium |
| BalancingAlgorithm achieves max-min <= 1 | PASS (when all steps always available) | High |
| BalancingAlgorithm fair with changing availability | NEEDS VERIFICATION (may fail) | High |
| WeightedBalancing weights always positive | NEEDS VERIFICATION (rescue logic) | High |
| Suite terminates under all non-Endless conditions | PASS (assuming finite steps) | Medium |
| StepCoverage + Length composition works correctly | LIKELY FAIL (due to bug #2) | High |

### 5.3 Subtle Issues TLA+ Could Expose

1. **Error in `after_test` hook**: If `after_test` raises, it's caught by the suite-level handler. This means `after_test` may execute partially. TLA+ could verify whether this leads to inconsistent model state.

2. **Algorithm with empty available steps**: If all guards return False simultaneously, `algorithm.choose()` receives an empty list. Current code doesn't handle this—`random.choice([])` raises `IndexError`. TLA+ with the invariant `available /= {} => choose succeeds` would catch this.

3. **WeightedBalancingAlgorithm negative weights**: The normalization `a - b` can produce negative values. The rescue adds `(abs(sum) + 0.2) / len` to each weight, but if a single weight is very negative while others are positive, the result could still have a negative individual weight after rescue. TLA+ could enumerate all cases.

4. **Seed determinism across runs**: Setting the same seed should produce identical test sequences. TLA+ can't verify this directly (it's about implementation, not logic), but it could verify that the algorithm's *decision function* is deterministic given the same inputs.

---

## 6. The Meta-Level: TLA+ and MBT Relationship

### 6.1 PyOsmo IS an MBT Tool; TLA+ CAN DO MBT

There's a fascinating recursive relationship:

- **PyOsmo** generates tests from *Python models* (classes with steps/guards)
- **TLA+** can generate tests from *TLA+ specifications* (formal state machines)

Both approaches share the same goal: systematically exploring a system's state space to find bugs. The difference is in formality and exhaustiveness:

| Aspect | PyOsmo (MBT) | TLA+ (Formal) |
|--------|--------------|----------------|
| Model language | Python | TLA+ math notation |
| Exploration | Random/weighted sampling | Exhaustive BFS |
| Guarantees | Probabilistic coverage | Mathematical proof |
| Bug finding | Heuristic | Complete (for finite models) |
| Learning curve | Low (Python developers) | High (formal methods) |
| Runtime | Fast (random sampling) | Slow (exponential state space) |

### 6.2 Complementary Usage

Rather than TLA+ *replacing* PyOsmo, they serve complementary roles:

1. **TLA+ verifies PyOsmo's engine** (this document's main topic)
2. **TLA+ specifications could inform PyOsmo models**: A TLA+ spec could be "compiled down" to a PyOsmo model for runtime testing
3. **PyOsmo tests what TLA+ proves**: TLA+ proves algorithmic correctness; PyOsmo tests the actual implementation against real systems

### 6.3 Prior Art: Model-Based Testing with TLA+ and Apalache

Research by Kuprianov and Konnov demonstrates using TLA+ specifications directly for integration test generation. In their Tendermint case study, 6 lines of TLA+ generated 500+ lines of integration tests. This approach "plays the role of the missing link between specifications and implementation."

MongoDB's "eXtreme Modelling" approach uses TLA+ for both verification and conformance testing—verifying that implementations match their formal specifications through trace checking.

---

## 7. Practical Recommendations

### 7.1 High-Priority TLA+ Specifications to Write

| Specification | Effort | Value | Rationale |
|---------------|--------|-------|-----------|
| Engine state machine (Section 4.1) | Medium | High | Verifies core execution correctness |
| Error cascade behavior | Low | High | Simple model, critical correctness |
| Balancing algorithm fairness | Low | High | Mathematical property, small state space |
| End condition composition | Low | Medium | Verifies And/Or/coverage interactions |

### 7.2 What NOT to Specify in TLA+

- **Model discovery logic** (parsing decorators/naming conventions): This is pure sequential code without state machine complexity. Unit tests suffice.
- **History data structures**: Simple append-only collections. No complex invariants beyond what Python's type system guarantees.
- **CLI/configuration**: No concurrency or state machine behavior.

### 7.3 Implementation Approach

1. **Start with the engine state machine** (Section 4.1): This is the highest-value specification. Model the phase transitions, hook ordering, and error handling cascade. Run TLC to verify safety and liveness properties.

2. **Add algorithm specifications**: Model each algorithm (especially `WeightedBalancingAlgorithm`) and verify fairness properties under various step availability patterns.

3. **Verify end condition composition**: Small TLA+ model verifying `And`/`Or` behavior with various condition combinations.

4. **Integrate with CI (optional)**: TLC can run as a CI check. Specifications serve as executable documentation of intended behavior.

### 7.4 Estimated Complexity

- **Engine state machine TLA+ spec**: ~150-200 lines of TLA+
- **Algorithm specs**: ~50-80 lines each
- **End condition spec**: ~60-80 lines
- **Learning curve**: Significant if team has no TLA+ experience (the main barrier to adoption)

### 7.5 Alternative: Property-Based Testing with Hypothesis

For teams that find TLA+ too heavyweight, Python's `hypothesis` library (already available in the project) can verify many of the same properties through randomized testing:

```python
from hypothesis import given, strategies as st

@given(st.lists(st.sampled_from(["step_a", "step_b", "step_c"]), min_size=1))
def test_balancing_fairness(steps):
    """After N*len(steps) iterations, all counts within 1 of each other."""
    ...
```

This provides probabilistic guarantees rather than TLA+'s mathematical proofs, but with much lower adoption cost.

---

## 8. Conclusion

TLA+ is a strong fit for verifying PyOsmo's core engine correctness. The main value propositions are:

1. **Proving hook ordering invariants** across all error paths (including error-in-hook scenarios)
2. **Verifying error strategy cascade** correctness for all strategy combinations
3. **Proving algorithm fairness** properties mathematically
4. **Catching edge cases** in end condition composition (especially the existing StepCoverage bugs)

The main barrier is the learning curve. For a small team, the alternative of enhanced property-based testing with Hypothesis may provide 80% of the value at 20% of the adoption cost. However, for the core state machine (the engine loop), TLA+ provides guarantees that no amount of testing can match.

The meta-level relationship between TLA+ and PyOsmo is also worth noting: both are tools for systematic state space exploration, operating at different levels of formality. A future integration where TLA+ specifications could be translated into PyOsmo models would be a powerful combination of formal verification and practical runtime testing.

---

## References

- [TLA+ Wikipedia](https://en.wikipedia.org/wiki/TLA+)
- [A Primer on Formal Verification and TLA+](https://jack-vanlightly.com/blog/2023/10/10/a-primer-on-formal-verification-and-tla) — Jack Vanlightly
- [Safety and Liveness Properties](https://www.hillelwayne.com/post/safety-and-liveness/) — Hillel Wayne
- [Use of Formal Methods at Amazon Web Services](https://lamport.azurewebsites.net/tla/formal-methods-amazon.pdf) — Newcombe et al.
- [Model-Based Testing with TLA+ and Apalache](http://conf.tlapl.us/2020/09-Kuprianov_and_Konnov-Model-based_testing_with_TLA_+_and_Apalache.pdf) — Kuprianov & Konnov
- [Fully-Tested Code Generation from TLA+ Specifications](https://dl.acm.org/doi/fullHtml/10.1145/3559744.3559747)
- [eXtreme Modelling in Practice (MongoDB)](https://arxiv.org/abs/2006.00915) — Davis et al.
- [Formal Verification of Concurrent Scheduling Strategies using TLA](https://www.researchgate.net/publication/4319663_Formal_verification_of_concurrent_scheduling_strategies_using_TLA)
- [Learn TLA+](https://learntla.com/)
- [Temporal Properties in TLA+](https://learntla.com/core/temporal-logic.html)
- [Safety, Liveness, and Fairness](https://lamport.azurewebsites.net/tla/safety-liveness.pdf) — Leslie Lamport
- [The Coming Need for Formal Specification (Dec 2025)](https://benjamincongdon.me/blog/2025/12/12/The-Coming-Need-for-Formal-Specification/) — Ben Congdon
