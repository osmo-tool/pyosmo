from abc import abstractmethod


class OsmoErrorStrategy:
    """
    Abstract class for defining how to behave in case of failure
    """

    @abstractmethod
    def failure_in_test(self, history, model, error):
        raise Exception("This is not implemented!")

    @abstractmethod
    def failure_in_suite(self, history, model, error):
        raise Exception("This is not implemented!")
