import time

from pyosmo.history.test_case import TestCase
from pyosmo.history.test_step_log import TestStepLog


class OsmoHistory:

    def __init__(self):
        self.test_cases = []
        self.stop_time = None
        self.start_time = time.time()

    def start_new_test(self):
        # Stop test case timer
        if self.current_test_case:
            self.current_test_case.stop()
        # Start a new test case
        self.test_cases.append(TestCase())

    def stop(self):
        if self.stop_time:
            return
        if self.current_test_case:
            self.current_test_case.stop()
        self.stop_time = time.time()

    def add_step(self, step, duration, error=None):
        """ Add a step to the history """
        if self.current_test_case is None:
            raise Exception("There is no current test case!!")
        self.current_test_case.add_step(TestStepLog(step, duration, error))

    @property
    def error_count(self):
        """ Total count of errors in all tests cases """
        return sum([x.error_count for x in self.test_cases])

    @property
    def current_test_case(self):
        """ The test case which is running or generating at the moment """
        return self.test_cases[-1] if self.test_cases else None

    @property
    def duration(self):
        if self.stop_time is None:
            # Test is still running
            return time.time() - self.start_time
        return self.stop_time - self.start_time

    @property
    def test_case_count(self):
        return len(self.test_cases)

    @property
    def total_amount_of_steps(self):
        return sum([len(tc.steps_log) for tc in self.test_cases])

    def get_step_count(self, step):
        """ Counts how many times the step is really called during whole history """
        return sum([test_case.get_step_count(step) for test_case in self.test_cases])

    @property
    def step_stats(self):
        stats = {}
        ret = ''
        for test_case in self.test_cases:
            for step in test_case.steps_log:
                if step.name in stats:
                    stats[step.name] = stats[step.name] + 1
                else:
                    stats[step.name] = 1
        for key, value in stats.items():
            ret += f'{key}:{value}\n'
        return ret

    @property
    def summary(self):
        if self.stop_time is None:
            raise Exception("Cannot get summary of ongoing test")
        ret = ''
        ret += 'Osmo summary:\n'
        ret += f'Test cases: {self.test_case_count}\n'
        ret += f'Test steps: {self.total_amount_of_steps}\n'
        ret += f'Duration: {self.duration:.2f}s\n'
        return ret

    def __str__(self):
        ret = ''
        tc_index = 0
        for test_case in self.test_cases:
            tc_index += 1
            ret += f'{tc_index}. test case {test_case.duration:.2f}s\n'
            for step in test_case.steps_log:
                ret += f'{step.timestamp} {step.duration:.2f}s {step.name}\n'
            ret += '\n'
        return ret
