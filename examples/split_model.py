"""This is simples possible example how to split model in two parts"""

import pyosmo


class TestModel(pyosmo.OsmoModel):
    def __init__(self):
        pass

    @staticmethod
    def guard_first():
        return True

    @staticmethod
    def step_first():
        print('1. step')

    @staticmethod
    def before_suite():
        print('START')

    @staticmethod
    def before_test():
        print('Test starts')

    @staticmethod
    def after_test():
        print('Test ends')

    @staticmethod
    def after_suite():
        print('END')


class TestModel2(pyosmo.OsmoModel):
    def __init__(self):
        pass

    @staticmethod
    def guard_second():
        return True

    @staticmethod
    def pre_second():
        print('-->')

    @staticmethod
    def step_second():
        print('2. step')

    @staticmethod
    def post_second():
        print('<--')


if __name__ == '__main__':
    osmo = pyosmo.Osmo(TestModel())
    osmo.add_model(TestModel2())
    osmo.generate()
