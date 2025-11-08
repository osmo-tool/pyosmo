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

    @abstractmethod
    def choose(self, history: OsmoHistory, choices: list[TestStep]) -> TestStep:
        raise Exception('This is just abstract class, not implementation')
