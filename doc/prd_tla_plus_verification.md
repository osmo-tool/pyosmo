# PRD: Formal Verification of PyOsmo Engine with TLA+

| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Author** | PyOsmo Team |
| **Created** | 2026-01-24 |
| **Last Updated** | 2026-01-24 |
| **Priority** | Medium |
| **Category** | Quality / Reliability |

---

## 1. Problem Statement

PyOsmo's test generation engine is a state machine with nested execution loops, two-level error handling, pluggable algorithms, and composable end conditions. The correctness of this engine is critical because:

- **Users trust PyOsmo to generate valid test sequences.** If the engine has subtle state management bugs, generated tests may not faithfully represent the model, leading to false confidence in the system under test.
- **Error handling is complex and multi-layered.** The two-level strategy cascade (test-level + suite-level) has subtle interactions that are difficult to verify through unit testing alone.
- **Algorithm fairness claims are unproven.** The balancing algorithms claim to distribute step execution fairly, but no formal proof exists that they achieve this under all step availability patterns.
- **Existing bugs have been found in end conditions** during code review (inverted range checks, per-test vs. cumulative coverage semantics), suggesting more may exist in unexplored paths.

Traditional testing cannot exhaustively verify these properties because the combinatorial explosion of states (error timing, guard availability changes, strategy combinations) makes complete coverage impractical.

---

## 2. Goals

### Primary Goals

1. **Prove engine execution correctness**: Formally verify that lifecycle hooks execute in the guaranteed order under all error paths
2. **Verify error strategy behavior**: Prove that no error is silently dropped when `AlwaysRaise` is configured, and that `AllowCount(n)` has correct threshold semantics
3. **Prove algorithm fairness**: Mathematically verify that `BalancingAlgorithm` achieves `max_count - min_count <= 1` for all step availability patterns
4. **Validate end condition composition**: Verify that `And`/`Or` combinators behave correctly and that no non-`Endless` configuration causes infinite execution

### Secondary Goals

5. **Document engine invariants**: The TLA+ specifications serve as executable, machine-checkable documentation of intended behavior
6. **Establish formal methods practice**: Build team capability in formal verification for future use
7. **Identify and fix existing bugs**: Surface edge-case bugs that code review and testing have missed

### Non-Goals

- Formal verification of the entire codebase (model discovery, CLI, history data structures)
- Replacing existing pytest-based test suite
- Verifying Python implementation correctness (TLA+ verifies the *design*, not the code)
- Performance optimization

---

## 3. Background

### 3.1 What is TLA+

TLA+ (Temporal Logic of Actions) is a formal specification language created by Leslie Lamport. It models systems as state machines and uses the TLC model checker to exhaustively explore all reachable states, verifying:

- **Safety properties** (invariants): Conditions that must hold in every reachable state ("bad things never happen")
- **Liveness properties**: Conditions that must eventually become true ("good things eventually happen")
- **Fairness**: Guarantees that enabled actions are eventually taken
- **Action properties**: Constraints on state transitions

### 3.2 Industry Precedent

- **Amazon Web Services**: Seven teams use TLA+ for critical distributed systems. TLC found a data-loss bug requiring 35 high-level steps to reproduce—impossible to find through testing.
- **MongoDB**: Uses TLA+ for replication protocol verification and conformance testing (trace checking).
- **Tendermint/Cosmos**: Model-based testing with TLA+ and Apalache generated 500+ lines of integration tests from 6 lines of specification.

### 3.3 PyOsmo Engine Architecture

The engine (`pyosmo/osmo.py`) implements a nested state machine:

```
IDLE → SUITE_RUNNING → TEST_RUNNING → STEP_EXECUTING → TEST_RUNNING → ...
```

With lifecycle hooks at each transition:
```
before_suite → (before_test → (before → pre_X → step → post_X → after)* → after_test)* → after_suite
```

Key complexity comes from:
- Error strategies that may swallow or propagate exceptions at two levels
- End conditions evaluated at different loop points
- Guards that dynamically change step availability between iterations
- Algorithm state that depends on execution history

---

## 4. Requirements

### 4.1 Functional Requirements

#### FR-1: Engine State Machine Specification
**Priority: P0**

Write a TLA+ specification that models the PyOsmo execution engine with the following state variables:
- Execution phase (`idle`, `suite`, `test`, `step`)
- Test and step counters
- Error counters (per-test and per-suite)
- Hook execution trace
- Error strategy configuration

The specification must model:
- All valid phase transitions
- Lifecycle hook execution at each transition
- Error occurrence and propagation through two-level strategy
- End condition evaluation and loop termination

#### FR-2: Safety Properties
**Priority: P0**

Define and verify these invariants:
- **Phase transition validity**: Only legal transitions occur (e.g., `step` can only transition to `test` or `suite`, never to `idle`)
- **Hook ordering**: `after_*` hooks are never called without corresponding `before_*` hooks having executed
- **Monotonic counters**: `total_steps` and `error_count` never decrease
- **Single active test**: At most one test case is in "running" state at any time
- **Steps added to active test only**: `add_step()` is never called when no test case is running

#### FR-3: Liveness Properties
**Priority: P1**

Define and verify these temporal properties:
- **Suite termination**: For any non-`Endless` end condition, the suite eventually reaches `idle` state
- **Step fairness**: Under `BalancingAlgorithm` with all steps always available, every step is eventually executed
- **Error propagation**: Under `AlwaysRaise`, every error eventually causes an exception to propagate

#### FR-4: Error Strategy Cascade Specification
**Priority: P0**

Model all four error strategies and verify:
- `AlwaysRaise`: No error is ever silently dropped
- `AlwaysIgnore`: Suite always terminates normally regardless of errors
- `IgnoreAsserts`: Only `AssertionError` is swallowed; all other errors propagate
- `AllowCount(n)`: Exactly `n` errors are tolerated; the `(n+1)`th error propagates

Verify behavior for all combinations of test-level and suite-level strategies (4x4 = 16 combinations).

#### FR-5: Algorithm Fairness Specification
**Priority: P1**

Model each step-selection algorithm and verify:

**BalancingAlgorithm:**
- After `k * |Steps|` iterations (k >= 1), `max_count - min_count <= 1` for all available steps
- Every continuously-available step is eventually selected

**WeightedBalancingAlgorithm:**
- Computed weights are always positive (never negative or zero)
- The "rescue negative totals" normalization produces valid probability distributions
- With equal weights, behavior converges to `BalancingAlgorithm` properties

**RandomAlgorithm / WeightedAlgorithm:**
- `choices` list is never empty when `choose()` is called (guard against `IndexError`)

#### FR-6: End Condition Composition Specification
**Priority: P2**

Model composable end conditions and verify:
- `And(c1, c2)` terminates iff both `c1` and `c2` are satisfied
- `Or(c1, c2)` terminates iff either `c1` or `c2` is satisfied
- `Length(n)` terminates after exactly `n` steps/tests
- `StepCoverage(p)` terminates when coverage percentage is reached
- No non-`Endless` composition can produce infinite execution (with finite step space)

### 4.2 Non-Functional Requirements

#### NFR-1: Specification Readability
Specifications must include comments explaining the correspondence between TLA+ variables/actions and Python code locations (file:line references).

#### NFR-2: Model Checking Performance
TLC model checking must complete within 10 minutes on a standard development machine for the primary engine specification with small constants (MaxSteps=5, MaxTests=3, |Steps|=4).

#### NFR-3: CI Integration (Optional)
TLC checks should be runnable as a CI step. Failures produce counterexample traces that map back to engine code.

#### NFR-4: Documentation Value
Each specification file serves as executable documentation of the intended behavior. Non-TLA+ developers should be able to read the invariant definitions and understand what properties are guaranteed.

---

## 5. User Stories

### US-1: Engine Developer
> As a PyOsmo engine developer, I want mathematical proof that my lifecycle hook ordering is never violated under any error path, so that users can rely on cleanup hooks (`after_test`, `after_suite`) always executing.

### US-2: Algorithm Author
> As a developer adding a new step-selection algorithm, I want a TLA+ specification template that defines required fairness properties, so that I can verify my algorithm meets the same guarantees as existing ones.

### US-3: Bug Reporter
> As a user who encountered unexpected behavior with `AllowCount(3)` + `AlwaysIgnore` strategy combination, I want the framework maintainers to have formally verified all 16 strategy combinations, so that edge cases are caught before release.

### US-4: PyOsmo User
> As a PyOsmo user, I want confidence that when I configure `StepCoverage(80)` with `And(Length(100))`, the suite will terminate and achieve the coverage I specified, not run forever due to a logic bug.

### US-5: New Contributor
> As a new contributor to PyOsmo, I want to read the TLA+ specifications to understand the engine's intended state machine behavior without having to reverse-engineer it from Python code.

---

## 6. Technical Design

### 6.1 Specification Structure

```
pyosmo/
  specs/
    tla/
      PyOsmoEngine.tla          # Core state machine (FR-1, FR-2, FR-3)
      ErrorStrategyCascade.tla   # Error handling (FR-4)
      BalancingAlgorithm.tla     # Balancing fairness (FR-5)
      WeightedBalancing.tla      # Weighted balancing (FR-5)
      EndConditions.tla          # Condition composition (FR-6)
      PyOsmoEngine.cfg           # TLC model config
      ErrorStrategyCascade.cfg
      BalancingAlgorithm.cfg
      WeightedBalancing.cfg
      EndConditions.cfg
```

### 6.2 Engine State Machine Model

**State Variables:**
```
phase ∈ {"idle", "suite", "test", "step"}
test_count ∈ Nat
step_count ∈ Nat  (current test)
total_steps ∈ Nat (all tests)
error_count ∈ Nat (current test)
suite_errors ∈ Nat (all tests)
available ⊆ Steps
hook_trace ∈ Seq(HookNames)
test_strategy ∈ {"raise", "ignore", "ignore_asserts", "allow_count"}
suite_strategy ∈ {"raise", "ignore", "ignore_asserts", "allow_count"}
```

**Actions:**
- `StartSuite`: idle → suite, execute before_suite
- `StartTest`: suite → test, reset per-test counters, execute before_test
- `ChooseStep`: test → step, algorithm selects from available
- `CompleteStep`: step → test, increment counters, execute after
- `StepError`: step → test|suite (depends on strategy), increment error counters
- `EndTest`: test → suite (when end condition met), execute after_test
- `EndSuite`: suite → idle (when suite condition met), execute after_suite
- `UpdateAvailability`: test → test, change guard results (models dynamic availability)

**Key Properties to Check:**
```
INVARIANT TypeInvariant
INVARIANT ValidPhaseTransitions
INVARIANT HookOrderingInvariant
INVARIANT MonotonicCounters
INVARIANT SingleActiveTestCase
PROPERTY SuiteEventuallyTerminates
PROPERTY AllStepsEventuallyExecuted (under Balancing)
```

### 6.3 Error Strategy Model

Models all 16 combinations of test × suite strategies. State tracks:
- Whether current error should propagate or be swallowed
- Running error count vs. allow threshold
- Whether suite continues or halts after test-level propagation

### 6.4 Algorithm Model

For `BalancingAlgorithm`: deterministic selection of minimum-count step with tie-breaking. Verify `max - min <= 1` after sufficient iterations.

For `WeightedBalancingAlgorithm`: models weight normalization arithmetic. Uses finite precision (integers scaled by 100) to approximate floating-point behavior. Verifies all intermediate weights remain positive.

### 6.5 Correspondence to Implementation

| TLA+ Action | Python Code |
|-------------|-------------|
| `StartSuite` | `osmo.py:97-103` (before_suite, algorithm init) |
| `StartTest` | `osmo.py:105-108` (start_new_test, before_test) |
| `ChooseStep` | `osmo.py:110-111` (before, algorithm.choose) |
| `CompleteStep` | `osmo.py:112-115` (_run_step success path) |
| `StepError` | `osmo.py:116-119` (_run_step error + strategy) |
| `EndTest` | `osmo.py:121-123` (end_test check, after_test) |
| `EndSuite` | `osmo.py:129-130` (end_suite check, after_suite) |

---

## 7. Discovered Issues

The investigation surfaced these existing bugs that TLA+ verification would formally confirm:

| # | Issue | Location | Severity | Status |
|---|-------|----------|----------|--------|
| 1 | `StepCoverage` range validation inverted: `if coverage_percent in range(1, 100)` should be `not in range(1, 101)` | `step_coverage.py:12` | Critical | Open |
| 2 | `StepCoverage.end_suite()` checks current test coverage, not cumulative across all tests | `step_coverage.py:25-32` | Major | Open |
| 3 | `OsmoTestCaseRecord.is_running()` returns True when stopped (inverted logic) | `test_case.py:19-20` | Moderate | Open |
| 4 | Empty `available_steps` causes `IndexError` in all algorithms (no guard against all-guards-False) | `osmo.py:110` | Major | Open |
| 5 | `WeightedBalancingAlgorithm` rescue logic may produce negative individual weights | `weighted.py:50-53` | Moderate | Open |
| 6 | `TestStepLog.name` uses `function_name` not semantic step name, causing history mismatches for decorator-based steps | `test_step_log.py:22-23` | Minor | Open |

---

## 8. Success Criteria

### 8.1 Verification Milestones

| Milestone | Criteria | Priority |
|-----------|----------|----------|
| M1: Engine spec passes TLC | All safety invariants hold for MaxSteps=5, MaxTests=3, Steps=4 | P0 |
| M2: Error strategies verified | All 16 strategy combinations verified for correct propagation behavior | P0 |
| M3: Balancing fairness proven | `BalancedCounts` invariant holds for Steps=5, MaxIterations=25 | P1 |
| M4: End conditions verified | And/Or composition correct; no infinite loops for finite configurations | P2 |
| M5: CI integration | TLC runs on PR checks, blocks merge on invariant violations | P3 |

### 8.2 Acceptance Criteria

- [ ] All P0 invariants pass TLC model checking with zero violations
- [ ] Each TLA+ specification has comments mapping actions to Python source locations
- [ ] Counterexample traces (if any found) are documented with corresponding Python reproduction steps
- [ ] Discovered bugs (Section 7) are fixed and covered by both TLA+ invariants and pytest regression tests
- [ ] Specifications are reviewed by at least one team member not involved in writing them

---

## 9. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Learning curve**: Team has no TLA+ experience | High | High | Start with simplest spec (error cascade). Use Learn TLA+ resources. Consider pairing with formal methods consultant for first spec. |
| **Specification drift**: TLA+ specs diverge from Python implementation over time | Medium | High | Add CI check that runs TLC. Include spec update in PR checklist for engine changes. |
| **State space explosion**: TLC runs too long with realistic constants | Medium | Medium | Use small constants for verification (MaxSteps=5). Rely on symmetry reduction. Parameterize specs. |
| **False confidence**: Team assumes TLA+ verification means implementation is correct | Low | High | Document clearly: TLA+ verifies the *design*, not the Python code. Maintain pytest suite for implementation testing. |
| **Over-specification**: Specs become too detailed, matching implementation rather than design intent | Medium | Low | Focus on *properties* (what should hold), not *how* (implementation details). Review specs for unnecessary specificity. |

---

## 10. Alternatives Considered

### 10.1 Property-Based Testing with Hypothesis (Recommended as Phase 0)

Python's `hypothesis` library can verify many of the same properties through randomized testing:

```python
@given(strategies=st.sampled_from(["raise", "ignore", "allow_count"]),
       error_positions=st.lists(st.booleans()))
def test_error_cascade_never_drops_errors(strategies, error_positions):
    ...
```

**Pros**: No new language to learn; integrates with existing pytest; fast iteration
**Cons**: Probabilistic (not exhaustive); may miss edge cases; no liveness proofs

**Recommendation**: Implement Hypothesis property tests as Phase 0 (immediate value), then pursue TLA+ for mathematically rigorous verification of critical properties.

### 10.2 Alloy (Lightweight Formal Methods)

Alloy is a simpler formal specification language with automatic analysis.

**Pros**: Easier learning curve than TLA+; good for structural properties
**Cons**: Less suited for temporal/liveness properties; smaller community; less industry adoption

### 10.3 Python-based Model Checking (e.g., Strix, mCRL2)

Use Python bindings for model checking directly.

**Pros**: Same language as implementation; lower adoption barrier
**Cons**: Less mature tooling; TLA+ has stronger community and industry validation

### 10.4 Do Nothing (Status Quo)

Rely on existing pytest suite and code review.

**Pros**: No investment needed
**Cons**: Leaves subtle state machine bugs undetected; no formal guarantees about algorithm fairness or hook ordering

---

## 11. Implementation Phases

### Phase 0: Hypothesis Property Tests (Prerequisite)

Add property-based tests covering the same properties targeted by TLA+ specs. This provides immediate value and serves as a validation baseline for the TLA+ work.

Scope:
- Hook ordering property test
- Error strategy combination test (all 16 pairs)
- Balancing algorithm fairness test
- End condition composition test
- Empty available_steps edge case test

### Phase 1: Core Engine Specification (P0)

Scope:
- `PyOsmoEngine.tla` with phase transitions, hook ordering, error cascade
- TLC configuration with small constants
- Verify all safety invariants
- Document any counterexamples found

### Phase 2: Algorithm Specifications (P1)

Scope:
- `BalancingAlgorithm.tla` with fairness proof
- `WeightedBalancing.tla` with weight positivity proof
- Verify with varying step availability patterns

### Phase 3: End Condition Specification (P2)

Scope:
- `EndConditions.tla` with And/Or composition
- Verify termination for all non-Endless configurations
- Model StepCoverage with test vs. suite semantics

### Phase 4: CI Integration (P3)

Scope:
- Add TLC to GitHub Actions workflow
- Run on PR checks (blocking)
- Report counterexample traces in PR comments

---

## 12. Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| TLA+ Toolbox / VS Code extension | Tool | Free, open source |
| TLC model checker | Tool | Included with TLA+ toolbox |
| Java runtime (for TLC) | Runtime | TLC requires JVM |
| Team TLA+ training | Knowledge | 1-2 weeks ramp-up for basics |
| Bug fixes from Section 7 | Code | Fix before spec matches intent, or spec against intended behavior |

---

## 13. Relationship Between TLA+ and PyOsmo (Meta-Level)

### 13.1 Conceptual Overlap

Both TLA+ and PyOsmo are tools for systematic state space exploration:

| Aspect | PyOsmo (MBT) | TLA+ (Formal Verification) |
|--------|--------------|----------------------------|
| **Model language** | Python classes | TLA+ mathematical notation |
| **Exploration** | Random/weighted sampling | Exhaustive breadth-first search |
| **Guarantees** | Probabilistic coverage | Mathematical proof |
| **Bug finding** | Heuristic (may miss) | Complete (for finite models) |
| **Learning curve** | Low (Python developers) | High (formal methods expertise) |
| **Runtime** | Fast (random sampling) | Slow (exponential state space) |
| **Target** | System under test | System design/algorithm |

### 13.2 Complementary Roles

1. **TLA+ verifies PyOsmo's engine** — proves the test generator itself is correct
2. **PyOsmo tests implementations** — runs generated tests against real systems
3. **TLA+ specs could become PyOsmo models** — future integration where formal specs compile to runtime test models

### 13.3 Future Opportunity: TLA+ to PyOsmo Model Compiler

A potential future project: translating TLA+ specifications into PyOsmo models automatically. This would combine:
- TLA+'s rigorous design verification (prove the design is correct)
- PyOsmo's runtime testing (verify the implementation matches the design)

Prior art: Kuprianov & Konnov's work with TLA+ and Apalache generated integration tests from TLA+ specs for Tendermint. MongoDB's "eXtreme Modelling" uses trace checking for conformance.

---

## 14. References

- [TLA+ Wikipedia](https://en.wikipedia.org/wiki/TLA+)
- [A Primer on Formal Verification and TLA+](https://jack-vanlightly.com/blog/2023/10/10/a-primer-on-formal-verification-and-tla) — Jack Vanlightly
- [Safety and Liveness Properties](https://www.hillelwayne.com/post/safety-and-liveness/) — Hillel Wayne
- [Use of Formal Methods at Amazon Web Services](https://lamport.azurewebsites.net/tla/formal-methods-amazon.pdf) — Newcombe et al.
- [Model-Based Testing with TLA+ and Apalache](http://conf.tlapl.us/2020/09-Kuprianov_and_Konnov-Model-based_testing_with_TLA_+_and_Apalache.pdf) — Kuprianov & Konnov
- [Fully-Tested Code Generation from TLA+ Specifications](https://dl.acm.org/doi/fullHtml/10.1145/3559744.3559747)
- [eXtreme Modelling in Practice (MongoDB)](https://arxiv.org/abs/2006.00915) — Davis et al.
- [Formal Verification of Concurrent Scheduling Strategies using TLA](https://www.researchgate.net/publication/4319663_Formal_verification_of_concurrent_scheduling_strategies_using_TLA)
- [Learn TLA+](https://learntla.com/)
- [Safety, Liveness, and Fairness](https://lamport.azurewebsites.net/tla/safety-liveness.pdf) — Leslie Lamport
- [The Coming Need for Formal Specification (Dec 2025)](https://benjamincongdon.me/blog/2025/12/12/The-Coming-Need-for-Formal-Specification/) — Ben Congdon
