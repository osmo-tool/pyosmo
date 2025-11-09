# Pytest-Pyosmo Discovery: Quick Start Guide

## What you have

This prototype demonstrates **pytest discovery of @pytest.model classes** - the first phase of the pytest-pyosmo integration strategy.

Files:
- `pytest_pyosmo_plugin.py` - The actual plugin (400 lines of code)
- `test_models_example.py` - Example models to test
- `conftest.py` - Integration instructions

## Installation

```bash
# Install dependencies
pip install pytest pyosmo

# That's it! The plugin is in this directory.
```

## Run the examples

### See what will be tested

```bash
pytest --collect-only -q

# Output shows all discovered models and generated tests
```

### Run all tests

```bash
pytest test_models_example.py -v

# Output:
# test_models_example.py::CounterModel::test_sequence_000 PASSED
# test_models_example.py::CounterModel::test_sequence_001 PASSED
# test_models_example.py::CounterModel::test_sequence_002 PASSED
# test_models_example.py::CounterModel::test_sequence_003 PASSED
# test_models_example.py::CounterModel::test_sequence_004 PASSED
# test_models_example.py::QuickCounterModel::test_sequence_000 PASSED
# test_models_example.py::QuickCounterModel::test_sequence_001 PASSED
# ...
```

### Run only quick tests (smoke test)

```bash
pytest test_models_example.py -m quick -v

# Runs only @pytest.mark.quick models (2 tests each)
# Fast: finishes in < 1 second
```

### Run only comprehensive tests

```bash
pytest test_models_example.py -m comprehensive -v

# Runs @pytest.mark.comprehensive models (10+ tests each)
# Thorough: ensures 100% state coverage
```

### Run specific model

```bash
pytest test_models_example.py::CounterModel -v
pytest test_models_example.py::AuthenticationModel -v
```

### Run with detailed output

```bash
pytest test_models_example.py -v -s

# The -s flag shows print() statements from models
# You'll see the sequence of actions each test took
```

## How it works - execution flow

```
1. pytest test_models_example.py
   ↓
2. conftest.py loads pytest_pyosmo_plugin
   ↓
3. Plugin's pytest_collect_file() hook scans files
   ↓
4. Finds @pytest.model classes in test_models_example.py
   ↓
5. For each model:
   a. Instantiates it
   b. Uses pyosmo to generate random sequences
   c. Creates a pytest test item for each sequence
   ↓
6. pytest runs all generated test items
   ↓
7. Results displayed
```

## Understanding the models

Each `@pytest.model` class has:

1. **`guard_*` methods** - Preconditions (when is this action valid?)
2. **`step_*` methods** - The action to execute
3. **`before_test()`** - Reset state before each generated test

Example:

```python
@pytest.model
class CounterModel:
    def __init__(self):
        self.value = 0
    
    def before_test(self):
        # Called before each generated test - resets state
        self.value = 0
    
    def guard_increment(self):
        # When can we increment? Always
        return True
    
    def step_increment(self):
        # What does increment do?
        self.value += 1
        assert self.value > 0  # Verify it worked
    
    def guard_decrement(self):
        # When can we decrement? Only if > 0
        return self.value > 0
    
    def step_decrement(self):
        # What does decrement do?
        self.value -= 1
        assert self.value >= 0  # Verify invariant
```

Pyosmo generates sequences like:
- `increment → increment → decrement`
- `increment → decrement → decrement → (can't decrement, guard prevents)`
- `increment → increment → increment`
- etc.

Each sequence is a pytest test. If any step fails, the whole test fails.

## The plugin code explained (simplified)

```python
# 1. Pytest finds test files
def pytest_collect_file(parent, file_path):
    # 2. Check if file has @pytest.model classes
    if _has_model_classes(module):
        # 3. Return collector for this file
        return ModelModule.from_parent(parent, path=file_path)

# 4. Collector finds @pytest.model classes
class ModelModule(Module):
    def collect(self):
        for name, obj in inspect.getmembers(module):
            if _has_pytest_model_marker(obj):
                # 5. Yield collector for each model
                yield ModelCollector.from_parent(self, name=name, obj=obj)

# 6. Each model collector generates tests
class ModelCollector(Collector):
    def collect(self):
        model = self.obj()  # Instantiate model
        
        osmo = pyosmo.Osmo(model)
        osmo.generate()  # Generate sequences
        
        for sequence in sequences:
            # 7. Create test item for each sequence
            yield ModelTestItem.from_parent(
                self, name=f"test_sequence_000", sequence=sequence
            )

# 8. Each test item is executed by pytest
class ModelTestItem(Item):
    def runtest(self):
        model = self.model_class()
        model.before_test()  # Reset
        
        for step_name in self.sequence:
            step_method = getattr(model, step_name)
            step_method()  # Execute step
```

That's the entire plugin! The complexity is just in error handling and configuration.

## Trying it out

### Create your own model

Create `test_my_model.py`:

```python
import pytest

@pytest.model
class BankAccountModel:
    def __init__(self):
        self.balance = 0
    
    def before_test(self):
        self.balance = 0
    
    def guard_deposit(self):
        return True
    
    def step_deposit(self):
        self.balance += 100
        assert self.balance > 0
    
    def guard_withdraw(self):
        return self.balance >= 50
    
    def step_withdraw(self):
        self.balance -= 50
        assert self.balance >= 0
```

Run it:

```bash
pytest test_my_model.py -v -s
```

The plugin will:
1. Find `@pytest.model BankAccountModel`
2. Generate ~5 random sequences
3. Run each sequence
4. Show results

### Modify generation

Control how many tests via markers:

```python
@pytest.mark.quick
@pytest.model
class FastBankModel(BankAccountModel):
    pass

@pytest.mark.comprehensive
@pytest.model
class ThoroughBankModel(BankAccountModel):
    pass

# Quick: 2 tests, 20 steps each
# Comprehensive: 10 tests, 100 steps each, 100% coverage
```

## Next steps

This plugin demonstrates **Phase 1: Discovery**.

Future phases:
- **Phase 2**: Fixture injection (models use pytest fixtures)
- **Phase 3**: Marker configuration (quick/comprehensive/stress)
- **Phase 4**: Parametrization (test across configurations)
- **Phase 5**: Plugin ecosystem (parallel execution, coverage, etc.)

## Troubleshooting

### "No tests found"

Check:
- File name starts with `test_`
- Class has `@pytest.model` decorator
- Model has at least one `guard_*/step_*` pair

```bash
# Debug: see what's discovered
pytest --collect-only -q
```

### "Cannot instantiate model"

If model `__init__` requires arguments:

```python
@pytest.model
class MyModel:
    def __init__(self, some_arg):
        # Phase 2 will support fixture injection
        # For now, provide a default
        pass
```

### Model tests fail

Add print() and run with `-s`:

```python
def step_something(self):
    print(f"Value before: {self.value}")
    self.value += 1
    print(f"Value after: {self.value}")

# Then:
pytest test_my_model.py -v -s
```

### Different tests each run

That's expected! Sequences are random. To get same sequences:

```python
# In your model __init__
osmo.seed = 42  # Same seed = same sequences
```

(Phase 3 configures this via markers)

## Further exploration

1. **Read the plugin code** - `pytest_pyosmo_plugin.py` is well-commented
2. **Study the examples** - `test_models_example.py` has various patterns
3. **Read pytest plugin docs** - https://docs.pytest.org/en/stable/how-to-write-plugins.html
4. **Read pyosmo docs** - https://github.com/osmo-tool/pyosmo

## Success!

If you can run this and see tests passing:

```bash
pytest test_models_example.py -v
# ... tests pass ...
```

You've successfully integrated model-based testing discovery into pytest! 🎉

This is exactly what users would get when installing `pytest-pyosmo`.

## Questions?

Check the longer implementation guide: `PYTEST_PYOSMO_DISCOVERY_IMPLEMENTATION.md`
