import random

from model import Model
from history import OsmoHistory
import time
from pyosmo.algorithm.random import RandomAlgorithm


class Osmo(object):
    """ Osmo tester core """

    def __init__(self, model, seed=None):
        """ Osmo need at least one model to work """
        self.model = Model()
        self.model.add_model(model)
        self.history = OsmoHistory()
        self.tests_in_a_suite = 10
        self.steps_in_a_test = 10
        self.debug = False
        # Use random as default algorithm
        self.algorithm = RandomAlgorithm()

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

    def generate(self):
        """ Generate / run tests """

        # Initialize algorithm
        self.algorithm.inititalize(self.random, self.model)

        self.model.execute_optional('before_suite')
        if not self.tests_in_a_suite:
            raise Exception("Empty model!")

        for _ in range(self.tests_in_a_suite):
            self.history.start_new_test()
            self.model.execute_optional('before_test')
            for _ in range(self.steps_in_a_test):
                # Use algorithm to select the step
                ending = self.algorithm.choose(self.history, self.model.get_list_of_available_steps())
                self.model.execute_optional('pre_{}'.format(ending))
                self._execute_step(ending)
                self.model.execute_optional('post_{}'.format(ending))
                # General after step which is run after each step
                self.model.execute_optional('after')
            self.model.execute_optional('after_test')
        self.model.execute_optional('after_suite')
        self.history.stop()
