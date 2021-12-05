from pyosmo.end_conditions.base import OsmoEndCondition
from pyosmo.history.history import OsmoHistory
from pyosmo.osmomodel import OsmoModel


class StepCoverage(OsmoEndCondition):
    """
    Stops testing when count is filled
    """

    def __init__(self, coverage_percent: int):
        if coverage_percent in range(1, 100):
            raise Exception(f"Coverage is {coverage_percent} and it need to be > 0 and < 100")
        self.coverage = coverage_percent / 100

    def end_test(self, history: OsmoHistory, model: OsmoModel) -> bool:
        """ Stops test case when defined number of test steps are executed """
        all_steps = len(list(model.all_steps))
        used_steps = len(list(filter(lambda s: history.current_test_case.is_used(s), model.all_steps)))
        current_coverage = used_steps / all_steps
        return current_coverage >= self.coverage

    def end_suite(self, history: OsmoHistory, model: OsmoModel) -> bool:
        """ Stops test suite when defined number of test cases are executed """
        all_steps = len(list(model.all_steps))
        used_steps = len(list(filter(lambda s: history.is_used(s), model.all_steps)))
        current_coverage = used_steps / all_steps
        return current_coverage >= self.coverage
