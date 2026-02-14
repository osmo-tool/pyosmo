# PyOsmo Roadmap

## Overview

This document tracks PyOsmo's development roadmap and feature comparison with the mature Java OSMO implementation (v3.7.1). It consolidates the project's priorities, current status, and planned improvements.

**Current Version**: v0.2.2
**Python Support**: 3.11–3.14

---

## What's Been Done (v0.1.3 → v0.2.2)

These items from the original roadmap are complete:

- **Decorator-based model API**: `@step`, `@guard`, `@weight`, `@pre`, `@post`, `@requires` decorators
- **Fluent configuration API**: Method chaining for Osmo setup (see `fluent_api_guide.md`)
- **Inspect-based model introspection**: Modern model discovery replacing `dir()` introspection
- **Plugin registry**: Extensible architecture for algorithms, end conditions, error strategies
- **pytest integration**: `pytest_pyosmo` plugin for native pytest discovery
- **Build modernization**: Consolidated to `pyproject.toml`, removed `setup.py`
- **Development tooling**: Migrated to ruff (linting/formatting) and ty (type checking)
- **CI/CD**: GitHub Actions on Python 3.11–3.14 with uv
- **README**: Complete and accurate
- **Publishing workflow**: Fixed for Python 3.11+

---

## Priority Classification

- **P1 (High)**: Important for production readiness and adoption
- **P2 (Medium)**: Quality improvements, nice-to-have features
- **P3 (Low)**: Future enhancements, optimization opportunities

---

## P1 — High Priority

### Type Hints & Docstrings

Improve type hint coverage on the public API and add Google-style docstrings to all public classes and methods. Run ty in CI for validation.

### Requirements Traceability

Port Java OSMO's requirement tracking system:
- `@requires()` decorator for associating steps with requirements
- `@requires_all()` / `@requires_any()` for AND/OR logic
- Requirement coverage tracking in history
- Requirement coverage end condition

```python
from pyosmo.decorators import requires

class LoginModel:
    @requires("REQ-001")
    def step_login(self):
        pass
```

### State & Step-Pair Coverage

- `@state` decorator for marking state-defining methods
- Track unique states visited during execution
- Track step sequences (pairs) for transition coverage
- End conditions based on state/step-pair coverage

### Structured Reporting

Replace basic console output with professional reports:
- JSON export for data interchange
- HTML reports (Jinja2-based)
- JUnit XML for CI/CD integration
- Markdown reports for documentation

```python
from pyosmo.reporting import HTMLReporter, JSONReporter

HTMLReporter(osmo.history).save("report.html")
JSONReporter(osmo.history).save("data.json")
```

### Model Validation & Analysis

Static model analysis before execution:
- Validate model structure
- Detect unreachable steps (always-false guards)
- Detect always-enabled steps (missing guards)
- CLI command: `pyosmo validate mymodel.py`

### Model Visualization

Generate visual representations of models for communication and debugging:
- Mermaid and GraphViz diagram export of steps, guards, and transitions
- Coverage heatmaps showing step execution frequency
- CLI command: `pyosmo visualize mymodel.py`
- Inline rendering in Jupyter notebooks

```bash
pyosmo visualize mymodel.py --format mermaid
# Output: steps, guards, and transitions as a Mermaid state diagram
```

### Test Case Minimization / Shrinking

When a failure is found, automatically find the shortest step sequence that reproduces it (similar to Hypothesis shrinking):
- Replay and reduce failing sequences
- Binary search and delta-debugging strategies
- Output minimal reproduction script

### Tutorials & Documentation

- Tutorial series: Getting Started, Data-Driven Testing, Scenario-Based Testing
- Generated API reference documentation (Sphinx or pdoc)
- Comprehensive user guide

---

## P2 — Medium Priority

### Variable Coverage

Track data variation across test executions:
- `@variable()` decorator with category-partition support
- Variable coverage metrics and end conditions

### Optimizer Algorithm

Greedy step selection to accelerate coverage:
- Select steps that cover uncovered requirements
- Select steps that visit unvisited states
- Reduce execution time to achieve coverage goals

### Test Case Persistence

Save and replay generated test sequences:
- Save sequences to JSON
- Replay saved sequences for regression

### Hypothesis Integration

Bridge MBT with property-based testing:
- Provide a Hypothesis strategy that generates step sequences from a PyOsmo model
- Leverage Hypothesis shrinking for automatic failure minimization
- Combine random model exploration with Hypothesis's database of interesting examples

```python
from pyosmo.hypothesis import osmo_strategy

@given(osmo_strategy(MyModel))
def test_model(steps):
    # Hypothesis drives step selection, shrinks on failure
    pass
```

### Jupyter Notebook Integration

First-class support for interactive model development:
- Inline model visualization (Mermaid/SVG diagrams)
- Live coverage display after `osmo.run()` in a cell
- Interactive step-by-step execution for debugging

### Performance Profiling

Built-in execution profiling:
- Step execution time tracking
- Guard evaluation time tracking
- Performance reports and CLI profiling mode

### Enhanced Error Reporting

Richer error context:
- Step execution traceback capture
- Model state snapshot on error
- Error reproduction scripts

---

## P3 — Future Enhancements

- **Parallel execution**: Multi-process test generation
- **Adaptive algorithms**: Runtime-adapting step selection
- **LLM-assisted model generation**: Generate model skeletons from requirements, user stories, or API specs using LLMs — extending the `model-creator/` concept to general-purpose model scaffolding
- **Live testing dashboard**: Web-based dashboard for long-running online tests showing real-time coverage progress, step execution heatmap, and current model state
- **Distributed testing**: Multi-machine coordination
- **Constraint solving**: Z3/OR-Tools integration
- **Probability-based end condition**: Random stopping with configurable probability

---

## Feature Comparison: PyOsmo vs Java OSMO

### Legend

- ✅ Fully implemented
- ⚠️ Partially implemented
- ❌ Missing
- 🔄 Different approach (language idioms)

### Core Features

| Feature | Java OSMO | PyOsmo | Status |
|---------|-----------|--------|--------|
| Step declaration | `@TestStep` annotation | `step_*` naming + `@step` decorator | ✅ |
| Guard declaration | `@Guard` annotation | `guard_*` naming + `@guard` decorator | ✅ |
| Weight declaration | `@Weight` annotation | `weight_*` naming + `@weight` decorator | ✅ |
| Pre/post step hooks | `@Before`/`@After` | `@pre`/`@post` decorators | ✅ |
| Suite/test lifecycle | `@BeforeSuite`, etc. | `before_suite()`, etc. | ✅ |
| Multiple models | Model composition | `Osmo(model1, model2)` | ✅ |
| Fluent config API | Builder pattern | Method chaining | ✅ |

### Algorithms

| Algorithm | Java OSMO | PyOsmo | Status |
|-----------|-----------|--------|--------|
| Random | ✅ | ✅ RandomAlgorithm | ✅ |
| Balancing | ✅ | ✅ BalancingAlgorithm | ✅ |
| Weighted Random | ✅ | ✅ WeightedAlgorithm | ✅ |
| Weighted Balancing | ✅ | ✅ WeightedBalancingAlgorithm | ✅ |
| Optimizer | ✅ | ❌ | P2 |
| Custom algorithms | ✅ Extensible | ✅ Extensible | ✅ |

### End Conditions

| Condition | Java OSMO | PyOsmo | Status |
|-----------|-----------|--------|--------|
| Length-based | ✅ | ✅ Length | ✅ |
| Time-based | ✅ | ✅ Time | ✅ |
| Step coverage | ✅ | ✅ StepCoverage | ✅ |
| Logical combinators | ✅ And/Or | ✅ And/Or | ✅ |
| Endless | ✅ | ✅ Endless | ✅ |
| Requirement coverage | ✅ | ❌ | P1 |
| State coverage | ✅ | ❌ | P1 |
| Probability-based | ✅ | ❌ | P3 |

### Error Handling

| Strategy | Java OSMO | PyOsmo | Status |
|----------|-----------|--------|--------|
| Always raise | ✅ | ✅ AlwaysRaise | ✅ |
| Always ignore | ✅ | ✅ AlwaysIgnore | ✅ |
| Allow count | ✅ | ✅ AllowCount | ✅ |
| Ignore asserts | ⚠️ | ✅ IgnoreAsserts | 🔄 |
| Custom strategies | ✅ | ✅ Extensible | ✅ |

### Coverage & Traceability

| Feature | Java OSMO | PyOsmo | Status |
|---------|-----------|--------|--------|
| Step coverage | ✅ | ✅ | ✅ |
| Requirements tracking | ✅ | ❌ | P1 |
| State coverage | ✅ | ❌ | P1 |
| Step-pair coverage | ✅ | ❌ | P1 |
| Variable coverage | ✅ | ❌ | P2 |

### Reporting & Output

| Feature | Java OSMO | PyOsmo | Status |
|---------|-----------|--------|--------|
| Console output | ✅ | ✅ | ✅ |
| Step statistics | ✅ | ✅ | ✅ |
| HTML reports | ✅ | ❌ | P1 |
| JSON export | ⚠️ | ❌ | P1 |
| JUnit XML | ✅ | ❌ | P1 |
| Test persistence | ✅ | ❌ | P2 |

### Integration

| Feature | Java OSMO | PyOsmo | Status |
|---------|-----------|--------|--------|
| Test framework | JUnit | pytest | ✅ (language-specific) |
| Package manager | Maven | pip/PyPI | ✅ (language-specific) |
| CI/CD templates | ⚠️ | ✅ GitHub Actions | ✅ |

### Summary by Status

| Status | Count |
|--------|-------|
| ✅ Fully implemented | ~28 |
| ⚠️ Partial / 🔄 Different | ~5 |
| ❌ Missing (planned) | ~15 |

---

## PyOsmo's Competitive Advantages

1. **Language simplicity**: Python is easier to learn than Java
2. **Rich ecosystem**: Integrates naturally with pytest, Selenium, Playwright, requests
3. **Interactive development**: Works in Jupyter notebooks and IPython
4. **Modern tooling**: pip/uv, ruff, ty — fast and ergonomic
5. **Flexible modeling**: Duck typing + decorators for model definition
6. **Pure Python**: No graphical tools or DSLs — just code

---

*Last updated: 2026-02-14*
