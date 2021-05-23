import time

from pyosmo.history.test_case import TestCase
from pyosmo.history.test_step_log import TestStepLog


class OsmoHistory:

    def __init__(self):
        self.test_cases = list()
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
        stats = dict()
        ret = ''
        for test_case in self.test_cases:
            for step in test_case.steps_log:
                if step.name in stats.keys():
                    stats[step.name] = stats[step.name] + 1
                else:
                    stats[step.name] = 1
        for key, value in stats.items():
            ret += '{}:{}\n'.format(key, value)
        return ret

    @property
    def summary(self):
        if self.stop_time is None:
            raise Exception("Cannot get summary of ongoing test")
        ret = ''
        ret += 'Osmo summary:\n'
        ret += 'Test cases: {}\n'.format(self.test_case_count)
        ret += 'Test steps: {}\n'.format(self.total_amount_of_steps)
        ret += 'Duration: {:.2f}s\n'.format(self.duration)
        return ret

    def __str__(self):
        ret = ''
        tc_index = 0
        for test_case in self.test_cases:
            tc_index += 1
            ret += '{}. test case {:.2f}s\n'.format(tc_index, test_case.duration)
            for step in test_case.steps_log:
                ret += '{} {:.2f}s {}\n'.format(step.timestamp, step.duration, step.name)
            ret += '\n'
        return ret
