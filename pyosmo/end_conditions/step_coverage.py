from pyosmo.end_conditions.base import OsmoEndCondition
from pyosmo.history.history import OsmoHistory
from pyosmo.model import OsmoModelCollector


class StepCoverage(OsmoEndCondition):
    """
    Stops testing when count is filled
    """

    def __init__(self, coverage_percent: int):
        if coverage_percent in range(1, 100):
            raise Exception(f"Coverage is {coverage_percent} and it need to be > 0 and < 100")
        self.coverage = coverage_percent / 100

    def end_test(self, history: OsmoHistory, model: OsmoModelCollector) -> bool:
        """ Stops test case when defined number of test steps are executed """
        all_steps = len(list(model.all_steps))
        used_steps = sum([1 for s in model.all_steps if history.current_test_case.is_used(s)])
        current_coverage = used_steps / all_steps
        return current_coverage >= self.coverage

    def end_suite(self, history: OsmoHistory, model: OsmoModelCollector) -> bool:
        """ Stops test suite when defined number of test cases are executed """
        all_steps = len(list(model.all_steps))
        used_steps = sum([1 for s in model.all_steps if history.current_test_case.is_used(s)])
        current_coverage = used_steps / all_steps
        return current_coverage >= self.coverage
