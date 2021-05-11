from pyosmo.end_conditions.base import OsmoEndCondition


class Time(OsmoEndCondition):
    """
    Stops testing when time is out
    """

    def __init__(self, time_in_sec):
        self.time_in_sec = time_in_sec

    def end_test(self, history, model):
        return history.current_test_case.duration >= self.time_in_sec

    def end_suite(self, history, model):
        return history.duration >= self.time_in_sec
