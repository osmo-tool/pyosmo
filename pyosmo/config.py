from pyosmo.algorithm.random import RandomAlgorithm


class OsmoConfig(object):
    def __init__(self):
        self._stop_on_failure = True
        self._algorithm = RandomAlgorithm()
        self._stop_test_on_exception = True
        self._steps_in_a_test = 1
        self._tests_in_a_suite = 1

    @property
    def stop_on_fail(self):
        return self._stop_on_failure

    @stop_on_fail.setter
    def stop_on_fail(self, value):
        self._stop_on_failure = value

    @property
    def stop_test_on_exception(self):
        return self._stop_test_on_exception

    @stop_test_on_exception.setter
    def stop_test_on_exception(self, value):
        self._stop_test_on_exception = value

    @property
    def algorithm(self):
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value):
        self._algorithm = value

    @property
    def steps_in_a_test(self):
        return self._steps_in_a_test

    @steps_in_a_test.setter
    def steps_in_a_test(self, value):
        self._steps_in_a_test = value

    @property
    def tests_in_a_suite(self):
        return self._tests_in_a_suite

    @tests_in_a_suite.setter
    def tests_in_a_suite(self, value):
        self._tests_in_a_suite = value