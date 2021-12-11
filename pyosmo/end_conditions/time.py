from datetime import timedelta

from pyosmo.end_conditions.base import OsmoEndCondition
from pyosmo.history.history import OsmoHistory
from pyosmo.model import OsmoModelCollector


class Time(OsmoEndCondition):
    """
    Stops testing when time is out
    """

    def __init__(self, duration: timedelta):
        self.duration = duration

    def end_test(self, history: OsmoHistory, model: OsmoModelCollector) -> bool:
        return history.current_test_case.duration >= self.duration

    def end_suite(self, history: OsmoHistory, model: OsmoModelCollector) -> bool:
        return history.duration >= self.duration
