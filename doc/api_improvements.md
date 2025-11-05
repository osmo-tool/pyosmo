# API Improvements for PyOsmo

## Overview

This document proposes concrete API improvements for pyosmo to enhance usability, maintainability, and developer experience. All proposals maintain backward compatibility where possible or provide clear migration paths.

---

## Table of Contents

1. [Decorator-Based API](#1-decorator-based-api)
2. [Requirements System](#2-requirements-system)
3. [Coverage Tracking](#3-coverage-tracking)
4. [Reporting API](#4-reporting-api)
5. [Configuration API](#5-configuration-api)
6. [History & Statistics API](#6-history--statistics-api)
7. [Model Validation API](#7-model-validation-api)
8. [Error Handling Improvements](#8-error-handling-improvements)
9. [CLI Improvements](#9-cli-improvements)

---

## 1. Decorator-Based API

### Rationale
While naming conventions (step_*, guard_*) work, decorators provide:
- Better IDE autocomplete and validation
- Explicit declaration of intent
- Metadata attachment (requirements, weights, etc.)
- Runtime validation capabilities

### Current State
```python
class Model:
    def step_login(self): pass
    def guard_login(self): return True
    def weight_login(self): return 10
```

### Proposed Decorator API (Optional, Coexists with Naming Convention)

#### 2.1 Core Decorators

```python
from pyosmo.decorators import step, guard, weight, pre, post

class Model:
    @step("login")  # Explicit step name
    @guard(lambda self: not self.logged_in)  # Inline guard
    @weight(10)  # Constant weight
    def user_login(self):  # Method name doesn't need prefix
        """Log in the user."""
        self.logged_in = True

    @step
    def logout(self):  # Name inferred from method name
        """Log out the user."""
        self.logged_in = False

    @guard("logout")  # Attach guard to specific step
    def must_be_logged_in(self) -> bool:
        return self.logged_in

    @pre("login")  # Pre-step hook
    def before_login(self):
        print("About to log in")

    @post("login")  # Post-step hook
    def after_login(self):
        print("Logged in successfully")
```

#### 2.2 Metadata Decorators

```python
from pyosmo.decorators import requires, variable, state

class ShoppingModel:
    @step
    @requires("REQ-101", "REQ-102")  # Requirements traceability
    def checkout(self):
        """Complete checkout process."""
        pass

    @step
    @variable("cart_size", categories=["empty", "small", "large"])
    def add_to_cart(self):
        """Add item to cart."""
        self.cart.append(Item())

    @state  # Mark as state-providing function
    def get_state(self) -> str:
        """Return current model state."""
        return f"cart={len(self.cart)},user={self.user_id}"
```

#### 2.3 Decorator Implementation

```python
# pyosmo/decorators.py enhancements
from functools import wraps
from typing import Callable, Optional, List, Union

class StepDecorator:
    """Decorator for marking test steps."""

    def __init__(
        self,
        name: Optional[str] = None,
        *,
        weight: Optional[Union[int, float]] = None,
        enabled: bool = True
    ):
        self.name = name
        self.weight = weight
        self.enabled = enabled

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Attach metadata
        wrapper._osmo_step = True
        wrapper._osmo_step_name = self.name or func.__name__
        wrapper._osmo_weight = self.weight
        wrapper._osmo_enabled = self.enabled

        return wrapper

def step(
    name_or_func: Optional[Union[str, Callable]] = None,
    *,
    weight: Optional[Union[int, float]] = None,
    enabled: bool = True
) -> Union[Callable, StepDecorator]:
    """Mark a method as a test step.

    Can be used with or without arguments:

        @step
        def my_step(self): pass

        @step("custom_name")
        def my_step(self): pass

        @step(weight=10, enabled=False)
        def my_step(self): pass

    Args:
        name_or_func: Step name or function (for no-arg usage)
        weight: Static weight for this step
        enabled: Whether step is enabled

    Returns:
        Decorated function or decorator
    """
    if callable(name_or_func):
        # Used without arguments: @step
        return StepDecorator()(name_or_func)
    else:
        # Used with arguments: @step("name")
        return StepDecorator(name_or_func, weight=weight, enabled=enabled)


def guard(
    step_name_or_func: Union[str, Callable],
    *,
    invert: bool = False
) -> Callable:
    """Mark a method as a guard for a step.

    Can be used as inline lambda or separate method:

        @step
        @guard(lambda self: self.ready)
        def process(self): pass

        @guard("process")
        def can_process(self) -> bool:
            return self.ready

    Args:
        step_name_or_func: Step name or guard function
        invert: Invert guard logic (step enabled when False)

    Returns:
        Decorated function
    """
    if callable(step_name_or_func):
        # Inline guard
        func = step_name_or_func
        func._osmo_guard_inline = True
        func._osmo_guard_invert = invert
        return func
    else:
        # Named guard
        def decorator(func: Callable) -> Callable:
            func._osmo_guard = True
            func._osmo_guard_for = step_name_or_func
            func._osmo_guard_invert = invert
            return func
        return decorator
```

#### 2.4 Backward Compatibility

```python
# pyosmo/model.py - Enhanced to support both styles
class OsmoModelCollector:
    def _discover_steps(self, model: object) -> List[TestStep]:
        """Discover steps using both naming convention and decorators."""
        steps = []

        for name in dir(model):
            method = getattr(model, name)

            # Check decorator-based steps
            if hasattr(method, '_osmo_step'):
                step_name = method._osmo_step_name
                steps.append(self._create_step_from_decorator(model, method, step_name))

            # Check naming convention (backward compatible)
            elif name.startswith('step_'):
                step_name = name[5:]  # Remove 'step_' prefix
                steps.append(self._create_step_from_naming(model, method, step_name))

        return steps
```

**Implementation Priority**: P2 (Phase 2, Week 4-5)

---

## 2. Requirements System

### Proposed API

```python
from pyosmo.requirements import Requirement, RequirementManager

# Define requirements
class Requirements:
    LOGIN = Requirement("REQ-001", "User must be able to log in")
    LOGOUT = Requirement("REQ-002", "User must be able to log out")
    CHECKOUT = Requirement("REQ-003", "User must complete checkout")
    PAYMENT = Requirement("REQ-004", "User must process payment")

# Use in model
from pyosmo.decorators import requires, requires_all, requires_any

class Model:
    @step
    @requires(Requirements.LOGIN)
    def step_login(self):
        pass

    @step
    @requires_all(Requirements.CHECKOUT, Requirements.PAYMENT)
    def step_complete_order(self):
        """Satisfies both checkout and payment requirements."""
        pass

    @step
    @requires_any(Requirements.LOGIN, Requirements.LOGOUT)
    def step_check_auth(self):
        """Satisfies either login or logout requirement."""
        pass

# Track coverage
osmo = Osmo(Model())
osmo.run()

print(osmo.history.requirement_coverage)
# Output: {
#   'REQ-001': 5,   # Covered 5 times
#   'REQ-002': 0,   # Not covered
#   'REQ-003': 3,
#   'REQ-004': 3
# }

# End condition based on requirements
from pyosmo.end_conditions import RequirementCoverage

osmo.test_end_condition = RequirementCoverage(
    requirements=[Requirements.LOGIN, Requirements.CHECKOUT],
    min_coverage=2  # Each requirement covered at least 2 times
)
```

### Implementation

```python
# pyosmo/requirements.py (NEW)
from dataclasses import dataclass
from typing import Set, Dict, Optional

@dataclass(frozen=True)
class Requirement:
    """Represents a testable requirement."""

    id: str
    description: str
    priority: str = "medium"  # high, medium, low
    category: Optional[str] = None

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return f"{self.id}: {self.description}"


class RequirementManager:
    """Manages requirement tracking and coverage."""

    def __init__(self):
        self._requirements: Dict[str, Requirement] = {}
        self._coverage: Dict[str, int] = {}
        self._step_requirements: Dict[str, Set[Requirement]] = {}

    def register(self, requirement: Requirement) -> None:
        """Register a requirement for tracking."""
        self._requirements[requirement.id] = requirement
        self._coverage[requirement.id] = 0

    def mark_covered(self, requirement: Requirement) -> None:
        """Mark a requirement as covered once."""
        if requirement.id not in self._coverage:
            self.register(requirement)
        self._coverage[requirement.id] += 1

    def get_coverage(self) -> Dict[str, int]:
        """Get coverage counts for all requirements."""
        return self._coverage.copy()

    def get_uncovered(self) -> Set[Requirement]:
        """Get requirements with zero coverage."""
        return {
            req for req_id, req in self._requirements.items()
            if self._coverage.get(req_id, 0) == 0
        }

    def coverage_percentage(self) -> float:
        """Get percentage of requirements covered at least once."""
        if not self._requirements:
            return 100.0
        covered = sum(1 for count in self._coverage.values() if count > 0)
        return (covered / len(self._requirements)) * 100
```

**Implementation Priority**: P1 (Phase 2, Week 4-6)

---

## 3. Coverage Tracking

### 4.1 State Coverage

```python
from pyosmo.decorators import state

class Model:
    @state
    def get_state(self) -> str:
        """Return unique state identifier."""
        return f"logged_in={self.logged_in},cart_size={len(self.cart)}"

# Access state coverage
osmo.run()
print(f"Unique states visited: {len(osmo.history.states_visited)}")
print(f"States: {osmo.history.states_visited}")

# End condition
from pyosmo.end_conditions import StateCoverage
osmo.test_end_condition = StateCoverage(
    min_states=10,  # Visit at least 10 unique states
    min_percentage=80  # Or cover 80% of observed states
)
```

### 4.2 Variable Coverage

```python
from pyosmo.decorators import variable

class Model:
    @variable("input_size", categories=["empty", "small", "medium", "large"])
    def get_input_size(self) -> str:
        if len(self.data) == 0:
            return "empty"
        elif len(self.data) < 10:
            return "small"
        elif len(self.data) < 100:
            return "medium"
        else:
            return "large"

    @variable("user_type")  # No categories - track all observed values
    def get_user_type(self) -> str:
        return self.current_user.type

# Access variable coverage
osmo.run()
print(osmo.history.variable_coverage)
# Output: {
#   'input_size': {'empty': 5, 'small': 10, 'medium': 3, 'large': 1},
#   'user_type': {'admin': 2, 'regular': 15, 'guest': 8}
# }
```

### 4.3 Step-Pair Coverage

```python
# Automatically tracked
osmo.run()
print(f"Step pairs executed: {len(osmo.history.step_pairs)}")
print(osmo.history.step_pairs)
# Output: {
#   ('login', 'browse'): 5,
#   ('browse', 'add_to_cart'): 10,
#   ('add_to_cart', 'checkout'): 3,
#   ...
# }

# End condition
from pyosmo.end_conditions import StepPairCoverage
osmo.test_end_condition = StepPairCoverage(percentage=90)
```

**Implementation Priority**: P1 (Phase 2, Week 6-8)

---

## 4. Reporting API

### Proposed Unified Reporting Interface

```python
from pyosmo.reporting import Reporter, Format

# Simple API
osmo = Osmo(model)
osmo.run()

# Single format
osmo.save_report("report.html", format=Format.HTML)
osmo.save_report("report.json", format=Format.JSON)
osmo.save_report("results.xml", format=Format.JUNIT)

# Multiple formats at once
osmo.save_reports(
    "reports/test_run",
    formats=[Format.HTML, Format.JSON, Format.JUNIT, Format.MARKDOWN]
)
# Creates:
#   reports/test_run.html
#   reports/test_run.json
#   reports/test_run.xml
#   reports/test_run.md
```

### Advanced Reporting Configuration

```python
from pyosmo.reporting import HTMLReporter, ReportConfig

config = ReportConfig(
    title="E-Commerce Test Suite",
    include_charts=True,
    include_timeline=True,
    include_statistics=True,
    theme="dark",  # or "light"
    custom_css="path/to/custom.css"
)

reporter = HTMLReporter(osmo.history, config)
reporter.save("report.html")
reporter.serve(port=8080)  # Launch local web server to view
```

### Programmatic Report Access

```python
from pyosmo.reporting import JSONReporter

reporter = JSONReporter(osmo.history)
data = reporter.to_dict()

# Access structured data
print(f"Total steps: {data['summary']['total_steps']}")
print(f"Duration: {data['summary']['duration']}")
print(f"Coverage: {data['coverage']['step_coverage']}%")

# Export for external analysis
import pandas as pd
df = pd.DataFrame(data['steps'])
df.to_csv("analysis.csv")
```

### Implementation

```python
# pyosmo/reporting/__init__.py (NEW MODULE)
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, List
from pathlib import Path

class Format(Enum):
    HTML = "html"
    JSON = "json"
    JUNIT = "junit"
    MARKDOWN = "md"
    CSV = "csv"


class Reporter(ABC):
    """Base class for all reporters."""

    def __init__(self, history: OsmoHistory):
        self.history = history

    @abstractmethod
    def generate(self) -> str:
        """Generate report content."""
        ...

    def save(self, path: Path) -> None:
        """Save report to file."""
        content = self.generate()
        Path(path).write_text(content)


class HTMLReporter(Reporter):
    """Generate HTML test report with interactive visualizations."""

    def __init__(self, history: OsmoHistory, config: Optional[ReportConfig] = None):
        super().__init__(history)
        self.config = config or ReportConfig()

    def generate(self) -> str:
        """Generate HTML report using Jinja2 template."""
        from jinja2 import Environment, PackageLoader

        env = Environment(loader=PackageLoader('pyosmo', 'templates'))
        template = env.get_template('report.html')

        return template.render(
            history=self.history,
            config=self.config,
            summary=self._generate_summary(),
            charts=self._generate_charts() if self.config.include_charts else None
        )

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        return {
            'total_tests': len(self.history.tests),
            'total_steps': sum(len(test.steps) for test in self.history.tests),
            'duration': self.history.duration,
            'step_coverage': self.history.step_coverage_percentage(),
            'pass_rate': self.history.pass_rate(),
        }

    def _generate_charts(self) -> Dict[str, str]:
        """Generate Chart.js compatible data."""
        return {
            'step_frequency': self._step_frequency_chart(),
            'execution_timeline': self._timeline_chart(),
            'coverage_progress': self._coverage_chart(),
        }
```

**Implementation Priority**: P1 (Phase 2, Week 8-9)

---

## 5. Configuration API

### Current Issues
- Verbose configuration
- No validation
- No presets
- Hard to discover options

### Proposed Improvements

#### 6.1 Fluent Configuration API

```python
# Current
osmo = Osmo(model)
osmo.seed = 12345
osmo.algorithm = RandomAlgorithm()
osmo.test_end_condition = Length(100)
osmo.test_suite_end_condition = Length(5)
osmo.error_strategy = AlwaysRaise()

# Proposed fluent API
osmo = (Osmo(model)
    .with_seed(12345)
    .with_algorithm(RandomAlgorithm())
    .with_test_end_condition(Length(100))
    .with_suite_end_condition(Length(5))
    .on_error(AlwaysRaise())
    .build())

# Or even more fluent
osmo = (Osmo(model)
    .random_algorithm(seed=12345)
    .stop_after_steps(100)
    .run_tests(5)
    .raise_on_error()
    .build())
```

#### 6.2 Configuration Presets

```python
from pyosmo.presets import smoke_test, regression_test, long_running_test, exploration_test

# Smoke test: Quick validation
osmo = Osmo(model).use_preset(smoke_test(steps=50, tests=3))

# Regression test: Full coverage, deterministic
osmo = Osmo(model).use_preset(regression_test(seed=12345, coverage=100))

# Long-running: Stress test
osmo = Osmo(model).use_preset(long_running_test(hours=10))

# Exploration: Find edge cases
osmo = Osmo(model).use_preset(exploration_test(max_diversity=True))
```

#### 6.3 Configuration Validation

```python
from pyosmo.config import OsmoConfig

config = OsmoConfig()
config.seed = "invalid"  # Should be int

# Raises: ConfigurationError: seed must be an integer, got str
```

#### 6.4 Configuration Serialization

```python
# Save configuration
osmo = Osmo(model).random_algorithm(seed=12345).stop_after_steps(100)
osmo.save_config("config.json")

# Load configuration
osmo = Osmo(model).load_config("config.json")
osmo.run()
```

**Implementation Priority**: P2 (Phase 2, Week 9-10)

---

## 6. History & Statistics API

### Current Issues
- Statistics returned as formatted strings
- Hard to use programmatically
- Limited metrics

### Proposed Improvements

#### 7.1 Structured Statistics

```python
# Current
print(osmo.history.step_stats())  # Returns formatted string

# Proposed
stats = osmo.history.statistics()
print(stats.total_steps)  # 1543
print(stats.unique_steps)  # 12
print(stats.most_executed_step)  # 'browse'
print(stats.least_executed_step)  # 'checkout'
print(stats.average_steps_per_test)  # 308.6
print(stats.step_execution_times)  # {'login': 0.5s, 'browse': 0.1s, ...}

# Export for analysis
import json
with open('stats.json', 'w') as f:
    json.dump(stats.to_dict(), f, indent=2)
```

#### 7.2 Test Case Access

```python
# Access individual test cases
for test_case in osmo.history.test_cases:
    print(f"Test {test_case.index}:")
    print(f"  Steps: {len(test_case.steps)}")
    print(f"  Duration: {test_case.duration}")
    print(f"  Status: {test_case.status}")  # PASS, FAIL, ERROR
    print(f"  Sequence: {test_case.step_names}")

# Failed tests only
failed_tests = osmo.history.failed_tests()
for test in failed_tests:
    print(f"Failed at step: {test.failed_step}")
    print(f"Error: {test.error}")
    print(f"Traceback: {test.traceback}")
```

#### 7.3 Advanced Metrics

```python
# Coverage progression over time
coverage_timeline = osmo.history.coverage_timeline()
# Returns: [(step_index, coverage_percentage), ...]

# Step execution frequency
frequency = osmo.history.step_frequency()
# Returns: {'login': 45, 'browse': 120, 'checkout': 23, ...}

# Step transition matrix
transitions = osmo.history.transition_matrix()
# Returns: DataFrame-like structure showing step A -> step B frequencies

# Requirement coverage over time
req_timeline = osmo.history.requirement_coverage_timeline()
# Returns: [(step_index, {req_id: coverage_count}), ...]
```

**Implementation Priority**: P1 (Phase 2, Week 7)

---

## 7. Model Validation API

### Proposed Static Analysis

```python
from pyosmo.analysis import ModelValidator, ValidationLevel

# Basic validation
validator = ModelValidator(model)
report = validator.validate()

if report.has_errors():
    print("Model has errors:")
    for error in report.errors:
        print(f"  - {error}")
    exit(1)

if report.has_warnings():
    print("Model has warnings:")
    for warning in report.warnings:
        print(f"  - {warning}")

# Detailed validation
report = validator.validate(level=ValidationLevel.STRICT)
print(report.to_markdown())
```

### Validation Checks

```python
class ModelValidator:
    def validate(self) -> ValidationReport:
        """Run all validation checks."""
        report = ValidationReport()

        # Check 1: All steps have guards or explicit "always enabled"
        self._check_guarded_steps(report)

        # Check 2: No unreachable steps (guard always False)
        self._check_unreachable_steps(report)

        # Check 3: No infinite loops (step always re-enables itself)
        self._check_infinite_loops(report)

        # Check 4: Weights are valid
        self._check_weights(report)

        # Check 5: Decorator usage is correct
        self._check_decorators(report)

        # Check 6: Requirements are defined
        self._check_requirements(report)

        return report
```

### CLI Integration

```bash
# Validate model before running
pyosmo validate mymodel.py

# Output:
# ✓ Model structure is valid
# ✓ Found 15 steps
# ✓ Found 12 guards
# ⚠ Warning: step_checkout has no guard (always enabled)
# ⚠ Warning: step_delete is never reachable (guard_delete always returns False)
# ✗ Error: weight_search returns negative value (-5)
#
# Model validation FAILED (1 error, 2 warnings)
```

**Implementation Priority**: P1 (Phase 3, Week 10-11)

---

## 8. Error Handling Improvements

### Current Issues
- Bare `except:` clauses
- Generic error messages
- Limited error context

### Proposed Improvements

#### 9.1 Custom Exception Hierarchy

```python
# pyosmo/exceptions.py (ENHANCED)
class PyOsmoError(Exception):
    """Base exception for all pyosmo errors."""
    pass

class ModelError(PyOsmoError):
    """Base exception for model-related errors."""
    pass

class StepExecutionError(ModelError):
    """Error during step execution."""

    def __init__(self, step_name: str, original_error: Exception):
        self.step_name = step_name
        self.original_error = original_error
        super().__init__(
            f"Error executing step '{step_name}': {original_error}"
        )

class GuardEvaluationError(ModelError):
    """Error during guard evaluation."""

    def __init__(self, guard_name: str, original_error: Exception):
        self.guard_name = guard_name
        self.original_error = original_error
        super().__init__(
            f"Error evaluating guard '{guard_name}': {original_error}"
        )

class ConfigurationError(PyOsmoError):
    """Invalid configuration."""
    pass

class EndConditionError(PyOsmoError):
    """Error in end condition evaluation."""
    pass
```

#### 9.2 Rich Error Context

```python
class ErrorContext:
    """Captures full context when an error occurs."""

    step_name: str
    test_index: int
    step_index: int
    model_state: Dict[str, Any]  # Snapshot of model state
    history: List[str]  # Previous steps
    error: Exception
    traceback: str

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for reporting."""
        ...

    def save_reproduction_script(self, path: str) -> None:
        """Generate script to reproduce this exact error."""
        ...
```

#### 9.3 Improved Error Messages

```python
# Bad (current)
raise Exception("Error in step")

# Good (proposed)
raise StepExecutionError(
    step_name="checkout",
    original_error=e,
    context=ErrorContext(
        test_index=3,
        step_index=45,
        model_state=self._capture_state(),
        history=self.history.get_last_steps(10)
    )
)
```

**Implementation Priority**: P2 (Phase 3, Week 11)

---

## 9. CLI Improvements

### Current Issues
- Limited commands
- No validation command
- No report generation from CLI

### Proposed Enhanced CLI

```bash
# Run tests
pyosmo run model.py --tests 5 --steps 100 --seed 12345

# Validate model
pyosmo validate model.py --strict

# Generate report from history
pyosmo report history.json --format html --output report.html

# Replay saved sequence
pyosmo replay sequence.json --model model.py

# Analyze model
pyosmo analyze model.py --show-coverage --show-transitions

# Initialize new model from template
pyosmo init my_model.py --template basic

# List available algorithms/end conditions
pyosmo list algorithms
pyosmo list end-conditions
pyosmo list error-strategies
```

### Implementation

```python
# pyosmo/cli/__init__.py (NEW STRUCTURE)
import click
from typing import Optional

@click.group()
@click.version_option()
def cli():
    """PyOsmo - Model-Based Testing for Python"""
    pass

@cli.command()
@click.argument('model_file', type=click.Path(exists=True))
@click.option('--tests', '-t', type=int, default=1, help='Number of tests to run')
@click.option('--steps', '-s', type=int, default=100, help='Steps per test')
@click.option('--seed', type=int, help='Random seed for reproducibility')
@click.option('--algorithm', '-a', type=click.Choice(['random', 'balancing', 'weighted']), default='random')
@click.option('--report', '-r', type=click.Path(), help='Save report to file')
@click.option('--format', '-f', type=click.Choice(['html', 'json', 'junit']), default='html')
def run(model_file: str, tests: int, steps: int, seed: Optional[int], algorithm: str, report: Optional[str], format: str):
    """Run model-based tests."""
    # Implementation
    ...

@cli.command()
@click.argument('model_file', type=click.Path(exists=True))
@click.option('--strict', is_flag=True, help='Enable strict validation')
@click.option('--fix', is_flag=True, help='Auto-fix issues where possible')
def validate(model_file: str, strict: bool, fix: bool):
    """Validate model structure and configuration."""
    # Implementation
    ...
```

**Implementation Priority**: P2 (Phase 3, Week 12)

---

## Summary Table

| Improvement Area | Priority | Effort | Impact | Phase |
|------------------|----------|--------|--------|-------|
| Decorator API | P2 | 1 week | Medium | 2 |
| Requirements System | P1 | 2 weeks | High | 2 |
| Coverage Tracking | P1 | 2 weeks | High | 2 |
| Reporting API | P1 | 1 week | High | 2 |
| Configuration API | P2 | 1 week | Medium | 2 |
| History API | P1 | 3 days | Medium | 2 |
| Model Validation | P1 | 1 week | High | 3 |
| Error Handling | P2 | 3 days | Medium | 3 |
| CLI Improvements | P2 | 3 days | Medium | 3 |

**Total Estimated Effort**: 8-9 weeks

---

## Migration Guide

### For Existing Users

All improvements maintain backward compatibility:

1. **Decorators**: Optional, naming convention still works
2. **Requirements**: New feature, doesn't affect existing code
3. **Coverage**: Enhanced tracking, doesn't break existing code
4. **Reporting**: New API, old methods still work
5. **Configuration**: New fluent API alongside old property setting
6. **History**: Enhanced API, old methods deprecated with warnings
7. **CLI**: New commands, old usage still works

### Deprecation Timeline

- **v0.2**: Add deprecation warnings for old APIs
- **v0.3**: Mark deprecated APIs as legacy
- **v1.0**: Remove deprecated APIs (with migration guide)

---

*Document Version: 1.0*
*Last Updated: 2025-11-05*
*Next Review: Start of Phase 2*
