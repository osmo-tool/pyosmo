from pyosmo.end_conditions.base import OsmoEndCondition


class StepCoverage(OsmoEndCondition):
    """
    Stops testing when count is filled
    """

    def __init__(self, coverage_percent):
        if coverage_percent > 100 or coverage_percent < 0:
            raise Exception(f"Coverage is {coverage_percent} and it need to be >0 and <1")
        self.coverage = coverage_percent / 100

    def end_test(self, history, model):
        """ Stops test case when defined number of test steps are executed """
        all_steps = model.all_steps
        steps_used = 0
        for step in all_steps:
            if history.current_test_case.get_step_count(step) > 0:
                steps_used += 1
        current_coverage = steps_used / len(all_steps)
        return current_coverage >= self.coverage

    def end_suite(self, history, model):
        """ Stops test suite when defined number of test cases are executed """
        all_steps = model.all_steps
        steps_used = 0
        for step in all_steps:
            if history.get_step_count(step) > 0:
                steps_used += 1
        current_coverage = steps_used / len(all_steps)
        return current_coverage >= self.coverage
