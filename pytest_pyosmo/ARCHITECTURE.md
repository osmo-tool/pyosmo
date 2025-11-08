# Pytest-Pyosmo Discovery: Technical Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          pytest Execution                               │
└─────────────────────────────────────────────────────────────────────────┘
            │
            ├─ pytest starts
            │
            ├─ pytest loads plugins via entry_points
            │  └─ Loads pytest_pyosmo_plugin.py
            │
            ├─ pytest_configure(config) hook
            │  └─ Register markers: @pytest.mark.model, @pytest.mark.quick
            │
            ├─ Scan test files
            │  └─ pytest_collect_file(parent, file_path) hook
            │     ├─ Is it test_*.py?
            │     ├─ Import module
            │     ├─ Has @pytest.model classes?
            │     └─ YES → Return ModelModule collector
            │
            ├─ ModelModule.collect()
            │  ├─ Call super().collect() for regular pytest tests
            │  └─ For each @pytest.model class:
            │     └─ Yield ModelCollector
            │
            ├─ ModelCollector.collect()
            │  ├─ Instantiate model
            │  ├─ pyosmo.Osmo(model).generate()
            │  ├─ For each generated sequence:
            │  │  └─ Yield ModelTestItem
            │  │
            │
            ├─ pytest executes each ModelTestItem
            │  ├─ Create fresh model instance
            │  ├─ Call model.before_test()
            │  ├─ For each step in sequence:
            │  │  ├─ Get step method
            │  │  ├─ Execute step
            │  │  └─ If assertion fails: Report failure + sequence context
            │  │
            │
            └─ Report results
```

## File Discovery Flow

```
test_models_example.py (Your test file)
        │
        ├─ Contains @pytest.model classes
        │  ├─ CounterModel
        │  ├─ QuickCounterModel (@pytest.mark.quick)
        │  ├─ ComprehensiveCounterModel (@pytest.mark.comprehensive)
        │  ├─ AuthenticationModel
        │  └─ ShoppingCartModel
        │
pytest_collect_file() hook
        │
        ├─ Is filename test_*.py? YES
        ├─ Can import? YES
        ├─ Has @pytest.model classes? YES
        │
        └─ Return ModelModule collector
                │
                ModelModule.collect()
                │
                ├─ super().collect() → Normal tests/fixtures
                │
                ├─ find all @pytest.model classes
                │  └─ CounterModel
                │  └─ QuickCounterModel
                │  └─ ComprehensiveCounterModel
                │  └─ AuthenticationModel
                │  └─ ShoppingCartModel
                │
                └─ For each: yield ModelCollector
```

## Model to Tests Conversion

```
@pytest.model
class CounterModel:
    def __init__(self):
        self.value = 0
    
    def before_test(self):
        self.value = 0
    
    def guard_increment(self):
        return True
    
    def step_increment(self):
        self.value += 1
    
    def guard_decrement(self):
        return self.value > 0
    
    def step_decrement(self):
        self.value -= 1


        ↓ ModelCollector.collect()
        ↓ Instantiate model
        ↓ pyosmo.Osmo(model).generate()


Generated sequences (5 tests):
        
Test 1: ["step_increment", "step_increment", "step_decrement"]
Test 2: ["step_increment", "step_decrement", "step_increment"]
Test 3: ["step_increment", "step_increment", "step_increment"]
Test 4: ["step_decrement", "step_increment"]  (decrement guard returns False initially)
Test 5: ["step_increment"]


        ↓ Create ModelTestItem for each sequence
        

pytest Items:
        
test_models_example.py::CounterModel::test_sequence_000
test_models_example.py::CounterModel::test_sequence_001
test_models_example.py::CounterModel::test_sequence_002
test_models_example.py::CounterModel::test_sequence_003
test_models_example.py::CounterModel::test_sequence_004


        ↓ pytest runs each item
        ↓ ModelTestItem.runtest()
        

Each test:
1. model = CounterModel()
2. model.before_test()  # value = 0
3. Execute step_increment()  # value = 1
4. Execute step_increment()  # value = 2
5. Execute step_decrement()  # value = 1
6. All assertions passed → PASSED
```

## Test Execution Detail

### For test_sequence_000:

```
Model instance created
│
before_test() called
│  self.value = 0
│
Execute sequence: [step_increment, step_increment, step_decrement]
│
├─ step_increment()
│  ├─ self.value += 1  # 0 → 1
│  └─ assert self.value > 0  # PASS
│
├─ step_increment()
│  ├─ self.value += 1  # 1 → 2
│  └─ assert self.value > 0  # PASS
│
├─ step_decrement()
│  ├─ self.value -= 1  # 2 → 1
│  └─ assert self.value >= 0  # PASS
│
Result: PASSED ✅
```

### If assertion fails (test_sequence_003 example):

```
Model instance created
│
before_test() called
│  self.value = 0
│
Execute sequence: [step_decrement, step_increment]
│
├─ Try step_decrement()
│  ├─ guard_decrement() returns False (self.value == 0)
│  └─ Guard prevented this step - that's actually OK!
│
Step execution stopped because guard returned False
│
Result: Test completes, but only executed 0 steps from sequence
```

Actually, pyosmo handles guards, so sequences are always valid.

### Real failure example:

```
Execute sequence: [step_increment, step_increment, step_increment, ...]
│
├─ step_increment(): PASS (value: 0 → 1)
├─ step_increment(): PASS (value: 1 → 2)
├─ step_increment(): PASS (value: 2 → 3)
│
├─ step_some_bad_step():
│  ├─ self.bad_operation()  # RAISES AssertionError!
│  └─ AssertionError: "Something went wrong"
│
Error captured with context:
{
    "model": "CounterModel",
    "sequence_num": 7,
    "full_sequence": ["step_increment", "step_increment", "step_increment", "step_some_bad_step"],
    "failed_at": "step_some_bad_step",
    "error": "AssertionError: Something went wrong"
}

Result: FAILED ❌
```

## Marker Configuration Flow

### Default Model

```python
@pytest.model
class MyModel:
    pass
```

Configuration applied:
- test_end_condition: Length(50)
- test_suite_end_condition: Length(5)
- seed: 42
- Result: 5 tests, ~50 steps each


### Quick Model

```python
@pytest.mark.quick
@pytest.model
class MyModel:
    pass
```

Configuration applied:
- test_end_condition: Length(20)
- test_suite_end_condition: Length(2)
- seed: 42
- Result: 2 tests, ~20 steps each


### Comprehensive Model

```python
@pytest.mark.comprehensive
@pytest.model
class MyModel:
    pass
```

Configuration applied:
- test_end_condition: Length(100)
- test_suite_end_condition: TransitionCoverage(100)
- seed: 42
- Result: ~10 tests, 100% transition coverage


### Stress Model

```python
@pytest.mark.stress
@pytest.model
class MyModel:
    pass
```

Configuration applied:
- test_end_condition: Length(500)
- test_suite_end_condition: Length(50)
- seed: 42
- Result: 50 tests, ~500 steps each

## Plugin Hook Sequence

```
pytest startup
│
├─ pytest_load_initial_conftests()
│  └─ Load conftest.py files
│     └─ conftest.py: pytest_plugins = ["pytest_pyosmo_plugin"]
│        └─ pytest loads pytest_pyosmo_plugin
│
├─ pytest_configure(config)
│  └─ Our hook: Register markers
│
├─ pytest_collection()
│  └─ pytest_collect_file(parent, file_path)
│     └─ Our hook: Check for @pytest.model classes
│        └─ For each test file
│           └─ If has models: Return ModelModule
│
├─ Collection phase continues
│  └─ ModelModule.collect()
│     └─ For each @pytest.model class
│        └─ Yield ModelCollector
│        │
│        └─ ModelCollector.collect()
│           └─ Generate test sequences
│           └─ Yield ModelTestItem for each sequence
│
├─ pytest_collection_finish(session)
│  └─ Collection complete, we have all test items
│
├─ Test execution phase
│  └─ For each ModelTestItem
│     └─ ModelTestItem.runtest()
│        └─ Execute the sequence
│
└─ Report results
```

## Class Hierarchy

```
pytest.Item (base class)
├─ pytest.Function (for regular test functions)
├─ pytest.Class (for test classes)
└─ ModelTestItem (our class for model tests)
   │
   ├─ Attributes:
   │  ├─ sequence: ["step_a", "step_b", ...]
   │  ├─ model_class: CounterModel
   │  ├─ seq_num: 0
   │  └─ nodeid: "test_file.py::CounterModel::test_sequence_000"
   │
   └─ Methods:
      ├─ runtest(): Execute the sequence
      └─ repr_failure(excinfo): Format error message

pytest.Collector (base class)
├─ pytest.Module (for .py files)
├─ pytest.Class (for test classes)
└─ ModelCollector (our class for model collection)
   │
   ├─ Attributes:
   │  ├─ obj: CounterModel (the @pytest.model class)
   │  └─ nodeid: "test_file.py::CounterModel"
   │
   └─ Methods:
      └─ collect(): Yield ModelTestItem for each sequence

ModelModule (our class)
│
├─ Extends: pytest.Module
├─ Attributes:
│  └─ Inherits from Module
│
└─ Methods:
   ├─ collect(): Find @pytest.model classes
   │  ├─ Call super().collect() for regular tests
   │  └─ For each @pytest.model class: yield ModelCollector
```

## Data Flow Diagram

```
Input: test_models_example.py
       │
       ├─ Source code
       │
       └─ Contains:
          @pytest.model
          class CounterModel: ...


pytest_collect_file() Hook
       │
       ├─ Import module
       │
       ├─ Inspect.getmembers() to find classes
       │
       └─ Check pytestmark for "model"


ModelModule Collector
       │
       ├─ Collect regular pytest tests
       │
       ├─ Find @pytest.model classes
       │
       └─ Yield ModelCollector for each


ModelCollector
       │
       ├─ Instantiate model
       │
       ├─ Call pyosmo.Osmo(model)
       │
       ├─ Generate sequences
       │
       └─ Yield ModelTestItem for each sequence


ModelTestItem × 5
       │
       ├─ test_sequence_000: [step_a, step_b]
       ├─ test_sequence_001: [step_a, step_c, step_b]
       ├─ test_sequence_002: [step_b, step_b]
       ├─ test_sequence_003: [step_c]
       └─ test_sequence_004: [step_a, step_b, step_c, step_a]


pytest Execution
       │
       ├─ Run test_sequence_000
       │  ├─ Create model
       │  ├─ Call before_test()
       │  ├─ Execute [step_a, step_b]
       │  └─ Result: PASSED ✅
       │
       ├─ Run test_sequence_001
       │  └─ Result: PASSED ✅
       │
       ├─ Run test_sequence_002
       │  └─ Result: FAILED ❌ (assertion in step_b)
       │
       ├─ Run test_sequence_003
       │  └─ Result: PASSED ✅
       │
       └─ Run test_sequence_004
          └─ Result: PASSED ✅


Output: Test Results
        │
        ├─ 4 passed, 1 failed
        │
        └─ Show which sequence failed with full context
```

## Discovery Comparison: Before vs After

### Before (without pytest-pyosmo)

```bash
pytest tests/ -v

# Output:
tests/test_counter.py::test_manual_1 PASSED
tests/test_counter.py::test_manual_2 PASSED
tests/test_counter.py::test_manual_3 PASSED
tests/test_counter.py::test_manual_4 PASSED
tests/test_counter.py::test_manual_5 PASSED

# Manual: Had to write each test manually
# Limited: Only covered scenarios you thought of
# Brittle: Each test change requires code change
```

### After (with pytest-pyosmo)

```bash
pytest tests/ -v

# Output:
tests/test_counter.py::CounterModel::test_sequence_000 PASSED
tests/test_counter.py::CounterModel::test_sequence_001 PASSED
tests/test_counter.py::CounterModel::test_sequence_002 PASSED
tests/test_counter.py::CounterModel::test_sequence_003 PASSED
tests/test_counter.py::CounterModel::test_sequence_004 PASSED

# Automatic: Tests generated from model
# Comprehensive: Explores all valid sequences
# Maintainable: Change model, get new tests
```

## Key Design Decisions

### Why ModelModule extends Module?

- Reason: We still want regular pytest tests in the same file
- Benefit: Models and tests can coexist
- Implementation: Call super().collect() first

### Why ModelCollector vs ModelTestItem for generation?

- ModelCollector: Orchestrates, handles errors, generates sequences
- ModelTestItem: Executes one sequence, handles step failures
- Separation: Each class has single responsibility

### Why seed = 42?

- Reason: Tests should be reproducible
- Benefit: Same seed = same sequence every run
- Downside: Different seed = different sequences (useful for stress testing)

### Why before_test()?

- Reason: Reset state between sequences
- Benefit: Each test starts clean
- Alternative: Create new model for each test (we do this too)

## Performance Considerations

### Generation time

- Instantiate model: ~1ms
- Generate 5 sequences via pyosmo: ~10-50ms
- Total per model: ~50-100ms

### Execution time

- Create model: ~1ms
- Run sequence (20-50 steps): ~50-200ms
- Total per test: ~50-200ms

### Scale

- 5 models × 5 tests = 25 tests
- Total generation + execution: ~10 seconds
- Quick tests: ~1 second
- Comprehensive tests: ~30 seconds

Use markers:
- `@pytest.mark.quick` for fast feedback (commit hooks)
- Default for normal CI
- `@pytest.mark.comprehensive` for nightly/release

## Error Handling

### Instantiation error

```python
class BadModel:
    def __init__(self, required_arg):
        pass  # No default value

# Plugin detects: Cannot instantiate
# Shows: ModelError item in output
# Doesn't crash pytest
```

### Generation error

```python
model = SomeModel()
osmo = pyosmo.Osmo(model)
osmo.generate()  # Fails (no guards/steps)

# Plugin detects: Cannot generate
# Shows: ModelGenerationError item
# Doesn't crash pytest
```

### Execution error

```python
def step_something(self):
    assert False  # Intentional failure

# Plugin detects: Step failed
# Shows: FAILED with sequence context
# Test marked as failed, pytest continues
```

## Summary

The plugin works by leveraging pytest's plugin API:

1. **pytest_collect_file** - We intercept file collection
2. **Collector/Item hierarchy** - We create custom collectors and items
3. **Markers** - We use pytest markers for configuration
4. **Standard test execution** - Pytest runs our items like normal tests

This is clean, extensible, and uses pytest's intended extension points.
