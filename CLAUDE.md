# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PyOsmo is a Model-Based Testing (MBT) framework for Python that generates test cases automatically from programmatic models. It uses pure Python as the modeling language (unlike traditional graphical MBT tools), enabling flexible modeling of complex system behaviors.

**Key Concepts:**
- **Steps**: Test actions (`step_*` methods or `@step` decorator)
- **Guards**: Preconditions that control step execution (`guard_*` methods or `@guard` decorator)
- **Weights**: Step selection probabilities (`weight_*` methods or `@weight` decorator)
- **Algorithms**: Step selection strategies (Random, Weighted, Balancing)
- **End Conditions**: Test termination criteria (Length, Time, StepCoverage, Endless)
- **Lifecycle Hooks**: `before_suite`, `before_test`, `before`, `after`, `after_test`, `after_suite`

## Development Commands

### Testing
```bash
# Run all tests
pytest pyosmo/tests/

# With coverage
pytest pyosmo/tests/ --cov=pyosmo

# Single test file
pytest pyosmo/tests/test_core.py

# Specific test
pytest pyosmo/tests/test_core.py::test_function_name

# Mutation testing
mutmut run
```

### Linting & Formatting
```bash
# Lint code (ruff is the primary linter)
ruff check pyosmo/

# Auto-fix issues
ruff check pyosmo/ --fix

# Format code
ruff format pyosmo/

# Check formatting without changes
ruff format --check pyosmo/

# Type checking
mypy pyosmo/
```

### Installation & Building
```bash
# Development install
pip install -e ".[dev]"

# Build package
python -m build

# Run CLI
pyosmo examples/calculator_example.py --algorithm weighted --test-len 100
```

### Publishing (NEW)
```bash
# Automated publishing workflow
make publish-patch     # Bump patch version (0.2.2 -> 0.2.3) and publish
make publish-minor     # Bump minor version (0.2.2 -> 0.3.0) and publish
make publish-major     # Bump major version (0.2.2 -> 1.0.0) and publish

# Just bump version (no publish)
make version-patch
make version-minor
make version-major

# Check if version exists on PyPI
make check-pypi
```

See [PUBLISHING.md](PUBLISHING.md) for detailed publishing instructions and troubleshooting.

## Architecture

### Core Components

**pyosmo/osmo.py** - Main entry point. The `Osmo` class orchestrates test generation:
- Accepts model instances
- Configures algorithms, end conditions, and error strategies
- Provides fluent API for configuration
- Executes test generation and tracks history

**pyosmo/model.py** - Model parser that discovers steps, guards, weights, and lifecycle hooks using:
1. Naming convention: `step_*`, `guard_*`, `weight_*` methods
2. Decorator-based: `@step`, `@guard`, `@weight`, `@pre`, `@post`, `@requires`

**pyosmo/config.py** - Configuration management using OsmoConfig class. Centralizes all test generation parameters.

### Plugin Architecture

**pyosmo/algorithm/** - Step selection strategies:
- `RandomAlgorithm`: Pure random selection
- `WeightedAlgorithm`: Weight-based random selection
- `BalancingAlgorithm`: Balances step execution to achieve coverage

**pyosmo/end_conditions/** - Test termination conditions:
- `Length(n)`: Stop after n steps
- `Time(seconds)`: Stop after elapsed time
- `StepCoverage(percentage)`: Stop when coverage threshold reached
- `And(*conditions)` / `Or(*conditions)`: Combine conditions
- `Endless()`: Run forever (online testing)

**pyosmo/error_strategy/** - Error handling:
- `AlwaysRaise`: Fail fast on any error
- `AlwaysIgnore`: Continue on all errors
- `IgnoreAssertions`: Ignore assertion errors only
- `AllowCount(n)`: Allow up to n errors

**pyosmo/history/** - Execution tracking:
- `History`: Main history tracker
- `TestCase`: Individual test case records
- `TestStepLog`: Step-level execution logs
- `Statistics`: Coverage and execution statistics

### Model Discovery

Models can define test logic using either approach:

**Naming Convention (classic):**
```python
class MyModel:
    def step_action_name(self):     # Test step
        pass

    def guard_action_name(self):    # Precondition
        return True

    def weight_action_name(self):   # Weight (default: 1)
        return 10

    def before_test(self):          # Setup
        pass
```

**Decorator-Based (modern):**
```python
from pyosmo import step, guard, weight

class MyModel:
    @step
    @guard(lambda self: self.ready)
    @weight(10)
    def action_name(self):
        pass
```

### Fluent Configuration API

Osmo supports method chaining for configuration:
```python
Osmo(MyModel())
    .random_algorithm(seed=42)
    .stop_after_steps(100)
    .run_tests(5)
    .raise_on_error()
    .generate()
```

## Code Style

- **Line length**: 120 characters
- **Python version**: 3.11+ (supports 3.11-3.14)
- **Linter**: Ruff (replaces flake8/black)
- **Quote style**: Double quotes
- **Type hints**: Encouraged for main code, not required for tests
- **Import sorting**: Handled by ruff (isort rules)

### Ruff Configuration
Key enabled rules: pycodestyle (E/W), pyflakes (F), isort (I), pep8-naming (N), pyupgrade (UP), bugbear (B), comprehensions (C4), simplify (SIM), return (RET)

Ignored rules:
- E501 (line too long - handled by formatter)
- B008 (function call in defaults)
- B904 (raise from in except)

## Testing Patterns

- Tests located in `pyosmo/tests/`
- Use pytest framework
- Hypothesis for property-based testing available
- Test coverage tracked via `--cov` flag
- Mutation testing with mutmut configured
- Per-file ignores: `__init__.py` allows unused imports, tests allow `assert False`

## CI/CD

GitHub Actions workflow (`.github/workflows/pr_check.yaml`):
- Tests on Python 3.11, 3.12, 3.13, 3.14
- Uses `uv` for fast dependency management
- Runs ruff linter and formatter checks
- Executes pytest suite

## Strategic Context

PyOsmo aims to become the leading open-source MBT tool for Python by:
- Emphasizing developer experience and pytest integration
- Using pure Python for modeling (vs. graphical tools)
- Supporting both offline (test generation) and online (real-time) testing
- Enabling long-running, regression, and exploratory testing

See `doc/strategic_vision_2025.md` for detailed roadmap and competitive analysis.

## Additional Tools

**model-creator/** - Autonomous website model generator that crawls websites and generates PyOsmo models automatically using BeautifulSoup4 and requests. See `model-creator/README.md` for usage.

## Common Development Workflow

1. Make changes to `pyosmo/` code
2. Run `ruff check pyosmo/ --fix` and `ruff format pyosmo/` to lint and format
3. Run `mypy pyosmo/` for type checking
4. Run `pytest pyosmo/tests/` to verify tests pass
5. Add/update tests in `pyosmo/tests/` for new functionality
6. Verify coverage with `pytest pyosmo/tests/ --cov=pyosmo`
