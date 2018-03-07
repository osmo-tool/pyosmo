import time


class TestStep(object):
    def __init__(self, identifier, duration):
        self._name = identifier
        self._timestamp = time.time()
        self._duration = duration

    @property
    def name(self):
        return self._name

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def duration(self):
        return self._duration


class TestCase(object):
    def __init__(self):
        self.steps = list()
        self._start_time = time.time()
        self._stop_time = None

    def add_step(self, step):
        self.steps.append(step)

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
        return self._stop_time - self._start_time


class OsmoHistory(object):

    def __init__(self):
        self.test_cases = list()
        self.stop_time = None
        self.start_time = time.time()
        self.current_test_case = None

    def start_new_test(self):
        # Stop test case timer
        if self.current_test_case:
            self.current_test_case.stop()
            # Store previous test case
            self.test_cases.append(self.current_test_case)
        # Start a new test case
        self.current_test_case = TestCase()

    def add_step(self, step_name, duration):
        """
        Add a step to the history
        :param step: complete name of the step
        :return:
        """
        if self.current_test_case is None:
            raise Exception("There is no current test case!!")
        self.current_test_case.add_step(TestStep(step_name, duration))

    def stop(self):
        if self.stop_time:
            return

        self.stop_time = time.time()

        if self.current_test_case:
            self.current_test_case.stop()
            self.test_cases.append(self.current_test_case)
            self.current_test_case = None

    @property
    def duration(self):
        return self.stop_time - self.start_time

    @property
    def test_case_count(self):
        return len(self.test_cases)

    @property
    def total_amount_of_steps(self):
        return sum([len(tc.steps) for tc in self.test_cases])

    def get_usage_count_of_test(self, test_name):
        counter = 0
        for test_case in self.test_cases:
            for step in test_case.steps:
                if step.name == test_name:
                    counter += 1
        return counter

    @property
    def step_stats(self):
        stats = dict()
        ret = ''
        for test_case in self.test_cases:
            for step in test_case.steps:
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

    def get_count_in_current_test_case(self, ending):
        count = 0
        for temp in self.current_test_case.steps:
            if ending in temp.name:
                count += 1
        return count

    def __str__(self):
        ret = ''
        tc_index = 0
        for test_case in self.test_cases:
            tc_index += 1
            ret += '{}. test case {:.2f}s\n'.format(tc_index, test_case.duration)
            for step in test_case.steps:
                ret += '{} {:.2f}s {}\n'.format(step.timestamp, step.duration, step.name)
            ret += '\n'
        return ret
