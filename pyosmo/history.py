import time


class TestStepLog:
    def __init__(self, step, duration):
        self._step = step
        self._timestamp = time.time()
        self._duration = duration

    @property
    def step(self):
        return self._step

    @property
    def name(self):
        return self._step.function_name

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def duration(self):
        return self._duration


class TestCase:
    def __init__(self):
        self.steps_log = list()
        self._start_time = time.time()
        self._stop_time = None

    def add_step(self, step_log):
        if self._stop_time is not None:
            raise Exception("Test case is already stopped, cannot add more test steps!")
        self.steps_log.append(step_log)

    @property
    def steps_count(self):
        return len(self.steps_log)

    def get_step_count(self, test_name):
        """ Counts how many times the step is really called during whole history """
        counter = 0
        for step in self.steps_log:
            if step.name == test_name:
                counter += 1
        return counter

    def stop(self):
        self._stop_time = time.time()

    @property
    def start_time(self):
        return self._start_time

    @property
    def stop_time(self):
        return self._stop_time

    @property
    def duration(self):
        if self._stop_time is None:
            # Test is still running
            return time.time() - self._start_time
        return self._stop_time - self._start_time


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

    @property
    def current_test_case(self):
        """ The test case which is running or generating at the moment """
        if self.test_cases:
            return self.test_cases[-1]
        return None

    def add_step(self, step, duration):
        """
        Add a step to the history
        :param step: complete name of the step
        :param duration: step duration
        :return:
        """
        if self.current_test_case is None:
            raise Exception("There is no current test case!!")
        self.current_test_case.add_step(TestStepLog(step, duration))

    def stop(self):
        if self.stop_time:
            return
        if self.current_test_case:
            self.current_test_case.stop()
        self.stop_time = time.time()

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

    def get_step_count(self, test_name):
        """ Counts how many times the step is really called during whole history """
        return sum([test_case.get_step_count(test_name) for test_case in self.test_cases])

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
        for key in stats.keys():
            ret += '{}:{}\n'.format(key, stats[key])
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

    def count_in_current_test_case(self, step):
        count = 0
        for step_log in self.current_test_case.steps_log:
            if step_log.step.function_name == step.function_name:
                count += 1
        return count

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
