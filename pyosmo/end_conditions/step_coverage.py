from pyosmo.end_conditions.base import OsmoEndCondition


class StepCoverage(OsmoEndCondition):
    """
    Stops testing when count is filled
    """

    def __init__(self, coverage):
        if coverage > 1 or coverage < 0:
            raise Exception("Coverage is {} and it need to be >0 and <1".format(coverage))
        self.coverage = coverage

    def end_test(self, history, model):
        """ Stops test case when defined number of test steps are executed """
        step_names = [x.function_name for x in model.all_steps]
        steps_used = 0
        for step_name in step_names:
            if history.current_test_case.get_step_count(step_name) > 0:
                steps_used += 1
        current_coverage = steps_used / len(step_names)
        return current_coverage >= self.coverage

    def end_suite(self, history, model):
        """ Stops test suite when defined number of test cases are executed """
        step_names = [x.function_name for x in model.all_steps]
        steps_used = 0
        for step_name in step_names:
            if history.get_step_count(step_name) > 0:
                steps_used += 1
        current_coverage = steps_used / len(step_names)
        return current_coverage >= self.coverage
