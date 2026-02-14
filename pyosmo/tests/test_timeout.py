import time

import pytest

from pyosmo.config import ConfigurationError
from pyosmo.osmo import Osmo


class HangingStepModel:
    def step_hang(self):
        time.sleep(10)

    def step_fast(self):
        pass


class HangingGuardModel:
    def step_action(self):
        pass

    def guard_action(self):
        time.sleep(10)
        return True


class FastModel:
    def step_one(self):
        pass

    def step_two(self):
        pass


class ErrorStepModel:
    def step_fail(self):
        raise ValueError('step error')


def test_hanging_step_raises_timeout():
    osmo = Osmo(HangingStepModel()).with_timeout(0.1).stop_after_steps(1).run_tests(1)
    with pytest.raises(TimeoutError, match='timed out after 0.1 seconds'):
        osmo.generate()


def test_hanging_guard_raises_timeout():
    osmo = Osmo(HangingGuardModel()).with_timeout(0.1).stop_after_steps(1).run_tests(1)
    with pytest.raises(TimeoutError, match='timed out after 0.1 seconds'):
        osmo.generate()


def test_timeout_none_disables_timeout():
    """With timeout=None, no timeout is applied (function runs normally)."""
    osmo = Osmo(FastModel()).with_timeout(None).stop_after_steps(5).run_tests(1)
    osmo.generate()
    assert len(osmo.history.test_cases) == 1


def test_with_timeout_returns_self():
    osmo = Osmo(FastModel())
    result = osmo.with_timeout(30)
    assert result is osmo


def test_fast_functions_work_with_timeout():
    osmo = Osmo(FastModel()).with_timeout(5.0).stop_after_steps(10).run_tests(1)
    osmo.generate()
    assert len(osmo.history.test_cases) == 1
    assert len(osmo.history.test_cases[0].steps_log) == 10


def test_timeout_propagates_to_model():
    osmo = Osmo(FastModel()).with_timeout(42.0)
    osmo.generate()
    assert osmo.model.timeout == 42.0


def test_default_timeout_is_60():
    osmo = Osmo(FastModel())
    assert osmo.timeout == 60.0


def test_timeout_validation_rejects_negative():
    osmo = Osmo(FastModel())
    with pytest.raises(ConfigurationError, match='positive number'):
        osmo.with_timeout(-1)


def test_timeout_validation_rejects_zero():
    osmo = Osmo(FastModel())
    with pytest.raises(ConfigurationError, match='positive number'):
        osmo.with_timeout(0)


def test_timeout_validation_rejects_string():
    osmo = Osmo(FastModel())
    with pytest.raises(ConfigurationError, match='positive number or None'):
        osmo.with_timeout('fast')  # type: ignore[arg-type]


def test_step_error_preserved_through_timeout():
    """Original exceptions should propagate through the timeout wrapper."""
    osmo = Osmo(ErrorStepModel()).with_timeout(5.0).stop_after_steps(1).run_tests(1)
    with pytest.raises(ValueError, match='step error'):
        osmo.generate()
