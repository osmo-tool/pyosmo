# PyOsmo - Model-Based Testing Tool

This is a Python-based model-based testing (MBT) framework inspired by the original OSMO tester.

## Project Structure

- `pyosmo/` - Main package directory
  - `algorithm/` - Test generation algorithms (random, weighted, balancing)
  - `end_conditions/` - Conditions for ending tests (length, time, coverage)
  - `error_strategy/` - Error handling strategies
  - `history/` - Test execution history tracking
  - `models/` - Base model classes
  - `tests/` - Unit tests
  - `osmo.py` - Main Osmo test generator class
  - `model.py` - Model parsing and validation
  - `decorators.py` - Decorators for model methods

## Key Concepts

- **Model**: A class with methods decorated as guards and steps
- **Guards**: Methods starting with `guard_` that return True/False
- **Steps**: Methods starting with `step_` that execute test actions
- **Algorithms**: Strategies for selecting which step to execute next
- **End Conditions**: Rules for when to stop test generation

## Testing

Run tests with: `pytest pyosmo/tests/`
