# pylint: disable=bare-except

from pyosmo import Osmo


def test_empty_model():
    class EmptyTestModel:
        def __init__(self):
            pass

    exception = False
    try:
        osmo = Osmo(EmptyTestModel())
        osmo.generate()
    except:
        exception = True

    if not exception:
        raise Exception("Osmo did not except empty model")


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
    assert tm1.step_execute, "Osmo did not execute step in first model"
    assert tm2.step_execute, "Osmo did not execute step in second model"
