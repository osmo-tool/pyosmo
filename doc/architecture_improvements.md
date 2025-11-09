# Architecture & Design Improvements for PyOsmo

## Overview

This document proposes architectural improvements to enhance pyosmo's maintainability, extensibility, performance, and code quality. The focus is on structural improvements that enable long-term growth while maintaining backward compatibility.

---

## Table of Contents

1. [Current Architecture Analysis](#1-current-architecture-analysis)
2. [Code Quality Improvements](#2-code-quality-improvements)
3. [Plugin Architecture Enhancement](#3-plugin-architecture-enhancement)
4. [Model Discovery & Introspection](#4-model-discovery--introspection)
5. [Event System](#5-event-system)
6. [Performance Optimizations](#6-performance-optimizations)
7. [Testing Infrastructure](#7-testing-infrastructure)
8. [Logging & Debugging](#8-logging--debugging)

---

## 1. Current Architecture Analysis

### 1.1 Current Structure

```
pyosmo/
├── osmo.py              # Main orchestrator (231 lines)
├── model.py             # Model introspection (185 lines)
├── config.py            # Configuration (132 lines)
├── main.py              # CLI (78 lines)
├── decorators.py        # Utility decorators (22 lines)
├── algorithm/           # Test generation algorithms
│   ├── base.py
│   ├── random.py
│   ├── balancing.py
│   └── weighted.py
├── end_conditions/      # Test termination conditions
├── error_strategy/      # Error handling strategies
├── history/             # Execution history tracking
└── models/              # Base model classes
```

### 1.2 Strengths

✅ **Clear Separation of Concerns**: Algorithms, conditions, strategies well separated
✅ **Plugin Architecture**: Easy to extend with new algorithms/conditions
✅ **Modularity**: Each component has single responsibility
✅ **Composition**: OsmoModelCollector enables multiple models

### 1.3 Weaknesses

❌ **Fragile Introspection**: Uses `dir()` and string matching
❌ **No Validation**: Model structure not validated before execution
❌ **Limited Extensibility**: Hard to add new model discovery mechanisms
❌ **Tight Coupling**: Some components directly depend on implementation details
❌ **No Event System**: Hard to add monitoring/logging hooks
❌ **Performance**: No lazy evaluation or optimization

---

## 2. Code Quality Improvements

### 2.1 Eliminate Fragile Patterns

#### Current: Fragile dir() Introspection

```python
# Current problematic pattern in model.py
def _discover_steps(self, model):
    steps = []
    for name in dir(model):  # ❌ Fragile: picks up inherited, private methods
        if name.startswith('step_'):
            method = getattr(model, name)
            steps.append(method)
    return steps
```

**Problems**:
- Picks up inherited methods from base classes
- Includes private methods if named `step_*`
- No validation of method signature
- Silent failures if methods don't exist

#### Proposed: Robust Discovery

```python
class ModelIntrospector:
    """Robust model introspection with validation."""

    def __init__(self, model: object):
        self.model = model
        self._cache: Dict[str, Any] = {}

    def discover_steps(self) -> List[TestStep]:
        """Discover steps with comprehensive validation."""
        if 'steps' in self._cache:
            return self._cache['steps']

        steps = []

        # Method 1: Decorator-based (explicit)
        steps.extend(self._discover_decorated_steps())

        # Method 2: Naming convention (implicit)
        steps.extend(self._discover_conventional_steps())

        # Validate all steps
        for step in steps:
            self._validate_step(step)

        self._cache['steps'] = steps
        return steps

    def _discover_conventional_steps(self) -> List[TestStep]:
        """Discover steps via naming convention."""
        steps = []

        # Only check instance's own class, not inherited
        for name, method in inspect.getmembers(
            self.model.__class__,
            predicate=inspect.isfunction
        ):
            # Check naming convention
            if not name.startswith('step_'):
                continue

            # Skip private methods
            if name.startswith('_'):
                continue

            # Validate signature
            if not self._is_valid_step_signature(method):
                raise ModelValidationError(
                    f"Step method {name} must have signature: "
                    f"(self) -> None"
                )

            steps.append(TestStep(
                name=name[5:],  # Remove 'step_' prefix
                method=method,
                guard=self._find_guard(name[5:]),
                weight=self._find_weight(name[5:])
            ))

        return steps

    def _is_valid_step_signature(self, method: Callable) -> bool:
        """Validate step method signature."""
        sig = inspect.signature(method)

        # Must have only 'self' parameter
        params = list(sig.parameters.values())
        return (
            len(params) == 1 and
            params[0].name == 'self'
        )
```

**Benefits**:
- ✅ Type-safe using inspect module
- ✅ Validates method signatures
- ✅ Clear error messages
- ✅ Avoids inherited method issues
- ✅ Cacheable for performance

---

### 2.2 Replace Bare Exception Handlers

#### Current: Overly Broad Exception Handling

```python
# Current pattern in various places
try:
    step_method()
except:  # ❌ Too broad
    raise
```

#### Proposed: Specific Exception Handling

```python
class StepExecutor:
    """Execute test steps with proper error handling."""

    def execute_step(
        self,
        step: TestStep,
        model: object,
        error_strategy: ErrorStrategy
    ) -> StepResult:
        """Execute a single step with error handling.

        Args:
            step: Step to execute
            model: Model instance
            error_strategy: How to handle errors

        Returns:
            StepResult with success/failure information

        Raises:
            StepExecutionError: If step fails and strategy is AlwaysRaise
        """
        try:
            # Execute step
            step.method(model)

            return StepResult(
                step_name=step.name,
                success=True,
                duration=time.time() - start_time
            )

        except AssertionError as e:
            # Test assertion failed
            return self._handle_error(
                step=step,
                error=e,
                error_type=ErrorType.ASSERTION,
                strategy=error_strategy
            )

        except AttributeError as e:
            # Missing attribute/method in model
            raise ModelStructureError(
                f"Step '{step.name}' tried to access missing attribute: {e}"
            ) from e

        except TypeError as e:
            # Method signature issue
            raise ModelStructureError(
                f"Step '{step.name}' has invalid signature: {e}"
            ) from e

        except KeyboardInterrupt:
            # User interrupted
            raise

        except Exception as e:
            # Other runtime errors
            return self._handle_error(
                step=step,
                error=e,
                error_type=ErrorType.RUNTIME,
                strategy=error_strategy
            )

    def _handle_error(
        self,
        step: TestStep,
        error: Exception,
        error_type: ErrorType,
        strategy: ErrorStrategy
    ) -> StepResult:
        """Handle error according to strategy."""
        if strategy.should_raise(error_type):
            raise StepExecutionError(
                step_name=step.name,
                original_error=error,
                context=self._capture_context()
            ) from error

        return StepResult(
            step_name=step.name,
            success=False,
            error=error,
            error_type=error_type
        )
```

**Benefits**:
- ✅ Clear error types and causes
- ✅ Proper error chaining with `from`
- ✅ Detailed error context
- ✅ Strategy-based error handling
- ✅ Keyboard interrupt preserved

---

### 2.3 Input Validation

#### Current: Limited Validation

```python
# Current minimal validation
def set_algorithm(self, algorithm):
    if not isinstance(algorithm, Algorithm):
        raise AttributeError("Must be Algorithm instance")
    self._algorithm = algorithm
```

#### Proposed: Comprehensive Validation

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class AlgorithmProtocol(Protocol):
    """Protocol for test generation algorithms."""

    def select_step(
        self,
        enabled_steps: List[TestStep],
        history: OsmoHistory
    ) -> TestStep:
        """Select next step to execute."""
        ...


class ConfigValidator:
    """Validates configuration values."""

    @staticmethod
    def validate_seed(seed: Optional[int]) -> None:
        """Validate random seed."""
        if seed is None:
            return

        if not isinstance(seed, int):
            raise ConfigurationError(
                f"Seed must be an integer, got {type(seed).__name__}"
            )

        if seed < 0:
            raise ConfigurationError(
                f"Seed must be non-negative, got {seed}"
            )

        if seed > 2**32 - 1:
            raise ConfigurationError(
                f"Seed must fit in 32 bits, got {seed}"
            )

    @staticmethod
    def validate_algorithm(algorithm: Any) -> None:
        """Validate algorithm."""
        if algorithm is None:
            return

        # Check protocol compliance
        if not isinstance(algorithm, AlgorithmProtocol):
            raise ConfigurationError(
                f"Algorithm must implement AlgorithmProtocol, "
                f"got {type(algorithm).__name__}"
            )

    @staticmethod
    def validate_end_condition(condition: Any) -> None:
        """Validate end condition."""
        if condition is None:
            raise ConfigurationError("End condition cannot be None")

        if not isinstance(condition, EndCondition):
            raise ConfigurationError(
                f"End condition must extend EndCondition, "
                f"got {type(condition).__name__}"
            )

        # Validate condition's internal state
        try:
            condition.validate()
        except NotImplementedError:
            pass  # Validation not implemented


class OsmoConfig:
    """Configuration with validation."""

    @property
    def seed(self) -> Optional[int]:
        return self._seed

    @seed.setter
    def seed(self, value: Optional[int]) -> None:
        ConfigValidator.validate_seed(value)
        self._seed = value
```

**Benefits**:
- ✅ Fail fast with clear errors
- ✅ Type-safe with protocols
- ✅ Comprehensive validation
- ✅ Better error messages

---

## 3. Plugin Architecture Enhancement

### 3.1 Current Plugin System

**Current**: Inheritance-based plugins work but lack discoverability

### 3.2 Enhanced Plugin Registry

```python
from typing import Type, Dict, Callable
from abc import ABC, abstractmethod

class PluginRegistry:
    """Central registry for all plugins."""

    def __init__(self):
        self._algorithms: Dict[str, Type[Algorithm]] = {}
        self._end_conditions: Dict[str, Type[EndCondition]] = {}
        self._error_strategies: Dict[str, Type[ErrorStrategy]] = {}

    def register_algorithm(
        self,
        name: str,
        algorithm_class: Type[Algorithm],
        *,
        description: str = ""
    ) -> None:
        """Register a test generation algorithm.

        Args:
            name: Unique name for this algorithm
            algorithm_class: Algorithm class
            description: Human-readable description
        """
        if name in self._algorithms:
            raise PluginError(f"Algorithm '{name}' already registered")

        # Validate it's a proper algorithm
        if not issubclass(algorithm_class, Algorithm):
            raise PluginError(
                f"{algorithm_class} must extend Algorithm"
            )

        self._algorithms[name] = algorithm_class

    def get_algorithm(self, name: str) -> Type[Algorithm]:
        """Get algorithm class by name."""
        if name not in self._algorithms:
            available = ', '.join(self._algorithms.keys())
            raise PluginError(
                f"Algorithm '{name}' not found. "
                f"Available: {available}"
            )
        return self._algorithms[name]

    def list_algorithms(self) -> Dict[str, Type[Algorithm]]:
        """List all registered algorithms."""
        return self._algorithms.copy()


# Global registry
registry = PluginRegistry()


# Decorator for easy registration
def register_algorithm(name: str, description: str = ""):
    """Decorator to register an algorithm."""
    def decorator(cls: Type[Algorithm]) -> Type[Algorithm]:
        registry.register_algorithm(name, cls, description=description)
        return cls
    return decorator


# Usage
@register_algorithm("random", "Purely random step selection")
class RandomAlgorithm(Algorithm):
    ...

@register_algorithm("balancing", "Coverage-balancing algorithm")
class BalancingAlgorithm(Algorithm):
    ...
```

### 3.3 Plugin Discovery

```python
# pyosmo/plugins/__init__.py

def discover_plugins(package_name: str = "pyosmo_plugins"):
    """Discover and load plugins from external packages.

    Plugins should be in packages named pyosmo_plugins_* and
    register themselves when imported.

    Example plugin structure:
        pyosmo_plugins_custom/
        └── __init__.py  # Registers algorithms on import
    """
    import pkgutil
    import importlib

    # Find all packages matching pattern
    for finder, name, ispkg in pkgutil.iter_modules():
        if name.startswith(package_name):
            try:
                importlib.import_module(name)
            except ImportError as e:
                warnings.warn(f"Failed to load plugin {name}: {e}")


# Auto-discover on import
discover_plugins()
```

**Benefits**:
- ✅ Centralized plugin management
- ✅ Easy plugin discovery via CLI
- ✅ External plugin support
- ✅ Clear registration API

---

## 4. Model Discovery & Introspection

### 4.1 Current Issues

- Uses `dir()` string matching (fragile)
- No validation before execution
- Hard to extend discovery mechanisms
- No caching

### 4.2 Proposed: Multi-Strategy Discovery

```python
from abc import ABC, abstractmethod
from typing import List, Protocol

class DiscoveryStrategy(ABC):
    """Base class for model discovery strategies."""

    @abstractmethod
    def discover_steps(self, model: object) -> List[TestStep]:
        """Discover test steps in model."""
        ...

    @abstractmethod
    def discover_guards(self, model: object) -> Dict[str, Callable]:
        """Discover guard functions."""
        ...


class NamingConventionDiscovery(DiscoveryStrategy):
    """Discover via step_*, guard_*, weight_* naming."""

    def discover_steps(self, model: object) -> List[TestStep]:
        """Discover steps via naming convention."""
        # Robust implementation from section 2.1
        ...


class DecoratorBasedDiscovery(DiscoveryStrategy):
    """Discover via @step, @guard decorators."""

    def discover_steps(self, model: object) -> List[TestStep]:
        """Discover steps via decorators."""
        steps = []

        for name, method in inspect.getmembers(model, inspect.ismethod):
            if hasattr(method, '_osmo_step'):
                steps.append(TestStep(
                    name=method._osmo_step_name,
                    method=method,
                    metadata=method._osmo_metadata
                ))

        return steps


class ModelDiscovery:
    """Orchestrates multiple discovery strategies."""

    def __init__(self, strategies: List[DiscoveryStrategy] = None):
        self.strategies = strategies or [
            DecoratorBasedDiscovery(),  # Try decorators first
            NamingConventionDiscovery(),  # Fall back to naming
        ]

    def discover(self, model: object) -> ModelMetadata:
        """Discover all model components."""
        all_steps = []
        all_guards = {}

        for strategy in self.strategies:
            steps = strategy.discover_steps(model)
            guards = strategy.discover_guards(model)

            all_steps.extend(steps)
            all_guards.update(guards)

        # Remove duplicates (decorator and naming might overlap)
        unique_steps = self._deduplicate_steps(all_steps)

        return ModelMetadata(
            steps=unique_steps,
            guards=all_guards,
            model=model
        )
```

**Benefits**:
- ✅ Multiple discovery mechanisms
- ✅ Easy to add new strategies
- ✅ Handles decorator + naming coexistence
- ✅ Deduplication built-in

---

## 5. Event System

### 5.1 Motivation

Enable:
- Custom logging
- Metrics collection
- Real-time monitoring
- Progress bars
- External integrations

### 5.2 Event-Based Architecture

```python
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Any, List

class EventType(Enum):
    """Types of events emitted during test execution."""
    SUITE_STARTED = "suite_started"
    SUITE_ENDED = "suite_ended"
    TEST_STARTED = "test_started"
    TEST_ENDED = "test_ended"
    STEP_STARTED = "step_started"
    STEP_ENDED = "step_ended"
    STEP_SELECTED = "step_selected"
    GUARD_EVALUATED = "guard_evaluated"
    ERROR_OCCURRED = "error_occurred"
    COVERAGE_MILESTONE = "coverage_milestone"


@dataclass
class Event:
    """Base event class."""
    type: EventType
    timestamp: float
    data: Dict[str, Any]


class EventBus:
    """Central event bus for pub/sub."""

    def __init__(self):
        self._listeners: Dict[EventType, List[Callable]] = {}

    def subscribe(
        self,
        event_type: EventType,
        callback: Callable[[Event], None]
    ) -> None:
        """Subscribe to an event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        listeners = self._listeners.get(event.type, [])
        for listener in listeners:
            try:
                listener(event)
            except Exception as e:
                # Don't let listener errors break execution
                logging.error(f"Event listener error: {e}")


class EventEmitter:
    """Mixin for classes that emit events."""

    def __init__(self):
        self.event_bus = EventBus()

    def emit(self, event_type: EventType, **data) -> None:
        """Emit an event."""
        event = Event(
            type=event_type,
            timestamp=time.time(),
            data=data
        )
        self.event_bus.publish(event)
```

### 5.3 Usage Examples

```python
# Built-in listeners

class ProgressBarListener:
    """Display progress bar during test execution."""

    def __init__(self, total_steps: int):
        self.pbar = tqdm(total=total_steps)

    def on_step_ended(self, event: Event) -> None:
        self.pbar.update(1)
        self.pbar.set_description(f"Step: {event.data['step_name']}")


class MetricsCollector:
    """Collect metrics for analysis."""

    def __init__(self):
        self.step_timings = []

    def on_step_ended(self, event: Event) -> None:
        self.step_timings.append({
            'step': event.data['step_name'],
            'duration': event.data['duration']
        })


# User code
osmo = Osmo(model)

# Add progress bar
progress = ProgressBarListener(total_steps=100)
osmo.event_bus.subscribe(EventType.STEP_ENDED, progress.on_step_ended)

# Collect metrics
metrics = MetricsCollector()
osmo.event_bus.subscribe(EventType.STEP_ENDED, metrics.on_step_ended)

osmo.run()

# Analyze metrics
import pandas as pd
df = pd.DataFrame(metrics.step_timings)
print(df.groupby('step')['duration'].mean())
```

**Benefits**:
- ✅ Decoupled monitoring/logging
- ✅ Easy to add custom listeners
- ✅ No performance impact if no listeners
- ✅ Enables rich integrations

---

## 6. Performance Optimizations

### 6.1 Lazy Evaluation

```python
class LazyModelCollector:
    """Model collector with lazy evaluation."""

    def __init__(self, model: object):
        self.model = model
        self._steps: Optional[List[TestStep]] = None
        self._guards: Optional[Dict[str, Callable]] = None

    @property
    def steps(self) -> List[TestStep]:
        """Lazily discover steps."""
        if self._steps is None:
            self._steps = self._discover_steps()
        return self._steps
```

### 6.2 Algorithm Optimizations

```python
class OptimizedWeightedAlgorithm(WeightedAlgorithm):
    """Weighted algorithm with optimization."""

    def __init__(self):
        super().__init__()
        self._weight_cache: Dict[str, float] = {}

    def select_step(
        self,
        enabled_steps: List[TestStep],
        history: OsmoHistory
    ) -> TestStep:
        """Select step with cached weights."""
        # Build weight array (cached)
        weights = []
        for step in enabled_steps:
            if step.name not in self._weight_cache:
                self._weight_cache[step.name] = step.get_weight()
            weights.append(self._weight_cache[step.name])

        # Select using numpy for speed
        import numpy as np
        weights_array = np.array(weights)
        probs = weights_array / weights_array.sum()
        idx = np.random.choice(len(enabled_steps), p=probs)

        return enabled_steps[idx]
```

### 6.3 History Optimization

```python
class OptimizedHistory(OsmoHistory):
    """History with efficient storage."""

    def __init__(self):
        super().__init__()
        self._step_counts: Counter = Counter()
        self._step_pairs: Counter = Counter()

    def add_step(self, step_name: str) -> None:
        """Add step with O(1) counting."""
        self._step_counts[step_name] += 1

        if self._last_step:
            self._step_pairs[(self._last_step, step_name)] += 1

        self._last_step = step_name

    def step_coverage_percentage(self) -> float:
        """Calculate coverage in O(1)."""
        return (len(self._step_counts) / self._total_steps) * 100
```

**Benefits**:
- ✅ Faster execution for large models
- ✅ Reduced memory usage
- ✅ Cached guard evaluation
- ✅ Efficient data structures

---

## 7. Testing Infrastructure

### 7.1 Enhanced Test Utilities

```python
# pyosmo/testing/__init__.py

class ModelTester:
    """Test utility for model developers."""

    def __init__(self, model: object):
        self.model = model
        self.collector = OsmoModelCollector(model)

    def assert_steps_discovered(self, expected: List[str]) -> None:
        """Assert expected steps are discovered."""
        actual = [step.name for step in self.collector.steps]
        assert set(actual) == set(expected), \
            f"Expected steps {expected}, got {actual}"

    def assert_guard_behavior(
        self,
        step_name: str,
        initial_state: Dict[str, Any],
        expected: bool
    ) -> None:
        """Assert guard returns expected value in given state."""
        # Set model state
        for key, value in initial_state.items():
            setattr(self.model, key, value)

        # Evaluate guard
        guard = self.collector.get_guard(step_name)
        actual = guard() if guard else True

        assert actual == expected, \
            f"Guard for {step_name} returned {actual}, expected {expected}"

    def simulate_step_sequence(
        self,
        steps: List[str]
    ) -> None:
        """Simulate a specific step sequence."""
        for step_name in steps:
            step = self.collector.get_step(step_name)
            step.execute(self.model)


# Usage in tests
def test_calculator_model():
    model = CalculatorModel()
    tester = ModelTester(model)

    # Test step discovery
    tester.assert_steps_discovered(['increase', 'decrease'])

    # Test guard behavior
    tester.assert_guard_behavior(
        'decrease',
        initial_state={'counter': 0},
        expected=False
    )

    tester.assert_guard_behavior(
        'decrease',
        initial_state={'counter': 5},
        expected=True
    )

    # Test step sequence
    tester.simulate_step_sequence(['increase', 'increase', 'decrease'])
    assert model.counter == 1
```

### 7.2 Property-Based Testing Integration

```python
from hypothesis import given, strategies as st

@given(
    steps=st.lists(st.sampled_from(['increase', 'decrease']), min_size=10, max_size=100),
    seed=st.integers(min_value=0, max_value=2**32-1)
)
def test_model_never_crashes(steps, seed):
    """Model should never crash regardless of step sequence."""
    osmo = Osmo(CalculatorModel())
    osmo.seed = seed
    osmo.error_strategy = AlwaysIgnore()  # Ignore assertion errors

    try:
        osmo.run()
    except Exception as e:
        raise AssertionError(f"Model crashed: {e}")
```

---

## 8. Logging & Debugging

### 8.1 Structured Logging

```python
import logging
import json
from typing import Any, Dict

class StructuredLogger:
    """JSON-structured logging for better parsing."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log(
        self,
        level: int,
        message: str,
        **context: Any
    ) -> None:
        """Log with structured context."""
        record = {
            'message': message,
            'timestamp': time.time(),
            **context
        }
        self.logger.log(level, json.dumps(record))

    def step_executed(
        self,
        step_name: str,
        duration: float,
        test_index: int,
        step_index: int
    ) -> None:
        """Log step execution."""
        self.log(
            logging.INFO,
            "Step executed",
            step_name=step_name,
            duration=duration,
            test_index=test_index,
            step_index=step_index,
            event_type="step_executed"
        )


# Configure structured logging
logging.basicConfig(
    format='%(message)s',  # Just JSON, no extra formatting
    level=logging.INFO,
    handlers=[
        logging.FileHandler('osmo.jsonl'),  # JSON lines format
        logging.StreamHandler()
    ]
)
```

### 8.2 Debug Mode

```python
class Osmo:
    """Enhanced with debug mode."""

    def __init__(self, model, *, debug: bool = False):
        self.debug = debug
        if debug:
            self._setup_debug_mode()

    def _setup_debug_mode(self) -> None:
        """Configure debug mode."""
        # Enable verbose logging
        logging.getLogger('pyosmo').setLevel(logging.DEBUG)

        # Add debug event listeners
        self.event_bus.subscribe(
            EventType.STEP_SELECTED,
            self._log_step_selection
        )

        self.event_bus.subscribe(
            EventType.GUARD_EVALUATED,
            self._log_guard_evaluation
        )

    def _log_step_selection(self, event: Event) -> None:
        """Log algorithm's step selection."""
        print(f"  Algorithm selected: {event.data['step_name']}")
        print(f"  From candidates: {event.data['candidates']}")
        print(f"  Weights: {event.data['weights']}")

    def _log_guard_evaluation(self, event: Event) -> None:
        """Log guard evaluation."""
        print(f"  Guard {event.data['guard_name']}: {event.data['result']}")


# Usage
osmo = Osmo(model, debug=True)
osmo.run()
```

---

## Implementation Roadmap

| Improvement | Priority | Effort | Phase |
|-------------|----------|--------|-------|
| Fix fragile introspection | P0 | 3 days | 1 |
| Replace bare exceptions | P0 | 2 days | 1 |
| Add input validation | P1 | 3 days | 1 |
| Plugin registry | P2 | 1 week | 2 |
| Multi-strategy discovery | P1 | 1 week | 2 |
| Event system | P2 | 1 week | 2 |
| Performance optimizations | P2 | 1 week | 3 |
| Testing utilities | P2 | 3 days | 3 |
| Structured logging | P2 | 2 days | 3 |
| **Total** | | **~6 weeks** | |

---

## Success Metrics

### Code Quality
- [ ] Zero bare `except:` clauses
- [ ] All public APIs have input validation
- [ ] Type hints: 90%+ coverage
- [ ] Mutation test score: 75%+

### Performance
- [ ] Step discovery: < 1ms for 100 steps
- [ ] Guard evaluation: < 0.1ms per guard
- [ ] History tracking: O(1) for common operations

### Extensibility
- [ ] Plugin system documented and tested
- [ ] At least 2 external plugins created
- [ ] Event system has 5+ useful listeners

### Maintainability
- [ ] Code duplication: < 5%
- [ ] Cyclomatic complexity: < 10 per function
- [ ] Clear separation of concerns

---

## Conclusion

These architectural improvements will:

1. **Improve Robustness** - Better error handling and validation
2. **Enhance Extensibility** - Plugin system and event bus
3. **Increase Performance** - Caching and optimization
4. **Better Developer Experience** - Testing utilities and debugging tools
5. **Future-Proof** - Clean architecture enables growth

All improvements can be implemented incrementally while maintaining backward compatibility.

---

*Document Version: 1.0*
*Last Updated: 2025-11-05*
*Next Review: End of Phase 1*
