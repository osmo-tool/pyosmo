from pyosmo.osmo import Osmo


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
        for step in tc.steps:
            assert 'not' not in step.name
