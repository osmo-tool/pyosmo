from abc import abstractmethod

from pyosmo.history.history import OsmoHistory
from pyosmo.model import OsmoModelCollector


class OsmoErrorStrategy:
    """
    Abstract class for defining how to behave in case of failure
    """

    @abstractmethod
    def failure_in_test(self, history: OsmoHistory, model: OsmoModelCollector, error: BaseException):
        raise Exception("This is not implemented!")

    @abstractmethod
    def failure_in_suite(self, history: OsmoHistory, model: OsmoModelCollector, error: BaseException):
        raise Exception("This is not implemented!")
