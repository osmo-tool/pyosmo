from datetime import datetime
from datetime import timedelta

from pyosmo.model import TestStep


class TestStepLog:
    def __init__(self, step: TestStep, duration: timedelta, error: Exception = None):
        self._step = step
        self._timestamp = datetime.now()
        self._duration = duration
        self._error = error

    @property
    def step(self) -> TestStep:
        return self._step

    @property
    def error(self) -> Exception:
        return self._error

    @property
    def name(self) -> str:
        return self._step.function_name

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def duration(self) -> timedelta:
        return self._duration
