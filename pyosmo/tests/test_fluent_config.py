"""Tests for the fluent configuration API."""


from pyosmo import Osmo
from pyosmo.algorithm import BalancingAlgorithm, RandomAlgorithm, WeightedAlgorithm
from pyosmo.end_conditions import Endless, Length, Time
from pyosmo.error_strategy import AllowCount, AlwaysIgnore, AlwaysRaise, IgnoreAsserts


class SimpleModel:
    """Simple test model with a single step."""

    def __init__(self):
        self.step_count = 0

    def step_increment(self):
        """Increment the step counter."""
        self.step_count += 1


class TestFluentConfigurationAPI:
    """Test the fluent configuration API methods."""

    def test_with_seed(self):
        """Test with_seed fluent method."""
        model = SimpleModel()
        osmo = Osmo(model).with_seed(12345)
        assert osmo.seed == 12345

    def test_with_seed_chaining(self):
        """Test that with_seed returns self for chaining."""
        model = SimpleModel()
        osmo = Osmo(model)
        result = osmo.with_seed(12345)
        assert result is osmo

    def test_with_algorithm(self):
        """Test with_algorithm fluent method."""
        model = SimpleModel()
        algo = RandomAlgorithm()
        osmo = Osmo(model).with_algorithm(algo)
        assert osmo.algorithm is algo

    def test_with_test_end_condition(self):
        """Test with_test_end_condition fluent method."""
        model = SimpleModel()
        condition = Length(50)
        osmo = Osmo(model).with_test_end_condition(condition)
        assert osmo.test_end_condition is condition

    def test_with_suite_end_condition(self):
        """Test with_suite_end_condition fluent method."""
        model = SimpleModel()
        condition = Length(3)
        osmo = Osmo(model).with_suite_end_condition(condition)
        assert osmo.test_suite_end_condition is condition

    def test_on_error(self):
        """Test on_error fluent method sets both error strategies."""
        model = SimpleModel()
        strategy = AlwaysIgnore()
        osmo = Osmo(model).on_error(strategy)
        assert osmo.test_error_strategy is strategy
        assert osmo.test_suite_error_strategy is strategy

    def test_on_test_error(self):
        """Test on_test_error fluent method."""
        model = SimpleModel()
        strategy = AlwaysIgnore()
        osmo = Osmo(model).on_test_error(strategy)
        assert osmo.test_error_strategy is strategy

    def test_on_suite_error(self):
        """Test on_suite_error fluent method."""
        model = SimpleModel()
        strategy = AlwaysIgnore()
        osmo = Osmo(model).on_suite_error(strategy)
        assert osmo.test_suite_error_strategy is strategy

    def test_build(self):
        """Test build method returns self."""
        model = SimpleModel()
        osmo = Osmo(model)
        result = osmo.build()
        assert result is osmo

    def test_fluent_chain_basic(self):
        """Test basic fluent chaining."""
        model = SimpleModel()
        osmo = (
            Osmo(model)
            .with_seed(12345)
            .with_algorithm(RandomAlgorithm())
            .with_test_end_condition(Length(100))
            .with_suite_end_condition(Length(5))
            .on_error(AlwaysRaise())
            .build()
        )

        assert osmo.seed == 12345
        assert isinstance(osmo.algorithm, RandomAlgorithm)
        assert isinstance(osmo.test_end_condition, Length)
        assert isinstance(osmo.test_suite_end_condition, Length)
        assert isinstance(osmo.test_error_strategy, AlwaysRaise)
        assert isinstance(osmo.test_suite_error_strategy, AlwaysRaise)


class TestConvenienceFluentAPI:
    """Test the convenience (more fluent) API methods."""

    def test_random_algorithm_no_seed(self):
        """Test random_algorithm without seed."""
        model = SimpleModel()
        osmo = Osmo(model).random_algorithm()
        assert isinstance(osmo.algorithm, RandomAlgorithm)

    def test_random_algorithm_with_seed(self):
        """Test random_algorithm with seed."""
        model = SimpleModel()
        osmo = Osmo(model).random_algorithm(seed=12345)
        assert isinstance(osmo.algorithm, RandomAlgorithm)
        assert osmo.seed == 12345

    def test_balancing_algorithm_no_seed(self):
        """Test balancing_algorithm without seed."""
        model = SimpleModel()
        osmo = Osmo(model).balancing_algorithm()
        assert isinstance(osmo.algorithm, BalancingAlgorithm)

    def test_balancing_algorithm_with_seed(self):
        """Test balancing_algorithm with seed."""
        model = SimpleModel()
        osmo = Osmo(model).balancing_algorithm(seed=54321)
        assert isinstance(osmo.algorithm, BalancingAlgorithm)
        assert osmo.seed == 54321

    def test_weighted_algorithm_no_seed(self):
        """Test weighted_algorithm without seed."""
        model = SimpleModel()
        osmo = Osmo(model).weighted_algorithm()
        assert isinstance(osmo.algorithm, WeightedAlgorithm)

    def test_weighted_algorithm_with_seed(self):
        """Test weighted_algorithm with seed."""
        model = SimpleModel()
        osmo = Osmo(model).weighted_algorithm(seed=99999)
        assert isinstance(osmo.algorithm, WeightedAlgorithm)
        assert osmo.seed == 99999

    def test_stop_after_steps(self):
        """Test stop_after_steps convenience method."""
        model = SimpleModel()
        osmo = Osmo(model).stop_after_steps(100)
        assert isinstance(osmo.test_end_condition, Length)
        # Length class doesn't expose the count, so we'll test by running
        osmo.run()
        assert model.step_count == 100

    def test_stop_after_time(self):
        """Test stop_after_time convenience method."""
        model = SimpleModel()
        osmo = Osmo(model).stop_after_time(1)
        assert isinstance(osmo.test_end_condition, Time)

    def test_run_tests(self):
        """Test run_tests convenience method."""
        model = SimpleModel()
        osmo = Osmo(model).stop_after_steps(5).run_tests(3)
        assert isinstance(osmo.test_suite_end_condition, Length)
        osmo.run()
        # Should run 3 tests with 5 steps each = 15 steps
        assert model.step_count == 15

    def test_run_endless(self):
        """Test run_endless convenience method."""
        model = SimpleModel()
        osmo = Osmo(model).run_endless()
        assert isinstance(osmo.test_suite_end_condition, Endless)

    def test_raise_on_error(self):
        """Test raise_on_error convenience method."""
        model = SimpleModel()
        osmo = Osmo(model).raise_on_error()
        assert isinstance(osmo.test_error_strategy, AlwaysRaise)
        assert isinstance(osmo.test_suite_error_strategy, AlwaysRaise)

    def test_ignore_errors_all(self):
        """Test ignore_errors with no max_count."""
        model = SimpleModel()
        osmo = Osmo(model).ignore_errors()
        assert isinstance(osmo.test_error_strategy, AlwaysIgnore)
        assert isinstance(osmo.test_suite_error_strategy, AlwaysIgnore)

    def test_ignore_errors_with_count(self):
        """Test ignore_errors with max_count."""
        model = SimpleModel()
        osmo = Osmo(model).ignore_errors(max_count=5)
        assert isinstance(osmo.test_error_strategy, AllowCount)
        assert isinstance(osmo.test_suite_error_strategy, AllowCount)

    def test_ignore_asserts(self):
        """Test ignore_asserts convenience method."""
        model = SimpleModel()
        osmo = Osmo(model).ignore_asserts()
        assert isinstance(osmo.test_error_strategy, IgnoreAsserts)
        assert isinstance(osmo.test_suite_error_strategy, IgnoreAsserts)

    def test_convenience_fluent_chain(self):
        """Test the full convenience fluent chain (even more fluent API)."""
        model = SimpleModel()
        osmo = (
            Osmo(model)
            .random_algorithm(seed=12345)
            .stop_after_steps(100)
            .run_tests(5)
            .raise_on_error()
            .build()
        )

        assert osmo.seed == 12345
        assert isinstance(osmo.algorithm, RandomAlgorithm)
        assert isinstance(osmo.test_end_condition, Length)
        assert isinstance(osmo.test_suite_end_condition, Length)
        assert isinstance(osmo.test_error_strategy, AlwaysRaise)

        # Run and verify
        osmo.run()
        assert model.step_count == 500  # 5 tests × 100 steps


class TestFluentAPIIntegration:
    """Integration tests for fluent API with actual test runs."""

    def test_fluent_api_execution(self):
        """Test that fluent API configuration works correctly during execution."""
        model = SimpleModel()
        osmo = Osmo(model).random_algorithm(seed=42).stop_after_steps(20).run_tests(2).build()

        osmo.run()

        # Should have run 2 tests with 20 steps each
        assert model.step_count == 40
        assert len(osmo.history.test_cases) == 2

    def test_mixed_api_styles(self):
        """Test that old and new API styles can be mixed."""
        model = SimpleModel()
        osmo = Osmo(model).random_algorithm(seed=123)

        # Mix old-style property setting
        osmo.test_end_condition = Length(15)

        # Continue with fluent API
        osmo.run_tests(2).build()

        osmo.run()

        assert model.step_count == 30  # 2 tests × 15 steps

    def test_fluent_api_with_error_handling(self):
        """Test fluent API with error handling configuration."""

        class ErrorModel:
            def __init__(self):
                self.step_count = 0

            def step_increment(self):
                """Step that sometimes raises an error."""
                self.step_count += 1
                if self.step_count == 5:
                    raise ValueError("Test error")

        model = ErrorModel()
        osmo = (
            Osmo(model)
            .random_algorithm(seed=42)
            .stop_after_steps(10)
            .run_tests(1)
            .ignore_errors(max_count=1)
            .build()
        )

        # Should handle the error and continue
        osmo.run()
        assert model.step_count >= 5  # At least reached the error

    def test_chaining_returns_self(self):
        """Test that all fluent methods return self for proper chaining."""
        model = SimpleModel()
        osmo1 = Osmo(model)

        # All these should return the same instance
        osmo2 = osmo1.with_seed(123)
        osmo3 = osmo2.random_algorithm()
        osmo4 = osmo3.stop_after_steps(10)
        osmo5 = osmo4.run_tests(1)
        osmo6 = osmo5.raise_on_error()
        osmo7 = osmo6.build()

        assert osmo1 is osmo2 is osmo3 is osmo4 is osmo5 is osmo6 is osmo7


class TestBackwardCompatibility:
    """Test that fluent API doesn't break existing code."""

    def test_old_style_still_works(self):
        """Test that old-style configuration still works."""
        model = SimpleModel()
        osmo = Osmo(model)
        osmo.seed = 12345
        osmo.algorithm = RandomAlgorithm()
        osmo.test_end_condition = Length(10)
        osmo.test_suite_end_condition = Length(2)
        osmo.test_error_strategy = AlwaysRaise()

        osmo.run()

        assert model.step_count == 20  # 2 tests × 10 steps

    def test_mixed_old_and_new_styles(self):
        """Test mixing old and new configuration styles."""
        model = SimpleModel()
        osmo = Osmo(model)

        # Old style
        osmo.seed = 12345

        # New fluent style
        osmo.random_algorithm().stop_after_steps(15)

        # Old style again
        osmo.test_suite_end_condition = Length(3)

        osmo.run()

        assert model.step_count == 45  # 3 tests × 15 steps
        assert osmo.seed == 12345
