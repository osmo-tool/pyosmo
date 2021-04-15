from pyosmo.osmo import Osmo


def test_step_without_guard():
    class TestModel:
        def __init__(self):
            pass

        @staticmethod
        def step_first():
            pass

    osmo = Osmo(TestModel())
    osmo.generate()
