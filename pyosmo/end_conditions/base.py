from abc import abstractmethod


class OsmoEndCondition:
    """
    Abstract end condition class
    """

    @abstractmethod
    def end_test(self, history, model):
        raise Exception("This is not implemented!")

    @abstractmethod
    def end_suite(self, history, model):
        raise Exception("This is not implemented!")
