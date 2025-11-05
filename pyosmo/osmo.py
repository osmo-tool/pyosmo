# pylint: disable=bare-except,broad-except,too-many-instance-attributes
import logging
from datetime import datetime, timedelta
from random import Random
from typing import Optional, Union, List

from pyosmo.config import OsmoConfig
from pyosmo.history.history import OsmoHistory
from pyosmo.model import OsmoModelCollector, TestStep

logger = logging.getLogger("osmo")


class Osmo(OsmoConfig):
    """
    Osmo tester core - Model-Based Testing framework.

    This class provides the main interface for configuring and running
    model-based tests. It manages test execution, model collection,
    and test history tracking.
    """

    def __init__(self, model: Optional[Union[object, List[object]]] = None) -> None:
        """
        Initialize Osmo with an optional model.

        Args:
            model: Optional model instance or list of model instances containing test steps and guards
        """
        super().__init__()
        self.model = OsmoModelCollector()
        if model:
            if isinstance(model, list):
                for m in model:
                    self.add_model(m)
            else:
                self.add_model(model)
        self.history = OsmoHistory()

    @property
    def seed(self) -> int:
        return self._seed

    @seed.setter
    def seed(self, value: int) -> None:
        """Set random seed for test generation"""
        logger.debug(f"Set seed: {value}")
        if not isinstance(value, int):
            raise AttributeError("Seed value must be an integer.")
        self._seed = value
        self._random = Random(self._seed)
        # update osmo_random in all models
        for model in self.model.sub_models:
            model.osmo_random = self._random  # type: ignore[attr-defined]

    @staticmethod
    def _check_model(model: object) -> None:
        """Check that model is valid"""
        if not hasattr(model, "__class__"):
            raise Exception("Osmo model need to be instance of model, not just class")

    def add_model(self, model: object) -> None:
        """Add model for osmo"""
        logger.debug(f"Add model:{model}")
        self._check_model(model)
        # Set osmo_random
        model.osmo_random = self._random  # type: ignore[attr-defined]
        self.model.add_model(model)

    def _run_step(self, step: TestStep) -> None:
        """
        Run step and save it to the history
        :param step: Test step
        :return:
        """
        logger.debug(f"Run step: {step}")
        start_time = datetime.now()
        try:
            step.execute()
            self.history.add_step(step, datetime.now() - start_time)
        except Exception as error:
            self.history.add_step(step, datetime.now() - start_time, error)
            raise error

    def run(self) -> None:
        """Same as generate but in online usage this sounds more natural"""
        self.generate()

    def generate(self) -> None:
        """Generate / run tests"""
        self.history = OsmoHistory()  # Restart the history
        logger.debug("Start generation..")
        logger.info(f"Using seed: {self.seed}")
        # Initialize algorithm
        self.algorithm.initialize(self.random, self.model)

        self.model.execute_optional("before_suite")
        if not self.model.all_steps:
            raise Exception("Empty model!")

        while True:
            try:
                self.history.start_new_test()
                self.model.execute_optional("before_test")
                while True:
                    # Use algorithm to select the step
                    self.model.execute_optional("before")
                    step = self.algorithm.choose(self.history, self.model.available_steps)
                    self.model.execute_optional(f"pre_{step}")
                    try:
                        self._run_step(step)
                    except BaseException as error:
                        self.test_error_strategy.failure_in_test(self.history, self.model, error)
                    self.model.execute_optional(f"post_{step.name}")
                    # General after step which is run after each step
                    self.model.execute_optional("after")

                    if self.test_end_condition.end_test(self.history, self.model):
                        break
                self.model.execute_optional("after_test")
            except BaseException as error:
                self.test_suite_error_strategy.failure_in_suite(self.history, self.model, error)
            if self.test_suite_end_condition.end_suite(self.history, self.model):
                break
        self.model.execute_optional("after_suite")
        self.history.stop()

    # Fluent Configuration API

    def with_seed(self, seed: int) -> "Osmo":
        """
        Set random seed for test generation (fluent API).

        Args:
            seed: Random seed value

        Returns:
            Self for method chaining
        """
        self.seed = seed
        return self

    def with_algorithm(self, algorithm: "OsmoAlgorithm") -> "Osmo":
        """
        Set test generation algorithm (fluent API).

        Args:
            algorithm: Algorithm instance

        Returns:
            Self for method chaining
        """
        self.algorithm = algorithm
        return self

    def with_test_end_condition(self, condition: "OsmoEndCondition") -> "Osmo":
        """
        Set test end condition (fluent API).

        Args:
            condition: End condition instance

        Returns:
            Self for method chaining
        """
        self.test_end_condition = condition
        return self

    def with_suite_end_condition(self, condition: "OsmoEndCondition") -> "Osmo":
        """
        Set test suite end condition (fluent API).

        Args:
            condition: End condition instance

        Returns:
            Self for method chaining
        """
        self.test_suite_end_condition = condition
        return self

    def on_error(self, strategy: "OsmoErrorStrategy") -> "Osmo":
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

    def on_test_error(self, strategy: "OsmoErrorStrategy") -> "Osmo":
        """
        Set error handling strategy for test level (fluent API).

        Args:
            strategy: Error strategy instance

        Returns:
            Self for method chaining
        """
        self.test_error_strategy = strategy
        return self

    def on_suite_error(self, strategy: "OsmoErrorStrategy") -> "Osmo":
        """
        Set error handling strategy for suite level (fluent API).

        Args:
            strategy: Error strategy instance

        Returns:
            Self for method chaining
        """
        self.test_suite_error_strategy = strategy
        return self

    def build(self) -> "Osmo":
        """
        Finalize configuration and return the Osmo instance (fluent API).

        This method exists for API consistency and simply returns self.
        It can be used as the final call in a fluent chain.

        Returns:
            Self
        """
        return self

    # Convenience fluent methods (more fluent API)

    def random_algorithm(self, seed: Optional[int] = None) -> "Osmo":
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

    def balancing_algorithm(self, seed: Optional[int] = None) -> "Osmo":
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

    def weighted_algorithm(self, seed: Optional[int] = None) -> "Osmo":
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

    def stop_after_steps(self, steps: int) -> "Osmo":
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

    def stop_after_time(self, seconds: int) -> "Osmo":
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

    def run_tests(self, count: int) -> "Osmo":
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

    def run_endless(self) -> "Osmo":
        """
        Run tests endlessly (convenience fluent API).

        Note: You'll need to manually interrupt execution (Ctrl+C).

        Returns:
            Self for method chaining
        """
        from pyosmo.end_conditions import Endless
        self.test_suite_end_condition = Endless()
        return self

    def raise_on_error(self) -> "Osmo":
        """
        Raise exceptions immediately when errors occur (convenience fluent API).

        Returns:
            Self for method chaining
        """
        from pyosmo.error_strategy import AlwaysRaise
        return self.on_error(AlwaysRaise())

    def ignore_errors(self, max_count: Optional[int] = None) -> "Osmo":
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
        else:
            from pyosmo.error_strategy import AllowCount
            return self.on_error(AllowCount(max_count))

    def ignore_asserts(self) -> "Osmo":
        """
        Ignore assertion errors but raise other exceptions (convenience fluent API).

        Returns:
            Self for method chaining
        """
        from pyosmo.error_strategy import IgnoreAsserts
        return self.on_error(IgnoreAsserts())
