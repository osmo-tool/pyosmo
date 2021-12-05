from abc import abstractmethod

from pyosmo.history.history import OsmoHistory
from pyosmo.osmomodel import OsmoModel


class OsmoEndCondition:
    """
    Abstract end condition class
    """

    @abstractmethod
    def end_test(self, history: OsmoHistory, model: OsmoModel) -> bool:
        raise Exception("This is not implemented!")

    @abstractmethod
    def end_suite(self, history: OsmoHistory, model: OsmoModel) -> bool:
        raise Exception("This is not implemented!")
