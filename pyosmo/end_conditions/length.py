from pyosmo.end_conditions.base import OsmoEndCondition


class Length(OsmoEndCondition):
    """
    Stops testing when count is filled
    """

    def __init__(self, count):
        self.count = count

    def end_test(self, history, model):
        """ Stops test case when defined number of test steps are executed """
        return history.current_test_case.steps_count >= self.count

    def end_suite(self, history, model):
        """ Stops test suite when defined number of test cases are executed """
        return history.test_case_count >= self.count
