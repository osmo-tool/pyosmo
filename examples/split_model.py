from pyosmo.osmo import Osmo


class TestModel:

    def __init__(self):
        pass

    def guard_first(self):
        return True

    def step_first(self):
        print("1. step")

    def before_suite(self):
        print('START')

    def before_test(self):
        print('Test starts')

    def after_test(self):
        print('Test ends')
        print('')

    def after_suite(self):
        print('END')


class TestModel2:

    def __init__(self):
        pass

    @staticmethod
    def guard_second():
        return True

    @staticmethod
    def pre_second():
        print("-->")

    @staticmethod
    def step_second():
        print("2. step")

    @staticmethod
    def post_second():
        print("<--")

osmo = Osmo(TestModel())
osmo.add_model(TestModel2())
osmo.generate()
