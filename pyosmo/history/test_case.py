import time

from pyosmo.model import TestStep


class TestCase:
    def __init__(self):
        self.steps_log = []
        self._start_time = time.time()
        self._stop_time = None

    def add_step(self, step_log):
        if self._stop_time is not None:
            raise Exception("Test case is already stopped, cannot add more test steps!")
        self.steps_log.append(step_log)

    @property
    def steps_count(self):
        return len(self.steps_log)

    @property
    def error_count(self):
        """ How many errors happened during this test case """
        return len(list(filter(lambda x: x.error is not None, self.steps_log)))

    def get_step_count(self, step):
        """ Counts how many times the step is really called during whole history """
        assert isinstance(step, TestStep)
        return len(list(filter(lambda x: x.step.name == step.name is not None, self.steps_log)))

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
