from pyosmo.end_conditions.base import OsmoEndCondition
from pyosmo.history.history import OsmoHistory
from pyosmo.osmomodel import OsmoModel


class Endless(OsmoEndCondition):

    def end_test(self, history: OsmoHistory, model: OsmoModel) -> bool:
        """ Newer stop the test """
        return False

    def end_suite(self, history: OsmoHistory, model: OsmoModel) -> bool:
        """ Never stop the suite """
        return False

    def __init__(self):
        pass
