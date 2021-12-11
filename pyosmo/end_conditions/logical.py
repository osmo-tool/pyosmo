from pyosmo.end_conditions.base import OsmoEndCondition
from pyosmo.history.history import OsmoHistory
from pyosmo.model import OsmoModelCollector


class LogicalEndCondition:
    def __init__(self, *args):
        if len(args) < 2:
            raise Exception("And operator needs at least two OsmoEndConditions!")
        self.endConditions = args


class And(OsmoEndCondition, LogicalEndCondition):
    """
    Logical AND, which make sure that all end conditions need to be true before this is true
    """

    def end_test(self, history: OsmoHistory, model: OsmoModelCollector) -> bool:
        """ Stops test case when all end conditions are filled """
        return False not in (ec.end_test(history, model) for ec in self.endConditions)

    def end_suite(self, history: OsmoHistory, model: OsmoModelCollector) -> bool:
        """ Stops test suite when all end conditions are filled """
        return False not in (ec.end_suite(history, model) for ec in self.endConditions)


class Or(OsmoEndCondition, LogicalEndCondition):
    """
    Logical OR, which make sure that one of the end conditions is true
    """

    def end_test(self, history: OsmoHistory, model: OsmoModelCollector) -> bool:
        """ Stops test case when all end conditions are filled """
        return True in (ec.end_test(history, model) for ec in self.endConditions)

    def end_suite(self, history: OsmoHistory, model: OsmoModelCollector) -> bool:
        """ Stops test suite when all end conditions are filled """
        return True in (ec.end_suite(history, model) for ec in self.endConditions)
