"""
pytest-pyosmo: Model-based testing discovery for pytest

This is a complete, working pytest plugin that discovers @pytest.model classes
and generates tests from them using pyosmo.

Installation:
    pip install pytest pyosmo

Usage:
    pytest tests/ -v
    pytest tests/ -m quick
    pytest tests/ --collect-only
"""

import inspect
from typing import Any

import pytest
from _pytest.nodes import Collector, Item
from _pytest.outcomes import Failed
from _pytest.python import Module

# ============================================================================
# STEP 1: Plugin Discovery - Make pytest load us
# ============================================================================


def pytest_configure(config):
    """Called when pytest starts - register markers"""
    config.addinivalue_line(
        'markers',
        'model: mark test as a model-based test',
    )
    config.addinivalue_line(
        'markers',
        'quick: quick model run (smoke test)',
    )
    config.addinivalue_line(
        'markers',
        'comprehensive: comprehensive model run',
    )
    config.addinivalue_line(
        'markers',
        'stress: extended stress test',
    )

    # Add pytest.model as an alias for pytest.mark.model
    # This allows users to use @pytest.model decorator
    if not hasattr(pytest, 'model'):
        pytest.model = pytest.mark.model

    print('[pytest-pyosmo] Plugin loaded and configured')


# ============================================================================
# STEP 2: File Collection - Find files with models
# ============================================================================


def pytest_collect_file(parent, file_path):
    """
    Pytest hook called for each file during collection.

    We look for files containing @pytest.model decorated classes.
    """
    # Only process test_*.py files
    if not file_path.name.startswith('test_'):
        return None

    if file_path.suffix != '.py':
        return None

    # Try to import the module
    try:
        module = _import_module(file_path)
    except Exception as e:
        print(f'[pytest-pyosmo] Failed to import {file_path}: {e}')
        return None

    # Check if module has @pytest.model classes
    if not _has_model_classes(module):
        return None

    # Return our custom collector
    print(f'[pytest-pyosmo] Found models in {file_path.name}')
    return ModelModule.from_parent(parent, path=file_path)


def _import_module(path):
    """Import a Python module from file path"""
    import importlib.util

    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(f'Cannot load {path}')

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _has_model_classes(module) -> bool:
    """Check if module contains @pytest.model classes"""
    return any(_has_pytest_model_marker(obj) for name, obj in inspect.getmembers(module, inspect.isclass))


def _has_pytest_model_marker(obj: Any) -> bool:
    """Check if class has @pytest.model decorator"""
    # Pytest stores marks in pytestmark attribute
    if not hasattr(obj, 'pytestmark'):
        return False

    marks = obj.pytestmark if isinstance(obj.pytestmark, list) else [obj.pytestmark]

    for mark in marks:
        # Check both .mark.name and .name (different pytest versions)
        mark_name = None
        if hasattr(mark, 'mark') and hasattr(mark.mark, 'name'):
            mark_name = mark.mark.name
        elif hasattr(mark, 'name'):
            mark_name = mark.name

        if mark_name == 'model':
            return True

    return False


# ============================================================================
# STEP 3: Model Collection - Find models in file
# ============================================================================


class ModelModule(Module):
    """
    Custom module collector for files containing @pytest.model classes.

    This extends pytest's Module to discover model classes.
    """

    def collect(self):
        """Discover model classes in this module"""
        # First call parent to collect normal tests/fixtures
        yield from super().collect()

        # Then find @pytest.model classes
        for name, obj in inspect.getmembers(self.obj, inspect.isclass):
            if _has_pytest_model_marker(obj):
                print(f'[pytest-pyosmo] Collecting model: {name}')
                yield ModelCollector.from_parent(
                    self,
                    name=name,
                    obj=obj,
                )


# ============================================================================
# STEP 4: Generate Tests - Create test items from model
# ============================================================================


class ModelCollector(Collector):
    """
    Collector for a single @pytest.model class.

    Responsible for:
    1. Instantiating the model
    2. Generating test sequences via pyosmo
    3. Creating test items for each sequence
    """

    def __init__(self, name, parent, obj):
        super().__init__(name, parent)
        self.obj = obj  # The @pytest.model class

    def collect(self):
        """Generate test items from pyosmo sequences"""
        try:
            import pyosmo
        except ImportError:
            yield SkipCollectionItem.from_parent(
                self,
                name='skip_pyosmo_not_installed',
                reason='pyosmo not installed',
            )
            return

        # Get configuration based on markers
        config = _get_model_config(self.obj)
        print(f'[pytest-pyosmo] Generating {config["num_tests"]} tests for {self.obj.__name__}')

        # Try to instantiate model
        try:
            model = self.obj()
        except Exception as e:
            yield ModelError.from_parent(
                self,
                name='model_instantiation_error',
                error=f'Cannot instantiate {self.obj.__name__}: {e}',
            )
            return

        # Generate sequences
        try:
            osmo = pyosmo.Osmo(model)
            osmo.test_end_condition = config['test_end_condition']
            osmo.test_suite_end_condition = config['test_suite_end_condition']
            osmo.seed = config['seed']

            # Generate test sequences
            osmo.generate()

            # Extract sequences from history
            sequences = []
            for test_case in osmo.history.test_cases:
                sequence = [step_log.name for step_log in test_case.steps_log]
                sequences.append(sequence)
        except Exception as e:
            yield ModelError.from_parent(
                self,
                name='model_generation_error',
                error=f'Cannot generate tests: {e}',
            )
            return

        # Create test item for each sequence
        for seq_num, sequence in enumerate(sequences):
            yield ModelTestItem.from_parent(
                self,
                name=f'test_sequence_{seq_num:03d}',
                sequence=sequence,
                model_class=self.obj,
                seq_num=seq_num,
            )


# ============================================================================
# STEP 5: Test Execution - Run generated test
# ============================================================================


class ModelTestItem(Item):
    """
    A single generated test sequence.

    This is what pytest executes - contains the sequence of steps.
    """

    def __init__(self, name, parent, sequence, model_class, seq_num):
        super().__init__(name, parent)
        self.sequence = sequence  # ["step_login", "step_add_item", ...]
        self.model_class = model_class
        self.seq_num = seq_num

        # Copy markers from model class to test item
        if hasattr(model_class, 'pytestmark'):
            marks = model_class.pytestmark
            if not isinstance(marks, list):
                marks = [marks]
            for mark in marks:
                # Skip the 'model' marker itself
                mark_name = getattr(mark, 'name', None)
                if mark_name and mark_name != 'model':
                    # Use the marker name directly to avoid structure issues
                    self.add_marker(mark_name)

    def runtest(self):
        """Execute the test sequence"""
        # Create fresh model instance
        model = self.model_class()

        # Call before_test if exists
        if hasattr(model, 'before_test'):
            model.before_test()

        # Execute each step
        for step_name in self.sequence:
            if not hasattr(model, step_name):
                raise AttributeError(f'{self.model_class.__name__} missing {step_name}')

            step_method = getattr(model, step_name)
            try:
                step_method()
            except Exception as e:
                # Add context about which step failed
                raise Failed(
                    f"Step '{step_name}' failed in sequence {self.seq_num}\n"
                    f'Sequence: {" → ".join(self.sequence)}\n'
                    f'Error: {e}'
                ) from e

    def repr_failure(self, excinfo):
        """Nice error message showing the full sequence"""
        seq_str = ' → '.join(self.sequence)
        return f'\nModel: {self.model_class.__name__}\nSequence {self.seq_num}: {seq_str}\nError: {excinfo.value}'


# ============================================================================
# STEP 6: Error Handling
# ============================================================================


class ModelError(Item):
    """Represents an error during model collection or generation"""

    def __init__(self, name, parent, error):
        super().__init__(name, parent)
        self.error = error

    def runtest(self):
        raise Failed(self.error)


class SkipCollectionItem(Item):
    """Item that should be skipped"""

    def __init__(self, name, parent, reason):
        super().__init__(name, parent)
        self.reason = reason

    def runtest(self):
        pytest.skip(self.reason)


# ============================================================================
# STEP 7: Configuration Management
# ============================================================================


def _get_model_config(model_class) -> dict[str, Any]:
    """
    Get test generation config based on markers.

    Default: moderate testing
    @pytest.mark.quick: fast smoke test
    @pytest.mark.comprehensive: full coverage
    @pytest.mark.stress: extended test
    """
    import pyosmo

    # Default config
    config = {
        'test_end_condition': pyosmo.end_conditions.Length(50),
        'test_suite_end_condition': pyosmo.end_conditions.Length(5),
        'seed': 42,
        'num_tests': 5,
    }

    # Check markers
    if hasattr(model_class, 'pytestmark'):
        marks = model_class.pytestmark
        if not isinstance(marks, list):
            marks = [marks]

        for mark in marks:
            mark_name = getattr(mark, 'name', None)

            if mark_name == 'quick':
                config.update(
                    {
                        'test_end_condition': pyosmo.end_conditions.Length(20),
                        'test_suite_end_condition': pyosmo.end_conditions.Length(2),
                        'num_tests': 2,
                    }
                )
            elif mark_name == 'comprehensive':
                config.update(
                    {
                        'test_end_condition': pyosmo.end_conditions.Length(100),
                        'test_suite_end_condition': pyosmo.end_conditions.StepCoverage(100),
                        'num_tests': 10,
                    }
                )
            elif mark_name == 'stress':
                config.update(
                    {
                        'test_end_condition': pyosmo.end_conditions.Length(500),
                        'test_suite_end_condition': pyosmo.end_conditions.Length(50),
                        'num_tests': 50,
                    }
                )

    return config


# ============================================================================
# STEP 8: Plugin Registration
# ============================================================================

# This makes pytest load our plugin
pytest_plugins = [__name__]


if __name__ == '__main__':
    print('pytest-pyosmo plugin module')
    print('Install with: pip install -e .')
    print('Or copy to your conftest.py')
