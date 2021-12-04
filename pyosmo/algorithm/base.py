from abc import abstractmethod


class OsmoAlgorithm:
    random = None
    model = None

    def __init__(self):
        pass

    def initialize(self, random, model):
        """
        Initialize Osmo algorithm
        :param random: Used random
        :param model: The test model
        """
        self.random = random
        self.model = model

    @abstractmethod
    def choose(self, history, choices):
        raise Exception("This is just abstract class, not implementation")
