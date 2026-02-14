# Documentation Improvements for PyOsmo

## Overview

This document outlines a comprehensive plan to improve pyosmo documentation from its current incomplete state to professional, user-friendly documentation that drives adoption and reduces support burden.

---

## Current State Assessment

### Existing Documentation

| Document | Status | Completeness | Quality | Issues |
|----------|--------|--------------|---------|--------|
| README.md | ❌ Broken | 60% | Fair | Cuts off mid-sentence at line 161 |
| doc/development.md | ⚠️ Outdated | 70% | Fair | References deprecated tools (pylint, flake8) |
| doc/mbt_good_practises.md | ✅ Good | 80% | Good | Useful but not comprehensive |
| doc/towards_randomized_tests.md | ✅ Good | 90% | Good | Well-written progression guide |
| API Reference | ❌ Missing | 0% | N/A | No generated documentation |
| Tutorials | ⚠️ Basic | 40% | Fair | Only code examples, no walkthroughs |
| User Guide | ❌ Missing | 0% | N/A | No comprehensive guide |

**Overall Grade: D+** (Functional but unprofessional)

### Pain Points

1. **First Impression**: Broken README discourages new users
2. **Learning Curve**: No structured tutorials or learning path
3. **API Discovery**: Hard to find available features
4. **Best Practices**: Scattered across files
5. **Troubleshooting**: No centralized help
6. **Migration**: No guide for users coming from other tools

---

## Documentation Goals

### Primary Goals
1. **Complete README** - Professional first impression
2. **API Reference** - Complete, searchable documentation
3. **Tutorial Series** - Structured learning path from beginner to advanced
4. **User Guide** - Comprehensive reference
5. **Contributing Guide** - Lower barrier for contributors

### Success Metrics
- README completion: 100%
- API documentation: 90%+ of public API
- Tutorials: 5+ complete tutorials
- User guide: All major features covered
- Time to first successful test: < 30 minutes
- Support questions answered by docs: > 80%

---

## Phase 1: Critical Fixes (Week 1)

### 1.1 Complete README.md

**Current Issues**:
- Cuts off at line 161 during performance testing section
- Missing sections: Advanced Usage, Configuration, Troubleshooting
- No table of contents
- Missing badges

**Proposed Structure**:

```markdown
# PyOsmo

[![PyPI version](https://badge.fury.io/py/pyosmo.svg)](https://badge.fury.io/py/pyosmo)
[![Python versions](https://img.shields.io/pypi/pyversions/pyosmo.svg)](https://pypi.org/project/pyosmo/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Test code](https://github.com/OPpuolitaival/pyosmo/actions/workflows/pr_check.yaml/badge.svg)](https://github.com/OPpuolitaival/pyosmo/actions/workflows/pr_check.yaml)
[![Documentation](https://readthedocs.org/projects/pyosmo/badge/)](https://pyosmo.readthedocs.io/)

A powerful, flexible model-based testing (MBT) framework for Python.

## Table of Contents

- [What is Model-Based Testing?](#what-is-model-based-testing)
- [Why PyOsmo?](#why-pyosmo)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Key Features](#key-features)
- [Examples](#examples)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## What is Model-Based Testing?

Model-based testing automatically generates test cases from a model of your system...

## Why PyOsmo?

- **Pure Python** - Use Python's full power for modeling
- **Flexible** - Online and offline testing modes
- **Powerful** - Multiple algorithms, coverage criteria, strategies
- **Easy** - Simple API, minimal boilerplate
- **Extensible** - Plugin architecture for algorithms and strategies

## Installation

```bash
pip install pyosmo
```

## Quick Start

```python
import pyosmo

class CalculatorModel:
    def __init__(self):
        self.value = 0

    def step_add(self):
        self.value += 1

    def step_subtract(self):
        self.value -= 1

    def guard_subtract(self):
        return self.value > 0

# Run tests
osmo = pyosmo.Osmo(CalculatorModel())
osmo.run()
```

## Key Features

### Flexible Model Definition
- Convention-based or decorator-based API
- Guards for conditional steps
- Weights for probability control
- Lifecycle hooks

### Multiple Test Generation Algorithms
- Random
- Balancing (ensures even coverage)
- Weighted
- Weighted Balancing

### Comprehensive End Conditions
- Length-based (steps or test cases)
- Time-based
- Coverage-based
- Logical combinations (AND, OR)

### Robust Error Handling
- Always raise
- Always ignore
- Allow N errors
- Custom strategies

### Rich History & Statistics
- Step execution tracking
- Coverage metrics
- Timing information
- Detailed test logs

## Examples

### Regression Testing
```python
osmo = pyosmo.Osmo(model)
osmo.test_end_condition = pyosmo.end_conditions.StepCoverage(100)
osmo.test_suite_end_condition = pyosmo.end_conditions.Length(5)
osmo.seed = 12345  # Reproducible
osmo.run()
```

### Long-Running Stress Test
```python
osmo = pyosmo.Osmo(model)
osmo.test_end_condition = pyosmo.end_conditions.Time(hours=10)
osmo.run()
```

### Pytest Integration
```python
def test_my_system():
    osmo = pyosmo.Osmo(MyModel())
    osmo.test_end_condition = pyosmo.end_conditions.Length(100)
    osmo.run()
```

See [examples/](examples/) for more comprehensive examples.

## Documentation

- **[User Guide](https://pyosmo.readthedocs.io/guide/)** - Comprehensive guide
- **[API Reference](https://pyosmo.readthedocs.io/api/)** - Complete API docs
- **[Tutorials](https://pyosmo.readthedocs.io/tutorials/)** - Step-by-step tutorials
- **[Examples](examples/)** - Real-world examples

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Inspired by the original Java OSMO tool by Teemu Kanstren.

## Support

- **Issues**: [GitHub Issues](https://github.com/osmo-tool/pyosmo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/osmo-tool/pyosmo/discussions)
- **Email**: oopee1@gmail.com
```

**Tasks**:
- [ ] Fix incomplete performance testing section
- [ ] Add table of contents
- [ ] Add badges for PyPI, versions, license, docs
- [ ] Add "What is MBT?" section
- [ ] Add "Why PyOsmo?" section with clear value proposition
- [ ] Add comprehensive examples section
- [ ] Add links to full documentation
- [ ] Add support/contact section
- [ ] Add acknowledgments

**Effort**: 4 hours
**Priority**: P0

---

### 1.2 Update development.md

**Tasks**:
- [ ] Replace pylint/flake8 references with ruff
- [ ] Add uv-based development workflow
- [ ] Update testing instructions
- [ ] Add modern IDE setup (VSCode, PyCharm)
- [ ] Add pre-commit hooks setup
- [ ] Add debugging tips

**Example Updated Content**:

```markdown
# Development Guide

## Setup Development Environment

### Prerequisites
- Python 3.11 or higher
- uv (recommended) or pip

### Quick Setup

Using uv (recommended):
```bash
# Clone repository
git clone https://github.com/osmo-tool/pyosmo.git
cd pyosmo

# Install with dev dependencies
uv venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
uv pip install -e ".[dev]"
```

Using pip:
```bash
pip install -e ".[dev]"
```

## Code Quality Tools

We use **ruff** for both linting and formatting.

### Linting
```bash
ruff check .
```

### Formatting
```bash
ruff format .
```

### Type Checking
```bash
ty check pyosmo/
```

## Testing

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest pyosmo/tests/test_core.py
```

### Run with coverage
```bash
pytest --cov=pyosmo --cov-report=html
```

### Mutation testing
```bash
mutmut run
mutmut results
```

## IDE Setup

### VSCode

Install recommended extensions:
- Python
- Pylance
- Ruff

Settings (`.vscode/settings.json`):
```json
{
  "python.linting.enabled": false,
  "ruff.enable": true,
  "ruff.lint.run": "onSave",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  }
}
```

### PyCharm

1. Settings → Tools → File Watchers → Add Ruff
2. Settings → Editor → Code Style → Python → Set line length to 120
3. Enable type checking in inspections

## Pre-commit Hooks

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

## Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or via environment variable:
```bash
export PYOSMO_LOG_LEVEL=DEBUG
python your_test.py
```
```

**Effort**: 3 hours
**Priority**: P1

---

## Phase 2: API Documentation (Week 2-3)

### 2.1 Set Up Sphinx/pdoc

**Goal**: Auto-generated API documentation hosted on Read the Docs

**Tasks**:
- [ ] Choose documentation tool (recommend Sphinx with autodoc)
- [ ] Configure Sphinx
- [ ] Set up Read the Docs integration
- [ ] Configure automatic builds on commit

**Sphinx Configuration**:

```python
# docs/conf.py
project = 'PyOsmo'
copyright = '2024, Olli-Pekka Puolitaival'
author = 'Olli-Pekka Puolitaival'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # Google/NumPy docstring support
    'sphinx.ext.viewcode',  # Source code links
    'sphinx.ext.intersphinx',  # Links to other projects
    'sphinx_rtd_theme',  # Read the Docs theme
    'myst_parser',  # Markdown support
]

html_theme = 'sphinx_rtd_theme'

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}
```

**Directory Structure**:
```
docs/
├── conf.py
├── index.rst
├── api/
│   ├── osmo.rst
│   ├── model.rst
│   ├── algorithms.rst
│   ├── end_conditions.rst
│   └── error_strategy.rst
├── guide/
│   ├── getting_started.md
│   ├── concepts.md
│   └── advanced.md
└── tutorials/
    ├── tutorial_01_basics.md
    ├── tutorial_02_data.md
    └── tutorial_03_requirements.md
```

**Effort**: 1 week
**Priority**: P1

---

### 2.2 Complete API Docstrings

**Goal**: 80%+ docstring coverage on public API

**Google Style Docstring Template**:

```python
def run(self, max_iterations: int = 1000) -> OsmoHistory:
    """Run test generation and execution.

    Executes the test model using the configured algorithm and end
    conditions. Returns a history object containing all test execution
    details, statistics, and coverage metrics.

    Args:
        max_iterations: Maximum number of iterations to prevent infinite
            loops. The test will stop if this limit is reached even if
            end conditions are not met.

    Returns:
        OsmoHistory object containing complete test execution history,
        including all executed steps, coverage statistics, timing
        information, and any errors encountered.

    Raises:
        ModelExecutionError: If a step fails and error strategy is
            AlwaysRaise.
        EndConditionError: If end condition evaluation fails.
        ConfigurationError: If model or configuration is invalid.

    Example:
        >>> osmo = Osmo(MyModel())
        >>> osmo.test_end_condition = Length(100)
        >>> history = osmo.run()
        >>> print(f"Executed {history.total_steps} steps")
        Executed 100 steps

    See Also:
        - :class:`OsmoHistory`: History and statistics
        - :meth:`generate`: Alias for run()
        - :class:`EndCondition`: Available end conditions
    """
    ...
```

**Priority Classes/Modules**:
1. `pyosmo.Osmo` - Main entry point
2. `pyosmo.OsmoConfig` - Configuration
3. `pyosmo.model.OsmoModelCollector` - Model management
4. `pyosmo.history.OsmoHistory` - Results
5. All algorithm classes
6. All end condition classes
7. All error strategy classes

**Tasks**:
- [ ] Document all public classes
- [ ] Document all public methods
- [ ] Add examples to key classes
- [ ] Add "See Also" cross-references
- [ ] Document all exceptions
- [ ] Run docstring coverage tool

**Tools**:
```bash
# Check docstring coverage
interrogate pyosmo/ --verbose --ignore-init-method --ignore-private --fail-under 80
```

**Effort**: 1 week
**Priority**: P1

---

## Phase 3: Tutorial Series (Week 4-5)

### 3.1 Tutorial Structure

**Learning Path**:
1. **Basics** - First model, basic concepts (30 min)
2. **Algorithms & End Conditions** - Control test generation (45 min)
3. **Advanced Modeling** - Guards, weights, multiple models (1 hour)
4. **Requirements & Coverage** - Traceability and metrics (1 hour)
5. **Integration & Automation** - Pytest, CI/CD (45 min)

### 3.2 Tutorial 1: Getting Started

**File**: `docs/tutorials/01_getting_started.md`

**Structure**:
```markdown
# Tutorial 1: Getting Started with PyOsmo

**Duration**: 30 minutes
**Prerequisites**: Python 3.11+, basic Python knowledge
**What you'll learn**:
- What model-based testing is
- How to create your first model
- How to run tests
- How to interpret results

## What is Model-Based Testing?

[Explanation with diagrams]

## Your First Model

Let's create a model for a simple counter...

### Step 1: Define the Model

```python
# counter_model.py
class CounterModel:
    def __init__(self):
        self.count = 0

    def step_increment(self):
        self.count += 1
        print(f"Count: {self.count}")

    def step_decrement(self):
        self.count -= 1
        print(f"Count: {self.count}")

    def guard_decrement(self):
        return self.count > 0
```

**Explanation**:
- `step_*` methods define actions
- `guard_*` methods define when actions are allowed
- Model tracks state (`self.count`)

### Step 2: Run the Model

```python
import pyosmo

osmo = pyosmo.Osmo(CounterModel())
osmo.run()
```

**What happens**:
1. PyOsmo discovers steps (increment, decrement)
2. Randomly selects enabled steps
3. Executes until default end condition

### Step 3: Control Test Length

```python
osmo = pyosmo.Osmo(CounterModel())
osmo.test_end_condition = pyosmo.end_conditions.Length(20)
osmo.run()
```

Now the test runs for exactly 20 steps.

### Step 4: View Statistics

```python
osmo.run()
stats = osmo.history.statistics()
print(f"Total steps: {stats.total_steps}")
print(f"Increment count: {stats.step_counts['increment']}")
print(f"Decrement count: {stats.step_counts['decrement']}")
```

## Exercise

Extend the model to:
1. Add a `reset` step that sets count to 0
2. Add a `multiply` step that doubles the count
3. Add a guard to prevent count from exceeding 100

[Solution provided at end]

## Next Steps

- [Tutorial 2: Algorithms & End Conditions](02_algorithms.md)
- [Example Code](../../examples/tutorial_01/)

## Summary

You learned:
- ✅ What model-based testing is
- ✅ How to create a simple model
- ✅ How to run tests
- ✅ How to control test length
- ✅ How to view statistics
```

**Effort**: 1 day per tutorial
**Priority**: P1

---

### 3.3 Tutorial 2: Algorithms & End Conditions

**Topics**:
- Available algorithms (Random, Balancing, Weighted)
- When to use each algorithm
- End conditions (Length, Time, Coverage)
- Combining end conditions (AND, OR)
- Deterministic testing with seeds

### 3.4 Tutorial 3: Advanced Modeling

**Topics**:
- Model lifecycle hooks (before_test, after_test, etc.)
- Step hooks (pre_*, post_*)
- Multiple models with OsmoModelCollector
- Weighted steps
- Model organization best practices

### 3.5 Tutorial 4: Requirements & Coverage

**Topics**:
- Requirements traceability
- State coverage
- Variable coverage
- Step-pair coverage
- Coverage-driven testing

### 3.6 Tutorial 5: Integration & Automation

**Topics**:
- Pytest integration
- Offline test generation
- CI/CD integration
- Report generation
- Performance testing with locust

**Effort**: 1 week (5 tutorials)
**Priority**: P1

---

## Phase 4: User Guide (Week 6-7)

### 4.1 Comprehensive User Guide

**File**: `docs/guide/index.md`

**Structure**:

```markdown
# PyOsmo User Guide

## Table of Contents

### Getting Started
- [Installation](installation.md)
- [Quick Start](quickstart.md)
- [Core Concepts](concepts.md)

### Model Development
- [Creating Models](models/creating.md)
- [Guards and Weights](models/guards_weights.md)
- [Lifecycle Hooks](models/hooks.md)
- [Multiple Models](models/multiple.md)
- [Best Practices](models/best_practices.md)

### Test Generation
- [Algorithms](generation/algorithms.md)
- [End Conditions](generation/end_conditions.md)
- [Error Strategies](generation/error_strategies.md)
- [Configuration](generation/configuration.md)

### Coverage & Metrics
- [Step Coverage](coverage/steps.md)
- [Requirements Traceability](coverage/requirements.md)
- [State Coverage](coverage/states.md)
- [Variable Coverage](coverage/variables.md)

### Reporting & Analysis
- [Test History](reporting/history.md)
- [Statistics](reporting/statistics.md)
- [Report Generation](reporting/reports.md)
- [Visualization](reporting/visualization.md)

### Integration
- [Pytest Integration](integration/pytest.md)
- [CI/CD](integration/cicd.md)
- [Offline Testing](integration/offline.md)
- [Performance Testing](integration/performance.md)

### Advanced Topics
- [Model Validation](advanced/validation.md)
- [Custom Algorithms](advanced/custom_algorithms.md)
- [Custom End Conditions](advanced/custom_conditions.md)
- [Debugging](advanced/debugging.md)

### Reference
- [Configuration Options](reference/configuration.md)
- [CLI Reference](reference/cli.md)
- [API Reference](../api/)
- [Glossary](reference/glossary.md)

### Appendices
- [Troubleshooting](appendix/troubleshooting.md)
- [FAQ](appendix/faq.md)
- [Migration Guide](appendix/migration.md)
- [Comparison with Java OSMO](appendix/java_comparison.md)
```

**Key Sections to Develop**:

#### 4.1.1 Troubleshooting Guide

```markdown
# Troubleshooting

## Common Issues

### "No steps found in model"

**Symptom**: PyOsmo reports no steps discovered

**Causes**:
1. Methods don't start with `step_`
2. Model not properly instantiated
3. Methods are static/class methods

**Solutions**:
```python
# ❌ Wrong
class Model:
    @staticmethod
    def step_action():  # Static methods not supported
        pass

# ✅ Correct
class Model:
    def step_action(self):  # Instance method
        pass
```

### "All steps disabled"

**Symptom**: Test ends immediately with 0 steps

**Causes**:
1. All guards return False
2. Circular guard dependencies

**Solutions**:
- Check guard logic
- Ensure at least one step is always enabled
- Use model validation: `pyosmo validate model.py`

[More issues...]
```

#### 4.1.2 FAQ

```markdown
# Frequently Asked Questions

## General

### What is the difference between online and offline MBT?

**Online MBT**: Steps execute against real system as test runs
**Offline MBT**: Steps generate test script for later execution

Use online when:
- Testing non-deterministic systems
- Need runtime adaptation
- Long-running tests

Use offline when:
- Reusing existing test infrastructure
- Need reproducible test suites
- Deterministic systems

### How is PyOsmo different from property-based testing (Hypothesis)?

**Hypothesis**: Generates test inputs for a single test function
**PyOsmo**: Generates sequences of actions for stateful testing

They complement each other:
```python
from hypothesis import given, strategies as st

class Model:
    @given(amount=st.integers(1, 100))
    def step_deposit(self, amount):
        self.balance += amount
```

[More questions...]
```

**Effort**: 2 weeks
**Priority**: P1

---

## Phase 5: Contributing & Community (Week 8)

### 5.1 CONTRIBUTING.md

**Structure**:
```markdown
# Contributing to PyOsmo

## Welcome!

Thanks for your interest in contributing to PyOsmo!

## Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest features
- 📖 Improve documentation
- 🔧 Submit code fixes
- ✨ Add new features
- 🧪 Write tests

## Getting Started

### Development Setup

[Step by step setup instructions]

### Making Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run quality checks
6. Submit pull request

### Code Style

We use ruff for linting and formatting...

### Testing

All new features must include tests...

### Documentation

All new features must include documentation...

## Pull Request Process

1. Update CHANGELOG.md
2. Ensure all tests pass
3. Update documentation
4. Request review

## Code of Conduct

Be respectful and inclusive...

## Questions?

Ask in [GitHub Discussions](https://github.com/osmo-tool/pyosmo/discussions)
```

**Effort**: 1 day
**Priority**: P2

---

### 5.2 Example Gallery

**File**: `docs/examples/index.md`

**Categories**:
- **Basic Examples** - Simple models to learn from
- **Web Testing** - Selenium/Playwright integration
- **API Testing** - REST API testing
- **Data Science** - Testing ML models
- **Game Testing** - Stateful game logic
- **Database Testing** - CRUD operations

Each example includes:
- Clear goal/purpose
- Complete code
- Explanation
- Expected output
- Variations/exercises

**Effort**: 3 days
**Priority**: P2

---

## Documentation Maintenance

### Continuous Improvement

**Automated Checks**:
```yaml
# .github/workflows/docs.yml
name: Documentation

on: [push, pull_request]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          pip install sphinx sphinx-rtd-theme interrogate

      - name: Check docstring coverage
        run: interrogate pyosmo/ --fail-under 80

      - name: Build docs
        run: |
          cd docs
          make html

      - name: Check for broken links
        run: sphinx-build -b linkcheck docs docs/_build/linkcheck
```

**Review Schedule**:
- **Weekly**: Fix broken links, address doc issues
- **Monthly**: Review and update examples
- **Quarterly**: Major documentation review
- **Per release**: Update all version-specific content

---

## Success Metrics

### Quantitative
- [ ] README completeness: 100%
- [ ] Docstring coverage: 80%+
- [ ] Tutorial count: 5+
- [ ] User guide pages: 30+
- [ ] Example count: 20+
- [ ] Doc build errors: 0
- [ ] Broken links: 0

### Qualitative
- [ ] New users can get started in < 30 minutes
- [ ] 80%+ of questions answered by docs
- [ ] Positive feedback on documentation
- [ ] Documentation mentioned in reviews/testimonials

### Community Engagement
- [ ] GitHub stars: 100+
- [ ] Doc page views: 1000+/month
- [ ] Low "docs unclear" issue rate

---

## Timeline Summary

| Phase | Duration | Priority | Deliverables |
|-------|----------|----------|--------------|
| Phase 1: Critical Fixes | Week 1 | P0 | Complete README, updated dev docs |
| Phase 2: API Docs | Week 2-3 | P1 | Sphinx setup, 80% docstrings |
| Phase 3: Tutorials | Week 4-5 | P1 | 5 complete tutorials |
| Phase 4: User Guide | Week 6-7 | P1 | Comprehensive guide |
| Phase 5: Community | Week 8 | P2 | Contributing guide, examples |
| **Total** | **8 weeks** | | **Professional documentation** |

---

## Resources Needed

**Tools**:
- Sphinx + sphinx-rtd-theme (free)
- Read the Docs hosting (free for open source)
- interrogate for docstring coverage (free)
- Mermaid for diagrams (free)

**People**:
- 1 technical writer (can be developer)
- 1 reviewer for accuracy
- Community contributors for examples

**Budget**:
- $0 (all open source tools)
- Optional: Professional editing ($500-1000)

---

## Appendix: Documentation Templates

### API Reference Template
```markdown
## ClassName

Brief description.

### Constructor

`__init__(param1, param2, ...)`

**Parameters**:
- `param1` (type): Description
- `param2` (type): Description

**Example**:
```python
obj = ClassName(param1, param2)
```

### Methods

#### method_name

`method_name(param1, param2) -> return_type`

Description.

**Parameters**:
...

**Returns**:
...

**Raises**:
...

**Example**:
...
```

### Tutorial Template
```markdown
# Tutorial N: Title

**Duration**: X minutes
**Prerequisites**: ...
**What you'll learn**: ...

## Introduction

[Context and motivation]

## Step 1: [Action]

[Explanation]

```python
[Code]
```

**What's happening**:
- Point 1
- Point 2

## Step 2: [Action]

...

## Exercise

[Hands-on challenge]

## Summary

- ✅ Learned X
- ✅ Learned Y

## Next Steps

- [Related tutorial]
- [Related docs]
```

---

*Document Version: 1.0*
*Last Updated: 2025-11-05*
*Next Review: End of Phase 1*
