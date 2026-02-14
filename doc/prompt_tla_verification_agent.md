# Agent Prompt: Implement TLA+ Formal Verification for PyOsmo

## Context

You are working on the PyOsmo project (`/Users/oopee/git/pyosmo`), a Model-Based Testing framework for Python. Your task is to implement formal verification of the PyOsmo engine using TLA+ specifications, following the PRD at `doc/prd_tla_plus_verification.md` and the technical investigation at `doc/tla_plus_investigation.md`.

## Your Mission

Implement the TLA+ formal verification work in phases. Complete each phase fully before moving to the next. After each phase, run verification to confirm correctness before proceeding.

---

## Phase 0: Fix Discovered Bugs

Before writing specifications, fix the bugs discovered during investigation. These are documented in Section 7 of the PRD.

1. **Fix `StepCoverage` range validation** (`pyosmo/end_conditions/step_coverage.py:12`):
   - Current: `if coverage_percent in range(1, 100)` raises exception (inverted logic)
   - Fix: Should reject values NOT in valid range. Valid range is 1-100 inclusive.

2. **Fix `StepCoverage.end_suite()`** (`pyosmo/end_conditions/step_coverage.py:25-32`):
   - Current: Checks `current_test_case` coverage (per-test)
   - Fix: Should check cumulative coverage across ALL test cases in the suite

3. **Fix `OsmoTestCaseRecord.is_running()`** (`pyosmo/history/test_case.py:19-20`):
   - Current: Returns True when stopped (inverted)
   - Fix: Rename to `is_stopped()` or invert the logic. Check all callers.

4. **Fix empty `available_steps` crash** (`pyosmo/osmo.py`):
   - Current: If all guards return False, `algorithm.choose()` gets empty list → `IndexError`
   - Fix: Check for empty available steps before calling algorithm. Raise a clear `OsmoError` explaining no steps are available.

5. **Fix `TestStepLog.name`** (`pyosmo/history/test_step_log.py:22-23`):
   - Current: Uses `_step.function_name` instead of `_step.name`
   - Fix: Use `_step.name` for semantic step name in history/statistics

After each fix:
- Run `pytest pyosmo/tests/` to verify no regressions
- Run `ruff check pyosmo/ --fix && ruff format pyosmo/`
- Add a regression test if one doesn't exist for the fixed behavior

---

## Phase 1: Hypothesis Property Tests

Before writing TLA+ specs, implement property-based tests using Hypothesis that verify the same properties. These serve as immediate value and validation baseline.

Create file: `pyosmo/tests/test_properties.py`

Implement these property tests:

### 1.1 Hook Ordering Property
```python
# Test that lifecycle hooks always execute in correct order regardless of:
# - Number of steps per test
# - Number of tests per suite
# - Which steps are available
# - Whether errors occur
# Capture hook calls via a tracking model, verify ordering invariant holds.
```

### 1.2 Error Strategy Combinations (all 16 pairs)
```python
# For each combination of test_strategy × suite_strategy:
#   ("raise", "ignore", "ignore_asserts", "allow_count") × same
# Run with models that produce errors at random positions.
# Verify:
#   - AlwaysRaise at test level: error always propagates to suite level
#   - AlwaysIgnore: suite always completes normally
#   - AllowCount(n): exactly n errors tolerated, (n+1)th propagates
```

### 1.3 Balancing Algorithm Fairness
```python
# Given N steps all always available, after k*N iterations:
#   - max_count - min_count <= 1
# Given steps with changing availability:
#   - No available step is starved (count stays within bounds)
```

### 1.4 End Condition Composition
```python
# And(Length(a), Length(b)) terminates after max(a, b) steps
# Or(Length(a), Length(b)) terminates after min(a, b) steps
# StepCoverage works correctly at both test and suite level
```

### 1.5 Empty Available Steps
```python
# When all guards return False, engine raises clear error
# When guards alternate (some steps available, then none), behavior is correct
```

After implementing:
- Run `pytest pyosmo/tests/test_properties.py -v`
- All tests must pass
- Run `ruff check pyosmo/ --fix && ruff format pyosmo/`

---

## Phase 2: TLA+ Engine State Machine Specification

Create directory: `pyosmo/specs/tla/`

### 2.1 Write `PyOsmoEngine.tla`

Model the core execution engine state machine. Reference the specification sketch in Section 4.1 of `doc/tla_plus_investigation.md` but expand it to include:

- All phase transitions (idle, suite, test, step)
- Lifecycle hook execution tracking
- Two-level error handling with configurable strategies
- End condition evaluation
- Dynamic step availability (guards changing between iterations)
- History state (test count, step count, error count)

The specification should be approximately 150-250 lines.

### 2.2 Write `PyOsmoEngine.cfg`

TLC configuration with small constants:
```
CONSTANTS
  Steps = {s1, s2, s3, s4}
  MaxSteps = 5
  MaxTests = 3
  ErrorStrategies = {"raise", "ignore", "allow_count"}

INVARIANT TypeInvariant
INVARIANT ValidPhaseTransitions
INVARIANT HookOrderingInvariant
INVARIANT MonotonicCounters
INVARIANT SingleActiveTestCase

PROPERTY SuiteTerminates
```

### 2.3 Write `ErrorStrategyCascade.tla`

Focused specification for error strategy interactions:
- Model all 4 strategies at test level and suite level
- Track error occurrence, propagation, and swallowing
- Verify no silent error loss under AlwaysRaise
- Verify AllowCount threshold semantics

### 2.4 Write `ErrorStrategyCascade.cfg`

Configuration testing all 16 strategy combinations.

### 2.5 Verify with TLC

Run TLC on each specification:
```bash
java -jar tla2tools.jar -config PyOsmoEngine.cfg PyOsmoEngine.tla
java -jar tla2tools.jar -config ErrorStrategyCascade.cfg ErrorStrategyCascade.tla
```

If TLC is not available locally, document the expected verification results based on the specification analysis. Note any properties that cannot be verified without TLC and explain why.

---

## Phase 3: Algorithm Fairness Specifications

### 3.1 Write `BalancingAlgorithm.tla`

Model the deterministic balancing algorithm:
- State: step_counts function, available set, chosen step
- Action: Choose minimum-count step, increment its count
- Invariant: After |Steps| iterations, max - min <= 1
- Liveness: All available steps eventually executed

### 3.2 Write `WeightedBalancing.tla`

Model the weighted balancing algorithm:
- State: step_counts, weights (fixed), available set
- Action: Compute normalized weights, subtract history norm, rescue negatives, choose
- Invariant: All computed weights > 0 after normalization
- Safety: No division by zero in normalization

Use integer arithmetic scaled by 100 to model the floating-point behavior.

### 3.3 Write configurations and verify

---

## Phase 4: End Condition Specifications

### 4.1 Write `EndConditions.tla`

Model composable end conditions:
- Length, StepCoverage, Time (abstracted), Endless
- And/Or combinators
- Test-level vs suite-level semantics
- Verify termination properties

### 4.2 Verify no infinite loops

For all non-Endless configurations with finite step sets, prove suite eventually terminates.

---

## Phase 5: Documentation and Integration

### 5.1 Add README for specs
Create `pyosmo/specs/tla/README.md` explaining:
- What each spec verifies
- How to run TLC
- How to interpret counterexamples
- Correspondence between TLA+ and Python code

### 5.2 Update CLAUDE.md
Add a section about the TLA+ specifications to the project's CLAUDE.md.

### 5.3 Final verification
- Run full test suite: `pytest pyosmo/tests/`
- Run linter: `ruff check pyosmo/ --fix && ruff format pyosmo/`
- Verify all property tests pass
- Verify TLA+ specs are syntactically valid (if tooling available)

---

## Constraints and Guidelines

1. **Read before writing**: Always read the relevant source files before modifying them. Understand the existing code patterns.

2. **Test after each change**: Run `pytest pyosmo/tests/` after every code modification. Do not proceed if tests fail.

3. **Lint after each change**: Run `ruff check pyosmo/ --fix && ruff format pyosmo/` after code changes.

4. **Follow existing patterns**: Match the project's code style (double quotes, 120 char lines, type hints encouraged).

5. **Minimal changes for bug fixes**: Fix only what's broken. Don't refactor surrounding code.

6. **TLA+ specs should be self-documenting**: Include comments mapping each action to the Python source location (file:line).

7. **If TLC is not installed**: Write the specifications correctly anyway. Document that verification requires `tla2tools.jar` (available from https://github.com/tlaplus/tlaplus/releases). The specs themselves have value as executable documentation.

8. **If stuck on TLA+ syntax**: Use standard TLA+ patterns from Leslie Lamport's examples. The key operators are:
   - `/\` (and), `\/` (or), `=>` (implies)
   - `'` (next state), `UNCHANGED` (stuttering)
   - `[]` (always), `<>` (eventually), `~>` (leads-to)
   - `WF_vars(Action)` (weak fairness)

9. **Commit messages**: If committing, use descriptive messages like "Add TLA+ engine state machine specification" or "Fix StepCoverage range validation bug".

10. **Do not skip phases**: Complete Phase 0 (bug fixes) before Phase 1 (Hypothesis tests) before Phase 2 (TLA+ specs). Each phase validates the previous.

---

## Definition of Done

- [ ] All 5 bugs from Section 7 of PRD are fixed with regression tests
- [ ] Property-based tests in `test_properties.py` pass (5+ properties)
- [ ] `PyOsmoEngine.tla` specification written with safety and liveness properties
- [ ] `ErrorStrategyCascade.tla` covers all 16 strategy combinations
- [ ] `BalancingAlgorithm.tla` proves fairness property
- [ ] `WeightedBalancing.tla` proves weight positivity
- [ ] `EndConditions.tla` proves termination for non-Endless configs
- [ ] All TLC configs written
- [ ] README for specs directory exists
- [ ] `pytest pyosmo/tests/` passes with zero failures
- [ ] `ruff check pyosmo/` passes with zero errors
- [ ] No regressions in existing test suite
