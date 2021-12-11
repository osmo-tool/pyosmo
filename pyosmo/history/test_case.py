from datetime import datetime, timedelta

from pyosmo.history.test_step_log import TestStepLog
from pyosmo.model import TestStep


class OsmoTestCaseRecord:
    def __init__(self):
        self.steps_log = []
        self._start_time = None
        self._stop_time = None
        self._start_time = datetime.now()

    def stop(self) -> None:
        self._stop_time = datetime.now()

    def is_started(self) -> bool:
        return self._start_time is not None

    def is_running(self) -> bool:
        return self._stop_time is not None

    def add_step(self, step_log: TestStepLog) -> None:
        if self.is_running():
            raise Exception("Test case is not running, cannot add more test steps!")
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
