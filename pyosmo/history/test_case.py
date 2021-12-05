from datetime import datetime, timedelta

from pyosmo.osmomodel import TestStep


class TestCase:
    def __init__(self):
        self.steps_log = []
        self._start_time = datetime.now()
        self._stop_time = None

    def add_step(self, step_log: TestStep):
        if self._stop_time is not None:
            raise Exception("Test case is already stopped, cannot add more test steps!")
        self.steps_log.append(step_log)

    @property
    def steps_count(self) -> int:
        return len(self.steps_log)

    @property
    def error_count(self) -> int:
        """ How many errors happened during this test case """
        return len(list(filter(lambda x: x.error is not None, self.steps_log)))

    def is_used(self, step: TestStep) -> bool:
        """ is used at least once """
        for sl in self.steps_log:
            if sl.step.name == step.name:
                return True
        return False

    def get_step_count(self, step: TestStep) -> int:
        """ Counts how many times the step is really called during whole history """
        return len(list(filter(lambda x: x.step.name == step.name is not None, self.steps_log)))

    def stop(self) -> None:
        self._stop_time = datetime.now()

    @property
    def start_time(self):
        return self._start_time

    @property
    def stop_time(self) -> datetime:
        return self._stop_time

    @property
    def duration(self) -> timedelta:
        if self._stop_time is None:
            # Test is still running
            return datetime.now() - self._start_time
        return self._stop_time - self._start_time
