# Configuration API Guide

This guide demonstrates how to use PyOsmo's fluent configuration API to set up and run model-based tests with a clean, readable syntax.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Fluent Configuration API](#fluent-configuration-api)
3. [Convenience Methods (More Fluent API)](#convenience-methods-more-fluent-api)
4. [Complete Examples](#complete-examples)
5. [API Reference](#api-reference)

---

## Basic Usage

The traditional way to configure PyOsmo:

```python
from pyosmo import Osmo
from pyosmo.algorithm import RandomAlgorithm
from pyosmo.end_conditions import Length
from pyosmo.error_strategy import AlwaysRaise

# Create model
class MyModel:
    def step_login(self):
        print("Logging in...")

# Traditional configuration
osmo = Osmo(MyModel())
osmo.seed = 12345
osmo.algorithm = RandomAlgorithm()
osmo.test_end_condition = Length(100)
osmo.test_suite_end_condition = Length(5)
osmo.test_error_strategy = AlwaysRaise()

# Run tests
osmo.run()
```

While this works, the fluent API provides a more concise and readable alternative.

---

## Fluent Configuration API

The fluent API allows you to chain configuration methods together:

### Available Methods

- `with_seed(seed)` - Set random seed for reproducibility
- `with_algorithm(algorithm)` - Set the step selection algorithm
- `with_test_end_condition(condition)` - Set when each test should stop
- `with_suite_end_condition(condition)` - Set when the test suite should stop
- `on_error(strategy)` - Set error handling strategy for both test and suite
- `on_test_error(strategy)` - Set error handling strategy for tests only
- `on_suite_error(strategy)` - Set error handling strategy for suite only
- `build()` - Finalize configuration (returns self)

### Example

```python
from pyosmo import Osmo
from pyosmo.algorithm import RandomAlgorithm
from pyosmo.end_conditions import Length
from pyosmo.error_strategy import AlwaysRaise

osmo = (Osmo(MyModel())
    .with_seed(12345)
    .with_algorithm(RandomAlgorithm())
    .with_test_end_condition(Length(100))
    .with_suite_end_condition(Length(5))
    .on_error(AlwaysRaise())
    .build())

osmo.run()
```

---

## Convenience Methods (More Fluent API)

For even more concise configuration, use the convenience methods that combine common operations:

### Algorithm Methods

- `random_algorithm(seed=None)` - Use random algorithm (optionally set seed)
- `balancing_algorithm(seed=None)` - Use balancing algorithm (optionally set seed)
- `weighted_algorithm(seed=None)` - Use weighted algorithm (optionally set seed)

### End Condition Methods

- `stop_after_steps(n)` - Stop each test after N steps
- `stop_after_time(seconds)` - Stop each test after N seconds
- `run_tests(n)` - Run N tests in the suite
- `run_endless()` - Run tests endlessly (use Ctrl+C to stop)

### Error Handling Methods

- `raise_on_error()` - Raise exceptions immediately
- `ignore_errors(max_count=None)` - Ignore errors (optionally limit count)
- `ignore_asserts()` - Ignore assertion errors only

### Example

```python
from pyosmo import Osmo

# Super concise configuration!
osmo = (Osmo(MyModel())
    .random_algorithm(seed=12345)
    .stop_after_steps(100)
    .run_tests(5)
    .raise_on_error()
    .build())

osmo.run()
```

This is equivalent to the traditional configuration shown in the basic usage section.

---

## Complete Examples

### Example 1: Quick Smoke Test

Run a quick 3-test smoke test with 20 steps each:

```python
from pyosmo import Osmo

class LoginModel:
    def step_login(self):
        print("Logging in...")

    def step_logout(self):
        print("Logging out...")

osmo = (Osmo(LoginModel())
    .random_algorithm(seed=42)
    .stop_after_steps(20)
    .run_tests(3)
    .build())

osmo.run()
```

### Example 2: Long-Running Test with Time Limit

Run tests for 60 seconds each:

```python
osmo = (Osmo(MyModel())
    .balancing_algorithm(seed=12345)
    .stop_after_time(60)  # 60 seconds per test
    .run_tests(10)
    .ignore_errors(max_count=5)  # Allow up to 5 errors
    .build())

osmo.run()
```

### Example 3: Exploratory Testing

Run tests endlessly to explore edge cases:

```python
osmo = (Osmo(MyModel())
    .weighted_algorithm()  # Use weighted algorithm for variety
    .stop_after_steps(1000)
    .run_endless()  # Run until Ctrl+C
    .ignore_asserts()  # Continue on assertion failures
    .build())

osmo.run()
```

### Example 4: Deterministic Regression Test

Run deterministic tests for regression testing:

```python
osmo = (Osmo(MyModel())
    .random_algorithm(seed=12345)  # Fixed seed for reproducibility
    .stop_after_steps(500)
    .run_tests(10)
    .raise_on_error()  # Fail fast on any error
    .build())

osmo.run()

# Print statistics
print(f"Total steps: {osmo.history.total_steps}")
print(f"Total tests: {len(osmo.history.test_cases)}")
print(f"Duration: {osmo.history.duration}")
```

### Example 5: Mixing Old and New Styles

You can mix the traditional property-based configuration with the fluent API:

```python
from pyosmo.end_conditions import StepCoverage

osmo = Osmo(MyModel()).random_algorithm(seed=100)

# Use traditional configuration for complex conditions
osmo.test_end_condition = StepCoverage(percentage=100)

# Continue with fluent API
osmo.run_tests(5).raise_on_error()

osmo.run()
```

### Example 6: Configuration Without build()

The `build()` method is optional - you can configure and run in one chain:

```python
# Without build() - run immediately
(Osmo(MyModel())
    .random_algorithm(seed=42)
    .stop_after_steps(50)
    .run_tests(3)
    .raise_on_error()
    .run())  # No build() needed!
```

---

## API Reference

### General Fluent Methods

#### `with_seed(seed: int) -> Osmo`

Set the random seed for test generation.

**Parameters:**
- `seed` (int): Random seed value for reproducible test generation

**Returns:** Self for method chaining

**Example:**
```python
osmo = Osmo(model).with_seed(12345)
```

---

#### `with_algorithm(algorithm: OsmoAlgorithm) -> Osmo`

Set the test generation algorithm.

**Parameters:**
- `algorithm` (OsmoAlgorithm): Algorithm instance (RandomAlgorithm, BalancingAlgorithm, etc.)

**Returns:** Self for method chaining

**Example:**
```python
from pyosmo.algorithm import BalancingAlgorithm
osmo = Osmo(model).with_algorithm(BalancingAlgorithm())
```

---

#### `with_test_end_condition(condition: OsmoEndCondition) -> Osmo`

Set when each individual test should end.

**Parameters:**
- `condition` (OsmoEndCondition): End condition instance (Length, Time, StepCoverage, etc.)

**Returns:** Self for method chaining

**Example:**
```python
from pyosmo.end_conditions import Length
osmo = Osmo(model).with_test_end_condition(Length(100))
```

---

#### `with_suite_end_condition(condition: OsmoEndCondition) -> Osmo`

Set when the entire test suite should end.

**Parameters:**
- `condition` (OsmoEndCondition): End condition instance

**Returns:** Self for method chaining

**Example:**
```python
from pyosmo.end_conditions import Length
osmo = Osmo(model).with_suite_end_condition(Length(5))
```

---

#### `on_error(strategy: OsmoErrorStrategy) -> Osmo`

Set error handling strategy for both test and suite levels.

**Parameters:**
- `strategy` (OsmoErrorStrategy): Error strategy instance

**Returns:** Self for method chaining

**Example:**
```python
from pyosmo.error_strategy import AlwaysIgnore
osmo = Osmo(model).on_error(AlwaysIgnore())
```

---

#### `on_test_error(strategy: OsmoErrorStrategy) -> Osmo`

Set error handling strategy for test level only.

**Parameters:**
- `strategy` (OsmoErrorStrategy): Error strategy instance

**Returns:** Self for method chaining

---

#### `on_suite_error(strategy: OsmoErrorStrategy) -> Osmo`

Set error handling strategy for suite level only.

**Parameters:**
- `strategy` (OsmoErrorStrategy): Error strategy instance

**Returns:** Self for method chaining

---

#### `build() -> Osmo`

Finalize configuration and return the Osmo instance. This method is optional but can be used as the final call in a fluent chain for consistency.

**Returns:** Self

**Example:**
```python
osmo = Osmo(model).with_seed(42).build()
```

---

### Convenience Methods

#### `random_algorithm(seed: Optional[int] = None) -> Osmo`

Use random algorithm for step selection, optionally setting the seed.

**Parameters:**
- `seed` (int, optional): Random seed. If provided, also sets the seed for the entire test run.

**Returns:** Self for method chaining

**Example:**
```python
osmo = Osmo(model).random_algorithm(seed=12345)
```

---

#### `balancing_algorithm(seed: Optional[int] = None) -> Osmo`

Use balancing algorithm for step selection (favors less-executed steps).

**Parameters:**
- `seed` (int, optional): Random seed

**Returns:** Self for method chaining

---

#### `weighted_algorithm(seed: Optional[int] = None) -> Osmo`

Use weighted algorithm for step selection (uses step weights).

**Parameters:**
- `seed` (int, optional): Random seed

**Returns:** Self for method chaining

---

#### `stop_after_steps(steps: int) -> Osmo`

Stop each test after N steps.

**Parameters:**
- `steps` (int): Number of steps per test

**Returns:** Self for method chaining

**Example:**
```python
osmo = Osmo(model).stop_after_steps(100)
```

---

#### `stop_after_time(seconds: int) -> Osmo`

Stop each test after N seconds.

**Parameters:**
- `seconds` (int): Maximum test duration in seconds

**Returns:** Self for method chaining

**Example:**
```python
osmo = Osmo(model).stop_after_time(60)  # 60 seconds
```

---

#### `run_tests(count: int) -> Osmo`

Run N tests in the suite.

**Parameters:**
- `count` (int): Number of tests to run

**Returns:** Self for method chaining

**Example:**
```python
osmo = Osmo(model).run_tests(5)
```

---

#### `run_endless() -> Osmo`

Run tests endlessly. You'll need to manually interrupt execution with Ctrl+C.

**Returns:** Self for method chaining

**Example:**
```python
osmo = Osmo(model).run_endless()
```

---

#### `raise_on_error() -> Osmo`

Raise exceptions immediately when errors occur (fail-fast behavior).

**Returns:** Self for method chaining

**Example:**
```python
osmo = Osmo(model).raise_on_error()
```

---

#### `ignore_errors(max_count: Optional[int] = None) -> Osmo`

Ignore errors during test execution.

**Parameters:**
- `max_count` (int, optional): Maximum number of errors to ignore. If None, all errors are ignored.

**Returns:** Self for method chaining

**Example:**
```python
# Ignore all errors
osmo = Osmo(model).ignore_errors()

# Ignore up to 5 errors
osmo = Osmo(model).ignore_errors(max_count=5)
```

---

#### `ignore_asserts() -> Osmo`

Ignore assertion errors but raise other exceptions.

**Returns:** Self for method chaining

**Example:**
```python
osmo = Osmo(model).ignore_asserts()
```

---

## Benefits of the Fluent API

1. **Readability**: Configuration reads like a sentence describing what you want to do
2. **Discoverability**: IDE autocomplete helps you discover available options
3. **Conciseness**: Less boilerplate code
4. **Chaining**: Configure everything in one expression
5. **Backward Compatible**: Old-style property setting still works
6. **Flexible**: Mix and match old and new styles as needed

---

## Best Practices

1. **Use convenience methods** when possible for maximum readability:
   ```python
   # Good
   osmo = Osmo(model).random_algorithm(seed=42).stop_after_steps(100)

   # Also fine, but more verbose
   osmo = Osmo(model).with_algorithm(RandomAlgorithm()).with_seed(42)
   ```

2. **Set seed explicitly** for reproducible tests:
   ```python
   osmo = Osmo(model).random_algorithm(seed=12345)
   ```

3. **Use meaningful step counts** based on your model size:
   ```python
   # Small model with 5 steps
   osmo = Osmo(model).stop_after_steps(50)

   # Large model with 50 steps
   osmo = Osmo(model).stop_after_steps(500)
   ```

4. **Store configuration** in variables for reuse:
   ```python
   def create_smoke_test(model):
       return (Osmo(model)
           .random_algorithm(seed=42)
           .stop_after_steps(20)
           .run_tests(3))

   osmo = create_smoke_test(MyModel())
   osmo.run()
   ```

5. **Build optional** - only use when you need a clear separation:
   ```python
   # With build() - clear intent to finalize configuration
   osmo = Osmo(model).random_algorithm(seed=42).build()
   osmo.run()

   # Without build() - also fine
   osmo = Osmo(model).random_algorithm(seed=42)
   osmo.run()
   ```

---

*Last updated: 2025-11-05*
