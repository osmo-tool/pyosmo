import random
import time

from pyosmo.model import Model
from pyosmo.config import OsmoConfig
from pyosmo.history import OsmoHistory


class Osmo(object):
    """ Osmo tester core """

    def __init__(self, model=None):
        """ Osmo need at least one model to work """
        self.model = Model()
        if model:
            self.add_model(model)
        self.history = OsmoHistory()
        self._config = OsmoConfig()
        self.debug = False
        self.random = None
        self.seed = None

    def set_seed(self, seed=None):
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

    def set_test_end_condition(self, end_condition):
        self._config.test_end_condition = end_condition

    def set_suite_end_condition(self, end_condition):
        self._config.test_suite_end_condition = end_condition

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

    def _execute_step(self, step):
        """
        Execute step and save it to the history
        :param ending: letter after step_
        :return:
        """
        start_time = time.time()
        try:
            step.execute()
        except:
            raise
        finally:
            self.history.add_step(step, time.time() - start_time)

    def generate(self, seed=random.randint(0, 10000)):
        """ Generate / run tests """

        self.set_seed(seed)
        # Initialize algorithm
        self.algorithm.inititalize(self.random, self.model)

        self.model.execute_optional('before_suite')
        if not len(self.model.all_steps):
            raise Exception("Empty model!")

        while True:
            self.history.start_new_test()
            self.model.execute_optional('before_test')
            while True:
                # Use algorithm to select the step
                self.model.execute_optional('before')
                step = self.algorithm.choose(self.history,
                                             self.model.get_list_of_available_steps())
                self.model.execute_optional('pre_{}'.format(step))
                try:
                    self._execute_step(step)
                except Exception as error:
                    self.p(error)
                    if self.stop_test_on_exception:
                        self.p("Step {} raised an exception. Stopping this test.".format(step))
                        raise error
                self.model.execute_optional('post_{}'.format(step.name))
                # General after step which is run after each step
                self.model.execute_optional('after')

                if self._config.test_end_condition.end_test(self.history, self.model):
                    break
            self.model.execute_optional('after_test')

            if self._config.test_suite_end_condition.end_suite(self.history, self.model):
                break

        self.model.execute_optional('after_suite')
        self.history.stop()
