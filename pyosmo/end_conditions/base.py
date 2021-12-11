from abc import abstractmethod

from pyosmo.history.history import OsmoHistory
from pyosmo.model import OsmoModelCollector


class OsmoEndCondition:
    """
    Abstract end condition class
    """

    @abstractmethod
    def end_test(self, history: OsmoHistory, model: OsmoModelCollector) -> bool:
        raise Exception("This is not implemented!")

    @abstractmethod
    def end_suite(self, history: OsmoHistory, model: OsmoModelCollector) -> bool:
        raise Exception("This is not implemented!")
