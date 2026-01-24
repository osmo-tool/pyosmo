"""Test history and statistics API"""

from pyosmo import Osmo
from pyosmo.end_conditions import Length


class SimpleModel:
    """Simple test model"""

    def __init__(self):
        self.counter = 0

    def step_action_a(self):
        self.counter += 1

    def step_action_b(self):
        self.counter += 1

    def step_action_c(self):
        self.counter += 1


def test_statistics():
    """Test structured statistics API"""
    model = SimpleModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(10)

    osmo.run()

    # Get structured statistics
    stats = osmo.history.statistics()

    # Verify structured data is accessible
    assert stats.total_steps == 10
    assert stats.total_tests == 1
    assert stats.unique_steps <= 3
    assert stats.error_count == 0
    assert stats.average_steps_per_test == 10.0

    # Verify step frequency is a dictionary
    assert isinstance(stats.step_frequency, dict)
    assert all(isinstance(k, str) for k in stats.step_frequency)
    assert all(isinstance(v, int) for v in stats.step_frequency.values())

    # Verify most/least executed steps are set
    assert stats.most_executed_step is not None
    assert stats.least_executed_step is not None


def test_statistics_to_dict():
    """Test statistics serialization"""
    model = SimpleModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(5)

    osmo.run()

    stats = osmo.history.statistics()
    data = stats.to_dict()

    # Verify dictionary structure
    assert 'total_steps' in data
    assert 'total_tests' in data
    assert 'duration_seconds' in data
    assert 'step_frequency' in data
    assert 'step_execution_times' in data

    # Verify types
    assert isinstance(data['total_steps'], int)
    assert isinstance(data['duration_seconds'], float)
    assert isinstance(data['step_frequency'], dict)


def test_step_frequency():
    """Test step_frequency method"""
    model = SimpleModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(10)

    osmo.run()

    frequency = osmo.history.step_frequency()

    # Verify it's a dictionary
    assert isinstance(frequency, dict)

    # Verify total equals total_amount_of_steps
    total = sum(frequency.values())
    assert total == osmo.history.total_amount_of_steps


def test_step_pairs():
    """Test step_pairs method for transition tracking"""
    model = SimpleModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(10)

    osmo.run()

    pairs = osmo.history.step_pairs()

    # Verify it's a dictionary with tuple keys
    assert isinstance(pairs, dict)
    assert all(isinstance(k, tuple) and len(k) == 2 for k in pairs)

    # Verify total pairs is one less than total steps
    # (n steps create n-1 pairs)
    total_pairs = sum(pairs.values())
    assert total_pairs == osmo.history.total_amount_of_steps - 1


def test_coverage_timeline():
    """Test coverage_timeline method"""
    model = SimpleModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(10)

    osmo.run()

    timeline = osmo.history.coverage_timeline()

    # Verify it's a list of tuples
    assert isinstance(timeline, list)
    assert all(isinstance(t, tuple) and len(t) == 2 for t in timeline)

    # Verify timeline has entry for each step
    assert len(timeline) == osmo.history.total_amount_of_steps

    # Verify coverage is non-decreasing
    coverages = [t[1] for t in timeline]
    for i in range(len(coverages) - 1):
        assert coverages[i] <= coverages[i + 1]


def test_failed_tests():
    """Test failed_tests method"""

    class FailingModel:
        def __init__(self):
            self.counter = 0

        def step_action(self):
            self.counter += 1
            if self.counter == 3:
                raise Exception('Intentional failure')

    model = FailingModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(5)

    # Import error strategy to ignore errors
    from pyosmo.error_strategy import AlwaysIgnore

    osmo.test_error_strategy = AlwaysIgnore()

    osmo.run()

    # Get failed tests
    failed = osmo.history.failed_tests()

    # There should be at least one failed test
    assert len(failed) > 0
    assert all(tc.error_count > 0 for tc in failed)


def test_statistics_str_representation():
    """Test string representation of statistics"""
    model = SimpleModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(5)

    osmo.run()

    stats = osmo.history.statistics()
    str_repr = str(stats)

    # Verify it contains expected information
    assert 'Total Tests:' in str_repr
    assert 'Total Steps:' in str_repr
    assert 'Duration:' in str_repr


def test_test_case_is_running():
    """is_running() should return True when test is active, False when stopped"""
    from pyosmo.history.test_case import OsmoTestCaseRecord

    tc = OsmoTestCaseRecord()
    assert tc.is_running() is True, 'New test case should be running'

    tc.stop()
    assert tc.is_running() is False, 'Stopped test case should not be running'


def test_cannot_add_step_to_stopped_test():
    """Adding a step to a stopped test case should raise"""
    import pytest

    from pyosmo.history.test_case import OsmoTestCaseRecord
    from pyosmo.history.test_step_log import TestStepLog
    from pyosmo.model import TestStep

    class DummyModel:
        def step_dummy(self):
            pass

    tc = OsmoTestCaseRecord()
    tc.stop()

    dummy_step = TestStep('step_dummy', DummyModel())
    from datetime import timedelta

    step_log = TestStepLog(dummy_step, timedelta(seconds=0))

    with pytest.raises(Exception, match='not running'):
        tc.add_step(step_log)
