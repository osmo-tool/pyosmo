from abc import abstractmethod
from random import Random
from typing import List

from pyosmo.history.history import OsmoHistory
from pyosmo.osmomodel import OsmoModel, TestStep


class OsmoAlgorithm:
    random = None
    model = None

    def __init__(self):
        pass

    def initialize(self, random: Random, model: OsmoModel):
        """
        Initialize Osmo algorithm
        :param random: Used random
        :param model: The test model
        """
        self.random = random
        self.model = model

    @abstractmethod
    def choose(self, history: OsmoHistory, choices: List[TestStep]) -> TestStep:
        raise Exception("This is just abstract class, not implementation")
