from pyosmo.end_conditions.base import OsmoEndCondition


class Endless(OsmoEndCondition):

    def end_test(self, history, model):
        """ Newer stop the test """
        return False

    def end_suite(self, history, model):
        """ Never stop the suite """
        return False

    def __init__(self):
        pass
