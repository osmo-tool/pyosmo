import random
import time

from pyosmo.model import Model
from pyosmo.config import OsmoConfig
from pyosmo.history import OsmoHistory


class Osmo(object):
    """ Osmo tester core """

    def __init__(self, model, seed=None):
        """ Osmo need at least one model to work """
        self.model = Model()
        self.model.add_model(model)
        self.history = OsmoHistory()
        self.config = OsmoConfig()
        self.tests_in_a_suite = 10
        self.steps_in_a_test = 10
        self.current_test_number = 0
        self.failed_tests = 0
        self.debug = False
        # Use random as default algorithm
        self.algorithm = self.config.algorithm

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

    def set_algorithm(self, algorithm):
        """
        Set algorithm for configuration of osmo.

        :param algorithm: Algorithm object.
        :return: Nothing
        """
        self.config.algorithm = algorithm
        self.algorithm = algorithm

    def stop_on_fail(self, value):
        """
        Set stop_on_fail value for configuration of osmo.

        :return: Nothing
        """
        self.config.stop_on_fail = value

    def add_model(self, model):
        """ Add model for osmo """
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
        elif self.config.stop_on_fail and self.failed_tests:
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
            try:
                for _ in range(self.steps_in_a_test):
                    # Use algorithm to select the step
                    ending = self.algorithm.choose(self.history,
                                                   self.model.get_list_of_available_steps())
                    self.model.execute_optional('pre_{}'.format(ending))
                    self._execute_step(ending)
                    self.model.execute_optional('post_{}'.format(ending))
                    # General after step which is run after each step
                    self.model.execute_optional('after')
            except Exception:
                self.failed_tests += 1
            self.model.execute_optional('after_test')
        self.model.execute_optional('after_suite')
        self.history.stop()
