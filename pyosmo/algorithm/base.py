from abc import ABC, abstractmethod
from random import Random

from pyosmo.history.history import OsmoHistory
from pyosmo.model import OsmoModelCollector, TestStep


class OsmoAlgorithm(ABC):
    random: Random | None
    model: OsmoModelCollector | None

    def __init__(self) -> None:
        self.random = None
        self.model = None

    def initialize(self, random: Random, model: OsmoModelCollector) -> None:
        """
        Initialize Osmo algorithm
        :param random: Used random
        :param model: The test model
        """
        self.random = random
        self.model = model

    def _ensure_initialized(self) -> Random:
        """Return the Random instance, raising if not yet initialized."""
        if self.random is None:
            raise RuntimeError('Algorithm not initialized. Call initialize() first.')
        return self.random

    @abstractmethod
    def choose(self, history: OsmoHistory, choices: list[TestStep]) -> TestStep:
        raise Exception('This is just abstract class, not implementation')
