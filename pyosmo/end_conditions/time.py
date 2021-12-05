from datetime import timedelta

from pyosmo.end_conditions.base import OsmoEndCondition
from pyosmo.history.history import OsmoHistory
from pyosmo.osmomodel import OsmoModel


class Time(OsmoEndCondition):
    """
    Stops testing when time is out
    """

    def __init__(self, duration: timedelta):
        self.duration = duration

    def end_test(self, history: OsmoHistory, model: OsmoModel) -> bool:
        return history.current_test_case.duration >= self.duration

    def end_suite(self, history: OsmoHistory, model: OsmoModel) -> bool:
        return history.duration >= self.duration
