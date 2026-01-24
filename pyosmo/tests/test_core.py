import pytest

from pyosmo import Osmo
from pyosmo.end_conditions import Length


def test_empty_model():
    class EmptyTestModel:
        def __init__(self):
            pass

    exception = False
    try:
        osmo = Osmo(EmptyTestModel())
        osmo.generate()
    except Exception:
        exception = True

    if not exception:
        raise Exception('Osmo did not except empty model')


def test_step_without_guard():
    class TestModel:
        def __init__(self):
            pass

        @staticmethod
        def step_first():
            pass

    osmo = Osmo(TestModel())
    osmo.generate()


def test_guard():
    class TestModel:
        def __init__(self):
            pass

        @staticmethod
        def guard_allow():
            return True

        @staticmethod
        def step_allow():
            pass

        @staticmethod
        def step_allow_without_guard():
            pass

        @staticmethod
        def guard_not_allow():
            return False

        @staticmethod
        def step_not_allow():
            pass

    osmo = Osmo(TestModel())
    osmo.generate()
    for tc in osmo.history.test_cases:
        for step in tc.steps_log:
            assert 'not' not in step.name


def test_split_model_with_same_name_functions():
    class TestModel1:
        def __init__(self):
            self.step_execute = False

        def step_first(self):
            self.step_execute = True

    class TestModel2:
        def __init__(self):
            self.step_execute = False

        def step_first(self):
            self.step_execute = True

    tm1 = TestModel1()
    tm2 = TestModel2()
    osmo = Osmo(tm1)
    osmo.add_model(tm2)
    osmo.generate()
    assert tm1.step_execute, 'Osmo did not execute step in first model'
    assert tm2.step_execute, 'Osmo did not execute step in second model'


def test_no_available_steps_raises_clear_error():
    """When all guards return False, engine should raise a clear error"""

    class AllGuardedModel:
        @staticmethod
        def step_blocked():
            pass

        @staticmethod
        def guard_blocked():
            return False

    osmo = Osmo(AllGuardedModel())
    osmo.test_end_condition = Length(10)
    with pytest.raises(Exception, match='No steps available'):
        osmo.generate()


def test_step_name_in_history_uses_semantic_name():
    """TestStepLog.name should return the semantic step name, not the function name"""

    class NameModel:
        @staticmethod
        def step_login():
            pass

        @staticmethod
        def step_logout():
            pass

    osmo = Osmo(NameModel())
    osmo.test_end_condition = Length(5)
    osmo.generate()

    # History should use semantic names (without 'step_' prefix)
    for tc in osmo.history.test_cases:
        for step_log in tc.steps_log:
            assert not step_log.name.startswith('step_'), f'Expected semantic name, got function name: {step_log.name}'
            assert step_log.name in ('login', 'logout')

    # step_frequency should also use semantic names
    frequency = osmo.history.step_frequency()
    for name in frequency:
        assert not name.startswith('step_')
