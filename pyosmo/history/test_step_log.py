import time


class TestStepLog:
    def __init__(self, step, duration, error=None):
        self._step = step
        self._timestamp = time.time()
        self._duration = duration
        self._error = error

    @property
    def step(self):
        return self._step

    @property
    def error(self):
        return self._error

    @property
    def name(self):
        return self._step.function_name

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def duration(self):
        return self._duration
