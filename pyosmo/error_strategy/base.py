from abc import ABC, abstractmethod

from pyosmo.history.history import OsmoHistory
from pyosmo.model import OsmoModelCollector


class OsmoErrorStrategy(ABC):
    """
    Abstract class for defining how to behave in case of failure
    """

    @abstractmethod
    def failure_in_test(self, history: OsmoHistory, model: OsmoModelCollector, error: BaseException) -> None:
        raise Exception('This is not implemented!')

    def failure_in_suite(self, history: OsmoHistory, model: OsmoModelCollector, error: BaseException) -> None:
        """Handle suite-level failures. By default delegates to failure_in_test."""
        self.failure_in_test(history, model, error)
