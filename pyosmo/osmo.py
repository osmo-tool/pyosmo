import random
import time

from pyosmo.model import Model
from pyosmo.config import OsmoConfig
from pyosmo.history import OsmoHistory


class Osmo(object):
    """ Osmo tester core """

    def __init__(self, model, seed=None):
        """ Osmo need at least one model to work """
        self._checkModel(model)
        self.model = Model()
        if model:
            self.model.add_model(model)
        self.history = OsmoHistory()
        self._config = OsmoConfig()
        self.current_test_number = 0
        self.failed_tests = 0
        self.debug = False

        if seed is None:
            self.seed = random.randint(0, 10000)
        else:
            self.seed = seed
        self.random = random.Random(self.seed)
        print("Using seed: {}".format(self.seed))

    def p(self, text):
        """ Print debugging texts if debug is enabled """
        if self.debug:
            print(text)

    def set_debug(self, debug):
        self.debug = debug

    def _checkModel(self, model):
        """ Check that model is valid"""
        if type(model) == type(Osmo):
            raise Exception("Osmo model need to be instance of model, not just class")

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        if not isinstance(value, OsmoConfig):
            raise AttributeError("config needs to be OsmoConfig.")
        self._config = value

    def set_algorithm(self, algorithm):
        """
        Set algorithm for configuration of osmo.

        :param algorithm: Algorithm object.
        :return: Nothing
        """
        self._config.algorithm = algorithm

    @property
    def algorithm(self):
        return self._config.algorithm

    @algorithm.setter
    def algorithm(self, value):
        self._config.algorithm = value

    @property
    def tests_in_a_suite(self):
        return self._config.tests_in_a_suite

    @tests_in_a_suite.setter
    def tests_in_a_suite(self, value):
        self._config.tests_in_a_suite = value

    @property
    def steps_in_a_test(self):
        return self._config.steps_in_a_test

    @steps_in_a_test.setter
    def steps_in_a_test(self, value):
        self._config.steps_in_a_test = value

    @property
    def stop_on_fail(self):
        """
        Set stop_on_fail value for configuration of osmo.

        :return: Nothing
        """
        return self._config.stop_on_fail

    @stop_on_fail.setter
    def stop_on_fail(self, value):
        self._config.stop_on_fail = value

    @property
    def stop_test_on_exception(self):
        """
        Set stop_test_on_exception for configuration of osmo.

        :return: Nothing
        """
        return self._config.stop_test_on_exception

    @stop_test_on_exception.setter
    def stop_test_on_exception(self, value):
        self._config.stop_test_on_exception = value

    def add_model(self, model):
        """ Add model for osmo """
        self._checkModel(model)
        self.model.add_model(model)

    def _execute_step(self, ending):
        """
        Execute step and save it to the history
        :param ending: letter after step_
        :return:
        """
        step_name = 'step_{}'.format(ending)
        start_time = time.time()
        self.model.execute(step_name)
        self.history.add_step(step_name, time.time() - start_time)

    def should_end_suite(self):
        """
        Check if suite should be ended.

        :return: Boolean
        """
        if self.current_test_number == self.tests_in_a_suite:
            return True
        elif self.stop_on_fail and self.failed_tests:
            return True
        return False

    def generate(self):
        """ Generate / run tests """

        # Initialize algorithm
        self.algorithm.inititalize(self.random, self.model)

        self.model.execute_optional('before_suite')
        if not self.tests_in_a_suite:
            raise Exception("Empty model!")

        while not self.should_end_suite():
            self.history.start_new_test()
            self.current_test_number += 1
            self.model.execute_optional('before_test')
            for _ in range(self.steps_in_a_test):
                # Use algorithm to select the step
                self.model.execute_optional('before')
                ending = self.algorithm.choose(self.history,
                                               self.model.get_list_of_available_steps())
                self.model.execute_optional('pre_{}'.format(ending))
                try:
                    returnvalue = self._execute_step(ending)
                    returnvalue = returnvalue if returnvalue is not None else True
                    if not returnvalue:
                        self.p("Step {} returned false. Stopping this test.".format(ending))
                        self.failed_tests += 1
                        break
                except Exception as error:
                    self.p(error)
                    self.failed_tests += 1
                    if self.stop_test_on_exception:
                        self.p("Step {} raised an exception. Stopping this test.".format(ending))
                        raise error
                self.model.execute_optional('post_{}'.format(ending))
                # General after step which is run after each step
                self.model.execute_optional('after')
            self.model.execute_optional('after_test')
        self.model.execute_optional('after_suite')
        self.history.stop()
