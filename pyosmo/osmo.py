import json
import logging
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path
from random import Random
from typing import TYPE_CHECKING

from pyosmo.config import OsmoConfig
from pyosmo.history.history import OsmoHistory
from pyosmo.model import OsmoModelCollector, TestStep

if TYPE_CHECKING:
    from pyosmo.algorithm.base import OsmoAlgorithm
    from pyosmo.end_conditions.base import OsmoEndCondition
    from pyosmo.error_strategy.base import OsmoErrorStrategy

logger = logging.getLogger('osmo')


class Osmo(OsmoConfig):
    """
    Osmo tester core - Model-Based Testing framework.

    This class provides the main interface for configuring and running
    model-based tests. It manages test execution, model collection,
    and test history tracking.
    """

    def __init__(self, model: object | list[object] | None = None) -> None:
        """
        Initialize Osmo with an optional model.

        Args:
            model: Optional model instance or list of model instances containing test steps and guards
        """
        super().__init__()
        self.model = OsmoModelCollector()
        self.runs: list[OsmoHistory] = []
        self._capture_callbacks: list[Callable[[], dict[str, str | bytes]]] = []
        self.history = OsmoHistory()
        if model:
            if isinstance(model, list):
                for m in model:
                    self.add_model(m)
            else:
                self.add_model(model)

    @property
    def seed(self) -> int:
        return self._seed

    @seed.setter
    def seed(self, value: int) -> None:
        """Set random seed for test generation with validation.

        Args:
            value: Random seed value (must be non-negative int that fits in 32 bits)

        Raises:
            ConfigurationError: If seed value is invalid
        """
        from pyosmo.config import ConfigValidator

        ConfigValidator.validate_seed(value)
        logger.debug(f'Set seed: {value}')
        self._seed = value
        self._random = Random(self._seed)
        # update osmo_random in all models
        for model in self.model.sub_models:
            model.osmo_random = self._random  # type: ignore[attr-defined]

    @staticmethod
    def _check_model(model: object) -> None:
        """Check that model is valid"""
        if not hasattr(model, '__class__'):
            raise Exception('Osmo model need to be instance of model, not just class')

    def add_model(self, model: object) -> None:
        """Add model for osmo"""
        logger.debug(f'Add model:{model}')
        self._check_model(model)
        # Set osmo_random
        model.osmo_random = self._random  # type: ignore[attr-defined]
        model.osmo_history = self.history  # type: ignore[attr-defined]
        self.model.add_model(model)

    def _run_step(self, step: TestStep) -> None:
        """
        Run step and save it to the history.

        Args:
            step: Test step to execute

        Raises:
            KeyboardInterrupt: User interrupted execution (preserved)
            Exception: Any error during step execution (with proper error chaining)
        """
        logger.debug(f'Run step: {step}')
        start_time = datetime.now()
        error = None
        try:
            step.execute()
        except KeyboardInterrupt:
            # Record step without error and re-raise immediately
            self.history.add_step(step, datetime.now() - start_time)
            raise
        except Exception as e:
            error = e

        duration = datetime.now() - start_time
        self.history.add_step(step, duration, error)

        if error is None:
            return

        if isinstance(error, AttributeError):
            raise RuntimeError(
                f"Step '{step}' tried to access missing attribute. Check your model implementation."
            ) from error
        if isinstance(error, TypeError):
            raise RuntimeError(
                f"Step '{step}' has invalid signature or type mismatch. Check your step method implementation."
            ) from error
        logger.debug(f'Step {step} failed with {type(error).__name__}: {error}')
        raise error

    def run(self) -> None:
        """Same as generate but in online usage this sounds more natural"""
        self.generate()

    def generate(self) -> None:
        """Generate / run tests"""
        self.history = OsmoHistory()  # Restart the history
        # Re-inject osmo_history into all models
        for sub_model in self.model.sub_models:
            sub_model.osmo_history = self.history  # type: ignore[attr-defined]
        # Propagate timeout to model collector and cached steps
        self.model.timeout = self._timeout
        self.model._cache_valid = False  # Force step re-discovery with new timeout
        logger.debug('Start generation..')
        logger.info(f'Using seed: {self.seed}')
        # Initialize algorithm
        self.algorithm.initialize(self.random, self.model)

        self.model.execute_optional('before_suite')
        if not self.model.all_steps:
            raise Exception('Empty model!')

        while True:
            try:
                self.history.start_new_test()
                self.model.execute_optional('before_test')
                while True:
                    # Use algorithm to select the step
                    self.model.execute_optional('before')
                    available = self.model.available_steps
                    if not available:
                        raise Exception('No steps available! All guards returned False.')
                    step = self.algorithm.choose(self.history, available)
                    self.model.execute_optional(f'pre_{step}')
                    try:
                        self._run_step(step)
                    except KeyboardInterrupt:
                        # User interrupted - re-raise immediately
                        raise
                    except BaseException as error:
                        # Let error strategy decide how to handle
                        self.test_error_strategy.failure_in_test(self.history, self.model, error)
                    # Run capture callbacks after each step
                    for callback in self._capture_callbacks:
                        for att_name, att_data in callback().items():
                            self.history.attach(att_name, att_data)
                    self.model.execute_optional(f'post_{step.name}')
                    # General after step which is run after each step
                    self.model.execute_optional('after')

                    if self.test_end_condition.end_test(self.history, self.model):
                        break
                self.model.execute_optional('after_test')
            except KeyboardInterrupt:
                # User interrupted - re-raise immediately without error strategy processing
                raise
            except BaseException as error:
                # Let suite error strategy decide how to handle
                self.test_suite_error_strategy.failure_in_suite(self.history, self.model, error)
            if self.test_suite_end_condition.end_suite(self.history, self.model):
                break
        self.model.execute_optional('after_suite')
        self.history.stop()
        self.runs.append(self.history)

    # Fluent Configuration API

    def with_seed(self, seed: int) -> 'Osmo':
        """
        Set random seed for test generation (fluent API).

        Args:
            seed: Random seed value

        Returns:
            Self for method chaining
        """
        self.seed = seed
        return self

    def with_algorithm(self, algorithm: 'OsmoAlgorithm') -> 'Osmo':
        """
        Set test generation algorithm (fluent API).

        Args:
            algorithm: Algorithm instance

        Returns:
            Self for method chaining
        """
        self.algorithm = algorithm
        return self

    def with_test_end_condition(self, condition: 'OsmoEndCondition') -> 'Osmo':
        """
        Set test end condition (fluent API).

        Args:
            condition: End condition instance

        Returns:
            Self for method chaining
        """
        self.test_end_condition = condition
        return self

    def with_suite_end_condition(self, condition: 'OsmoEndCondition') -> 'Osmo':
        """
        Set test suite end condition (fluent API).

        Args:
            condition: End condition instance

        Returns:
            Self for method chaining
        """
        self.test_suite_end_condition = condition
        return self

    def on_error(self, strategy: 'OsmoErrorStrategy') -> 'Osmo':
        """
        Set error handling strategy for both test and suite levels (fluent API).

        Args:
            strategy: Error strategy instance

        Returns:
            Self for method chaining
        """
        self.test_error_strategy = strategy
        self.test_suite_error_strategy = strategy
        return self

    def on_test_error(self, strategy: 'OsmoErrorStrategy') -> 'Osmo':
        """
        Set error handling strategy for test level (fluent API).

        Args:
            strategy: Error strategy instance

        Returns:
            Self for method chaining
        """
        self.test_error_strategy = strategy
        return self

    def on_suite_error(self, strategy: 'OsmoErrorStrategy') -> 'Osmo':
        """
        Set error handling strategy for suite level (fluent API).

        Args:
            strategy: Error strategy instance

        Returns:
            Self for method chaining
        """
        self.test_suite_error_strategy = strategy
        return self

    def capture_after_step(self, callback: Callable[[], dict[str, str | bytes]]) -> 'Osmo':
        """Register a callback to capture attachments after each step (fluent API).

        The callback is called after every step execution. It should return a dict
        mapping attachment names to data (str for text, bytes for binary).

        Args:
            callback: Callable returning dict of attachment name to data

        Returns:
            Self for method chaining
        """
        self._capture_callbacks.append(callback)
        return self

    def generate_and_save(self, directory: str | Path, runs: int = 10) -> None:
        """Run generate() multiple times and save all results to a directory.

        Args:
            directory: Output directory for all run data
            runs: Number of generate() runs (default: 10)
        """
        for _ in range(runs):
            self.generate()
        self.save_runs(directory)

    def save_runs(self, directory: str | Path) -> None:
        """Save all accumulated runs to a directory with summary.

        Creates:
            directory/
                summary.json    — cross-run flakiness analysis
                run_0/          — per-run history + attachments
                run_1/
                ...
        """
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        for run_index, run_history in enumerate(self.runs):
            run_history.save(directory / f'run_{run_index}')

        # Build summary with flakiness analysis
        step_results: dict[str, dict[str, int]] = {}
        step_frequency: dict[str, int] = {}

        for run_history in self.runs:
            # Track which steps passed/failed in this run
            run_step_errors: dict[str, bool] = {}
            for tc in run_history.test_cases:
                for step_log in tc.steps_log:
                    name = step_log.name
                    step_frequency[name] = step_frequency.get(name, 0) + 1
                    if step_log.error is not None:
                        run_step_errors[name] = True
                    elif name not in run_step_errors:
                        run_step_errors[name] = False

            for name, had_error in run_step_errors.items():
                if name not in step_results:
                    step_results[name] = {'pass': 0, 'fail': 0}
                if had_error:
                    step_results[name]['fail'] += 1
                else:
                    step_results[name]['pass'] += 1

        flaky_steps = [name for name, counts in step_results.items() if counts['pass'] > 0 and counts['fail'] > 0]

        summary = {
            'total_runs': len(self.runs),
            'step_results': step_results,
            'step_frequency': step_frequency,
            'flaky_steps': flaky_steps,
        }

        (directory / 'summary.json').write_text(json.dumps(summary, indent=2))

    def build(self) -> 'Osmo':
        """
        Finalize configuration and return the Osmo instance (fluent API).

        This method exists for API consistency and simply returns self.
        It can be used as the final call in a fluent chain.

        Returns:
            Self
        """
        return self

    # Convenience fluent methods (more fluent API)

    def random_algorithm(self, seed: int | None = None) -> 'Osmo':
        """
        Use random algorithm with optional seed (convenience fluent API).

        Args:
            seed: Optional random seed. If provided, also sets the seed.

        Returns:
            Self for method chaining
        """
        from pyosmo.algorithm import RandomAlgorithm

        self.algorithm = RandomAlgorithm()
        if seed is not None:
            self.seed = seed
        return self

    def balancing_algorithm(self, seed: int | None = None) -> 'Osmo':
        """
        Use balancing algorithm with optional seed (convenience fluent API).

        Args:
            seed: Optional random seed. If provided, also sets the seed.

        Returns:
            Self for method chaining
        """
        from pyosmo.algorithm import BalancingAlgorithm

        self.algorithm = BalancingAlgorithm()
        if seed is not None:
            self.seed = seed
        return self

    def weighted_algorithm(self, seed: int | None = None) -> 'Osmo':
        """
        Use weighted algorithm with optional seed (convenience fluent API).

        Args:
            seed: Optional random seed. If provided, also sets the seed.

        Returns:
            Self for method chaining
        """
        from pyosmo.algorithm import WeightedAlgorithm

        self.algorithm = WeightedAlgorithm()
        if seed is not None:
            self.seed = seed
        return self

    def stop_after_steps(self, steps: int) -> 'Osmo':
        """
        Stop each test after N steps (convenience fluent API).

        Args:
            steps: Number of steps per test

        Returns:
            Self for method chaining
        """
        from pyosmo.end_conditions import Length

        self.test_end_condition = Length(steps)
        return self

    def stop_after_time(self, seconds: int) -> 'Osmo':
        """
        Stop each test after N seconds (convenience fluent API).

        Args:
            seconds: Maximum test duration in seconds

        Returns:
            Self for method chaining
        """
        from pyosmo.end_conditions import Time

        self.test_end_condition = Time(timedelta(seconds=seconds))
        return self

    def run_tests(self, count: int) -> 'Osmo':
        """
        Run N tests in the suite (convenience fluent API).

        Args:
            count: Number of tests to run

        Returns:
            Self for method chaining
        """
        from pyosmo.end_conditions import Length

        self.test_suite_end_condition = Length(count)
        return self

    def run_endless(self) -> 'Osmo':
        """
        Run tests endlessly (convenience fluent API).

        Note: You'll need to manually interrupt execution (Ctrl+C).

        Returns:
            Self for method chaining
        """
        from pyosmo.end_conditions import Endless

        self.test_suite_end_condition = Endless()
        return self

    def raise_on_error(self) -> 'Osmo':
        """
        Raise exceptions immediately when errors occur (convenience fluent API).

        Returns:
            Self for method chaining
        """
        from pyosmo.error_strategy import AlwaysRaise

        return self.on_error(AlwaysRaise())

    def ignore_errors(self, max_count: int | None = None) -> 'Osmo':
        """
        Ignore errors during test execution (convenience fluent API).

        Args:
            max_count: Optional maximum number of errors to ignore.
                      If None, all errors are ignored.

        Returns:
            Self for method chaining
        """
        if max_count is None:
            from pyosmo.error_strategy import AlwaysIgnore

            return self.on_error(AlwaysIgnore())
        from pyosmo.error_strategy import AllowCount

        return self.on_error(AllowCount(max_count))

    def ignore_asserts(self) -> 'Osmo':
        """
        Ignore assertion errors but raise other exceptions (convenience fluent API).

        Returns:
            Self for method chaining
        """
        from pyosmo.error_strategy import IgnoreAsserts

        return self.on_error(IgnoreAsserts())

    def with_timeout(self, seconds: float | None) -> 'Osmo':
        """
        Set timeout for model function calls (fluent API).

        Args:
            seconds: Timeout in seconds (positive number) or None to disable

        Returns:
            Self for method chaining
        """
        self.timeout = seconds
        return self
