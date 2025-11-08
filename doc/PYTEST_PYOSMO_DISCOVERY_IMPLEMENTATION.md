# Implementing pytest-pyosmo Discovery: A Practical Guide

## Overview

This guide shows the exact code needed to make pytest discover and run pyosmo models automatically. By the end, you'll have a working plugin that makes models discoverable like normal pytest tests.

**What we're building:**
```bash
pytest tests/models/test_checkout.py -v

# Output:
# tests/models/test_checkout.py::CheckoutModel::test_sequence_0 PASSED
# tests/models/test_checkout.py::CheckoutModel::test_sequence_1 PASSED
# tests/models/test_checkout.py::CheckoutModel::test_sequence_2 FAILED
```

---

## Part 1: Project structure

```
pytest-pyosmo/
├── setup.py                          # Package metadata
├── pyproject.toml                    # Modern Python packaging
├── pytest_pyosmo/                    # Plugin code
│   ├── __init__.py
│   ├── plugin.py                     # Main pytest hooks
│   ├── collector.py                  # Model discovery logic
│   ├── markers.py                    # Marker support
│   └── config.py                     # Configuration management
├── tests/                            # Tests for the plugin itself
│   ├── test_discovery.py
│   ├── test_execution.py
│   └── fixtures/
│       └── sample_models.py          # Example models
└── examples/                         # User-facing examples
    └── test_checkout_model.py
```

---

## Part 2: The plugin entry point

### File: `setup.py`

```python
from setuptools import setup, find_packages

setup(
    name="pytest-pyosmo",
    version="1.0.0",
    description="Model-based testing plugin for pytest",
    author="Pyosmo Team",
    author_email="hello@pyosmo.dev",
    url="https://github.com/osmo-tool/pytest-pyosmo",
    packages=find_packages(),
    install_requires=[
        "pytest>=7.0",
        "pyosmo>=1.0.0",
    ],
    entry_points={
        "pytest11": [
            "pytest_pyosmo = pytest_pyosmo.plugin:pytest_plugins",
        ]
    },
    python_requires=">=3.9",
)
```

When pytest loads, it will automatically discover and load our plugin via the `pytest11` entry point.

### File: `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "pytest-pyosmo"
version = "1.0.0"
description = "Model-based testing plugin for pytest"
requires-python = ">=3.9"
dependencies = [
    "pytest>=7.0",
    "pyosmo>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest-cov",
    "black",
    "mypy",
    "flake8",
]

[project.urls]
Homepage = "https://github.com/osmo-tool/pytest-pyosmo"
Repository = "https://github.com/osmo-tool/pytest-pyosmo.git"
```

---

## Part 3: The core plugin code

### File: `pytest_pyosmo/__init__.py`

```python
"""Pytest plugin for pyosmo model-based testing"""

__version__ = "1.0.0"

from .plugin import pytest_plugins

__all__ = ["pytest_plugins"]
```

### File: `pytest_pyosmo/plugin.py`

```python
"""Main pytest plugin entry point"""

import inspect
from pathlib import Path
from typing import Optional, List, Any

from _pytest.python import Module
from _pytest.config import Config


def pytest_configure(config: Config):
    """Called after command line options are parsed"""
    config.addinivalue_line(
        "markers",
        "model: mark test as a model-based test",
    )
    config.addinivalue_line(
        "markers",
        "quick: quick model run (smoke test)",
    )
    config.addinivalue_line(
        "markers",
        "comprehensive: comprehensive model run",
    )
    config.addinivalue_line(
        "markers",
        "stress: extended stress test",
    )


def pytest_collect_file(parent, file_path):
    """
    Pytest hook: called for each file during test collection.
    We look for files containing @pytest.model decorated classes.
    """
    # Only process test_*.py files
    if not file_path.name.startswith("test_"):
        return None
    
    # Only process .py files
    if file_path.suffix != ".py":
        return None
    
    # Import the module and check for @pytest.model classes
    try:
        module = import_module(file_path)
    except Exception as e:
        # Let pytest handle import errors normally
        return None
    
    # Check if this module has any model classes
    if not has_model_classes(module):
        return None
    
    # Return our custom collector that will find model classes
    from .collector import ModelModule
    return ModelModule.from_parent(parent, path=file_path)


def has_model_classes(module) -> bool:
    """Check if a module contains any @pytest.model decorated classes"""
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if has_pytest_model_marker(obj):
            return True
    return False


def has_pytest_model_marker(obj: Any) -> bool:
    """Check if class has @pytest.model decorator"""
    # The marker is stored in pytestmark attribute
    if not hasattr(obj, "pytestmark"):
        return False
    
    marks = obj.pytestmark if isinstance(obj.pytestmark, list) else [obj.pytestmark]
    
    for mark in marks:
        if hasattr(mark, "mark") and mark.mark.name == "model":
            return True
        if hasattr(mark, "name") and mark.name == "model":
            return True
    
    return False


def import_module(path: Path):
    """Import a Python module from file path"""
    import importlib.util
    
    spec = importlib.util.spec_from_file_location(
        path.stem,
        path,
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import {path}")
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Register the plugin
pytest_plugins = "pytest_pyosmo.plugin"
```

---

## Part 4: The collector - finding and organizing models

### File: `pytest_pyosmo/collector.py`

```python
"""
Pytest collector for pyosmo models.

This module implements the discovery and collection of model classes
and the generation of test items for each model.
"""

import inspect
from typing import List, Generator, Any, Type

import pytest
from _pytest.nodes import Collector, Item
from _pytest.python import Module as PytestModule


class ModelModule(PytestModule):
    """
    Custom module collector for modules containing @pytest.model classes.
    
    This extends pytest's Module class to handle model discovery.
    """
    
    def collect(self) -> Generator[Collector, None, None]:
        """
        Discover model classes in this module.
        
        Yields ModelCollector instances for each @pytest.model class.
        """
        # First collect normal pytest tests/fixtures using parent behavior
        # (This ensures any regular tests in the same file still work)
        for item in super().collect():
            yield item
        
        # Then collect model classes
        from .plugin import has_pytest_model_marker
        
        for name, obj in inspect.getmembers(self.obj, inspect.isclass):
            if has_pytest_model_marker(obj):
                yield ModelCollector.from_parent(
                    self,
                    name=name,
                    obj=obj,
                )


class ModelCollector(Collector):
    """
    Collector for a single @pytest.model class.
    
    Responsible for:
    1. Instantiating the model
    2. Generating test sequences
    3. Creating test items for each sequence
    """
    
    def __init__(self, name, parent, obj):
        super().__init__(name, parent)
        self.obj = obj  # The model class
    
    def collect(self) -> Generator[Item, None, None]:
        """
        Generate test items from the model.
        
        Steps:
        1. Generate test sequences using pyosmo
        2. Create a ModelTestItem for each sequence
        """
        import pyosmo
        from .config import get_model_config
        
        # Get configuration (quick, comprehensive, stress, custom)
        config = get_model_config(self.obj, self.config)
        
        # Instantiate the model
        try:
            model = self.obj()
        except Exception as e:
            # If model instantiation fails, report it
            yield ModelInstantiationError.from_parent(
                self,
                name="instantiation_error",
                model_class=self.obj,
                error=e,
            )
            return
        
        # Generate test sequences
        try:
            osmo = pyosmo.Osmo(model)
            
            # Apply configuration
            osmo.test_end_condition = config["test_end_condition"]
            osmo.test_suite_end_condition = config["test_suite_end_condition"]
            osmo.seed = config["seed"]
            
            # Generate and collect sequences
            sequences = osmo.generate(return_sequences=True)
        except Exception as e:
            yield ModelGenerationError.from_parent(
                self,
                name="generation_error",
                model_class=self.obj,
                error=e,
            )
            return
        
        # Create a test item for each sequence
        for sequence_num, sequence in enumerate(sequences):
            yield ModelTestItem.from_parent(
                self,
                name=f"test_sequence_{sequence_num:03d}",
                sequence=sequence,
                model_class=self.obj,
                sequence_num=sequence_num,
                config=config,
            )


class ModelTestItem(Item):
    """
    A single generated test sequence.
    
    This is what pytest executes. It contains:
    - The sequence of steps to execute
    - The model class to instantiate
    - Configuration for this test
    """
    
    def __init__(self, name, parent, sequence, model_class, sequence_num, config):
        super().__init__(name, parent)
        self.sequence = sequence          # List of step names: ["step_login", "step_add_item"]
        self.model_class = model_class    # The @pytest.model class
        self.sequence_num = sequence_num  # Test number (0, 1, 2, ...)
        self.config = config              # Configuration dict
    
    def runtest(self):
        """Execute the test sequence"""
        # Instantiate model
        model = self.model_class()
        
        # Call before_test if it exists
        if hasattr(model, "before_test"):
            model.before_test()
        
        # Execute each step in sequence
        for step_name in self.sequence:
            # Get the step method
            if not hasattr(model, step_name):
                raise AttributeError(
                    f"Model {self.model_class.__name__} missing step: {step_name}"
                )
            
            step_method = getattr(model, step_name)
            
            # Execute it
            try:
                step_method()
            except Exception as e:
                # Enhance error message with sequence context
                raise ModelTestStepFailure(
                    f"Step {step_name} failed in sequence {self.sequence_num}\n"
                    f"Full sequence: {' → '.join(self.sequence)}\n"
                    f"Failed at: {step_name}"
                ) from e
    
    def repr_failure(self, excinfo):
        """
        Custom failure representation.
        
        Shows the full sequence so developers can understand what went wrong.
        """
        sequence_str = " → ".join(self.sequence)
        return (
            f"Model: {self.model_class.__name__}\n"
            f"Sequence {self.sequence_num}: {sequence_str}\n"
            f"\nFailure:\n{excinfo.exconly()}"
        )


class ModelInstantiationError(Item):
    """Marker item for model instantiation errors"""
    
    def __init__(self, name, parent, model_class, error):
        super().__init__(name, parent)
        self.model_class = model_class
        self.error = error
    
    def runtest(self):
        raise RuntimeError(
            f"Cannot instantiate model {self.model_class.__name__}: {self.error}"
        )


class ModelGenerationError(Item):
    """Marker item for test generation errors"""
    
    def __init__(self, name, parent, model_class, error):
        super().__init__(name, parent)
        self.model_class = model_class
        self.error = error
    
    def runtest(self):
        raise RuntimeError(
            f"Cannot generate tests for {self.model_class.__name__}: {self.error}"
        )


class ModelTestStepFailure(Exception):
    """Exception raised when a model test step fails"""
    pass
```

---

## Part 5: Configuration management

### File: `pytest_pyosmo/config.py`

```python
"""
Configuration for model test generation.

Controls how many tests to generate, test length, coverage targets, etc.
based on markers and custom configuration.
"""

from typing import Dict, Any
import pyosmo


def get_model_config(model_class, pytest_config) -> Dict[str, Any]:
    """
    Extract configuration for model test generation.
    
    Priority:
    1. Model class attributes (if model explicitly sets them)
    2. Pytest markers (quick, comprehensive, stress)
    3. pytest.ini configuration
    4. Defaults
    """
    
    # Get default configuration
    config = get_default_config()
    
    # Get pytest markers
    if hasattr(model_class, "pytestmark"):
        markers = model_class.pytestmark
        if not isinstance(markers, list):
            markers = [markers]
        
        for marker in markers:
            marker_name = getattr(marker, "name", None)
            
            if marker_name == "quick":
                config.update(QUICK_CONFIG)
            elif marker_name == "comprehensive":
                config.update(COMPREHENSIVE_CONFIG)
            elif marker_name == "stress":
                config.update(STRESS_CONFIG)
    
    # Get pytest.ini configuration (if set)
    if pytest_config and hasattr(pytest_config, "option"):
        if hasattr(pytest_config.option, "pyosmo_num_tests"):
            config["test_suite_end_condition"] = pyosmo.end_conditions.Length(
                pytest_config.option.pyosmo_num_tests
            )
    
    # Allow model class to override (if it defines __pyosmo_config__)
    if hasattr(model_class, "__pyosmo_config__"):
        config.update(model_class.__pyosmo_config__)
    
    return config


def get_default_config() -> Dict[str, Any]:
    """Default configuration for moderate testing"""
    return {
        "test_end_condition": pyosmo.end_conditions.Length(50),
        "test_suite_end_condition": pyosmo.end_conditions.Length(5),
        "seed": 42,  # Reproducible
    }


# Marker configurations
QUICK_CONFIG = {
    "test_end_condition": pyosmo.end_conditions.Length(20),
    "test_suite_end_condition": pyosmo.end_conditions.Length(2),
    "seed": 42,
}

COMPREHENSIVE_CONFIG = {
    "test_end_condition": pyosmo.end_conditions.Length(100),
    "test_suite_end_condition": pyosmo.end_conditions.TransitionCoverage(100),
    "seed": 42,
}

STRESS_CONFIG = {
    "test_end_condition": pyosmo.end_conditions.Length(500),
    "test_suite_end_condition": pyosmo.end_conditions.Length(50),
    "seed": 42,
}
```

---

## Part 6: Making models discoverable

### File: `pytest_pyosmo/markers.py`

```python
"""
Markers and decorators for marking model classes.

Provides the @pytest.model decorator that marks a class as a pyosmo model.
"""

import pytest


# The @pytest.model decorator is just a pytest marker
pytest.model = pytest.mark.model


# Users can also import it directly
__all__ = ["pytest.model"]
```

### Usage in user code:

```python
# tests/models/test_checkout.py
import pytest

@pytest.model
class CheckoutModel:
    def __init__(self):
        self.logged_in = False
        self.cart = []
    
    def before_test(self):
        self.logged_in = False
        self.cart = []
    
    def guard_login(self):
        return not self.logged_in
    
    def step_login(self):
        self.logged_in = True
```

---

## Part 7: Complete working example

### File: `examples/test_counter_model.py`

```python
"""
Example: Simple counter model for demonstration.

Run with:
    pip install pytest pytest-pyosmo pyosmo
    pytest examples/test_counter_model.py -v
"""

import pytest


@pytest.model
class CounterModel:
    """
    Model of a simple counter.
    
    The counter can increment, decrement, and reset.
    Invariant: value should never go negative.
    """
    
    def __init__(self):
        self.value = 0
    
    def before_test(self):
        """Reset state before each generated test"""
        self.value = 0
    
    # Increment action
    def guard_increment(self):
        """Can always increment"""
        return True
    
    def step_increment(self):
        """Increment and verify"""
        old_value = self.value
        self.value += 1
        assert self.value == old_value + 1, "Increment failed"
    
    # Decrement action
    def guard_decrement(self):
        """Can only decrement if not at zero"""
        return self.value > 0
    
    def step_decrement(self):
        """Decrement and verify"""
        old_value = self.value
        self.value -= 1
        assert self.value == old_value - 1, "Decrement failed"
        assert self.value >= 0, "Value went negative!"
    
    # Reset action
    def guard_reset(self):
        """Can always reset"""
        return True
    
    def step_reset(self):
        """Reset to zero"""
        self.value = 0
        assert self.value == 0, "Reset failed"


# You can also define multiple models in the same file
@pytest.mark.quick
class QuickCounterModel(CounterModel):
    """
    Same model but marked for quick testing.
    Will generate fewer, shorter test sequences.
    """
    pass


@pytest.mark.comprehensive
class ExhaustiveCounterModel(CounterModel):
    """
    Same model but marked for comprehensive testing.
    Will generate many tests until full coverage achieved.
    """
    pass
```

### Run it:

```bash
# Install
pip install pytest pytest-pyosmo pyosmo

# Run the example
pytest examples/test_counter_model.py -v

# Output:
# examples/test_counter_model.py::CounterModel::test_sequence_000 PASSED      [ 16%]
# examples/test_counter_model.py::CounterModel::test_sequence_001 PASSED      [ 33%]
# examples/test_counter_model.py::CounterModel::test_sequence_002 PASSED      [ 50%]
# examples/test_counter_model.py::CounterModel::test_sequence_003 PASSED      [ 66%]
# examples/test_counter_model.py::CounterModel::test_sequence_004 PASSED      [ 83%]
# examples/test_counter_model.py::QuickCounterModel::test_sequence_000 PASSED [ 100%]
# ...
# ============= 11 passed in 0.82s =============
```

---

## Part 8: Testing the plugin itself

### File: `tests/test_discovery.py`

```python
"""Tests for pytest-pyosmo discovery mechanism"""

import pytest
from pathlib import Path


def test_discover_model_class(testdir):
    """Test that pytest discovers @pytest.model classes"""
    
    # Create a test file with a model
    testdir.makepyfile("""
        import pytest
        
        @pytest.model
        class SimpleModel:
            def before_test(self):
                pass
            
            def guard_step1(self):
                return True
            
            def step_step1(self):
                pass
    """)
    
    # Run pytest with --collect-only to just collect, don't run
    result = testdir.runpytest("--collect-only", "-q")
    
    # Should find the model
    assert "SimpleModel" in str(result.outlines)


def test_collect_multiple_models(testdir):
    """Test collecting multiple models from one file"""
    
    testdir.makepyfile("""
        import pytest
        
        @pytest.model
        class Model1:
            def guard_a(self): return True
            def step_a(self): pass
        
        @pytest.model
        class Model2:
            def guard_b(self): return True
            def step_b(self): pass
    """)
    
    result = testdir.runpytest("--collect-only", "-q")
    
    assert "Model1" in str(result.outlines)
    assert "Model2" in str(result.outlines)


def test_marker_filtering(testdir):
    """Test that pytest markers work for filtering"""
    
    testdir.makepyfile("""
        import pytest
        
        @pytest.mark.quick
        @pytest.model
        class QuickModel:
            def guard_x(self): return True
            def step_x(self): pass
        
        @pytest.mark.comprehensive
        @pytest.model
        class ComprehensiveModel:
            def guard_y(self): return True
            def step_y(self): pass
    """)
    
    # Run only quick models
    result = testdir.runpytest("-m", "quick", "-v")
    
    # QuickModel should run
    assert "QuickModel" in str(result.outlines)
    # ComprehensiveModel should NOT run
    assert "ComprehensiveModel" not in str(result.outlines)


def test_regular_tests_still_work(testdir):
    """Test that regular pytest tests still work alongside models"""
    
    testdir.makepyfile("""
        import pytest
        
        def test_regular():
            assert 1 + 1 == 2
        
        @pytest.model
        class MyModel:
            def guard_x(self): return True
            def step_x(self): pass
    """)
    
    result = testdir.runpytest("-v")
    
    # Both regular test and model tests should run
    assert "test_regular PASSED" in str(result.outlines)
    assert "MyModel" in str(result.outlines)
```

### File: `tests/test_execution.py`

```python
"""Tests for model test execution"""

import pytest


def test_model_execution(testdir):
    """Test that generated model tests actually execute"""
    
    testdir.makepyfile("""
        import pytest
        
        @pytest.model
        class CounterModel:
            def __init__(self):
                self.value = 0
            
            def before_test(self):
                self.value = 0
            
            def guard_inc(self):
                return True
            
            def step_inc(self):
                self.value += 1
                assert self.value > 0
    """)
    
    result = testdir.runpytest("-v")
    
    # Tests should pass
    assert result.ret == 0
    assert "passed" in str(result.outlines).lower()


def test_model_test_failure(testdir):
    """Test that failed assertions in model steps are caught"""
    
    testdir.makepyfile("""
        import pytest
        
        @pytest.model
        class FailingModel:
            def guard_fail(self):
                return True
            
            def step_fail(self):
                assert False, "Intentional failure"
    """)
    
    result = testdir.runpytest("-v")
    
    # Tests should fail
    assert result.ret != 0
    assert "FAILED" in str(result.outlines)


def test_before_test_called(testdir):
    """Test that before_test is called before each sequence"""
    
    testdir.makepyfile("""
        import pytest
        
        @pytest.model
        class ResetModel:
            def __init__(self):
                self.setup_called = False
                self.value = 0
            
            def before_test(self):
                self.setup_called = True
                self.value = 0
            
            def guard_step(self):
                return True
            
            def step_step(self):
                # This should only pass if before_test was called
                assert self.setup_called
                assert self.value == 0
    """)
    
    result = testdir.runpytest("-v")
    
    # Should pass (before_test was called)
    assert result.ret == 0
```

---

## Part 9: Installation and usage

### Step 1: Install the plugin

```bash
# From source
git clone https://github.com/osmo-tool/pytest-pyosmo
cd pytest-pyosmo
pip install -e .

# Or from PyPI (once published)
pip install pytest-pyosmo
```

### Step 2: Create a model

```python
# tests/models/test_my_model.py
import pytest

@pytest.model
class MyModel:
    def __init__(self):
        self.state = "initial"
    
    def before_test(self):
        self.state = "initial"
    
    def guard_transition(self):
        return self.state == "initial"
    
    def step_transition(self):
        self.state = "done"
        assert self.state == "done"
```

### Step 3: Run it

```bash
# Run all models
pytest tests/models -v

# Run quick models only
pytest tests/models -m quick -v

# Run with coverage
pytest tests/models --cov=myapp --cov-report=html

# Run in parallel
pytest tests/models -n auto
```

---

## Part 10: How it works - deep dive

### The flow:

```
1. pytest starts
   ↓
2. Pytest loads plugins via entry_points
   → Loads pytest_pyosmo.plugin
   ↓
3. pytest_configure() runs
   → Registers markers (quick, comprehensive, stress, model)
   ↓
4. pytest scans test files
   → Calls pytest_collect_file() for each .py file
   ↓
5. Our plugin checks: "Does this file have @pytest.model?"
   → If yes, returns ModelModule collector
   ↓
6. ModelModule.collect() runs
   → Finds all @pytest.model classes
   → Returns ModelCollector for each
   ↓
7. ModelCollector.collect() runs
   → Instantiates model
   → Runs pyosmo to generate sequences
   → Returns ModelTestItem for each sequence
   ↓
8. pytest executes each ModelTestItem
   → Instantiates model
   → Calls before_test()
   → Executes each step in sequence
   → Captures any assertion failures
   ↓
9. pytest reports results
   → Shows pass/fail for each test sequence
```

### Key insight:

The pytest plugin API is designed exactly for this. We're not hacking or monkey-patching—we're using pytest's extension points:

- `pytest_configure` - Register markers
- `pytest_collect_file` - Decide which files to process
- `pytest.Collector` - Organize test items
- `pytest.Item` - Define executable tests

This is the same API that pytest-asyncio, pytest-django, pytest-cov all use.

---

## Part 11: Advanced features (phase 2)

### Fixture injection (Phase 2)

```python
# pytest_pyosmo/fixtures.py

import inspect
from typing import Dict, Any


def inject_fixtures_into_model(model_class, request):
    """
    Inspect model __init__ signature and inject matching fixtures.
    """
    sig = inspect.signature(model_class.__init__)
    fixtures = {}
    
    for param_name in sig.parameters:
        if param_name == "self":
            continue
        
        # Try to get this fixture from pytest
        try:
            fixture_value = request.getfixturevalue(param_name)
            fixtures[param_name] = fixture_value
        except pytest.FixtureLookupError:
            # Fixture doesn't exist, that's ok - param is required arg
            pass
    
    return fixtures
```

Then in ModelCollector.collect():

```python
def collect(self):
    fixtures = inject_fixtures_into_model(self.obj, self.request)
    model = self.obj(**fixtures)
    # ... rest of collection
```

This requires storing `self.request` in ModelCollector, which is available.

---

## Part 12: Troubleshooting

### Problem: Models not discovered

```bash
# Check what pytest sees
pytest --collect-only -q

# Ensure file name starts with test_
# Ensure class has @pytest.model decorator
# Ensure model has at least one guard_* / step_* pair
```

### Problem: "Cannot instantiate model"

```python
# Your model __init__ might be expecting fixtures
@pytest.fixture
def my_fixture():
    return "value"

@pytest.model
class MyModel:
    def __init__(self, my_fixture):  # ← This fixture will be injected
        self.value = my_fixture
```

### Problem: Tests fail inconsistently

```python
# Check your before_test() fully resets state
def before_test(self):
    self.counter = 0  # ← Make sure to reset EVERYTHING
    self.cache.clear()
    self.connection.reset()

# Use seed for reproducibility
# Same seed = same sequence generated
```

---

## Summary

The plugin works by:

1. **Discovering**: Scanning test files for `@pytest.model` classes
2. **Collecting**: Instantiating each model and using pyosmo to generate sequences
3. **Organizing**: Creating a ModelTestItem for each sequence
4. **Executing**: Running each sequence through pytest's normal test execution
5. **Reporting**: Showing results like normal pytest tests

The key advantage: **It looks and feels like normal pytest.** Users don't need to learn new commands, new tools, or new workflows. They just write a model class and run `pytest`.

This is exactly why pytest won the Python testing market—it got out of the way and let developers focus on testing, not on using the tool.

pytest-pyosmo should do the same for model-based testing.
