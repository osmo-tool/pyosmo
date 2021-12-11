from pyosmo.end_conditions.base import OsmoEndCondition
from pyosmo.history.history import OsmoHistory
from pyosmo.model import OsmoModelCollector


class Length(OsmoEndCondition):
    """
    Stops testing when count is filled
    """

    def __init__(self, count):
        self.count = count

    def end_test(self, history: OsmoHistory, model: OsmoModelCollector) -> bool:
        """ Stops test case when defined number of test steps are executed """
        return history.current_test_case.steps_count >= self.count

    def end_suite(self, history: OsmoHistory, model: OsmoModelCollector) -> bool:
        """ Stops test suite when defined number of test cases are executed """
        return history.test_case_count >= self.count
