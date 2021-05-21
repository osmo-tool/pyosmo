# pylint: disable=bare-except
import logging
import random
import time

from pyosmo.config import OsmoConfig
from pyosmo.history import OsmoHistory
from pyosmo.model import Model

logger = logging.getLogger('osmo')
logger.setLevel(logging.INFO)


class Osmo:
    """ Osmo tester core """

    def __init__(self, model=None):
        """ Osmo need at least one model to work """
        self.model = Model()
        if model:
            self.add_model(model)
        self.history = OsmoHistory()
        self._config = OsmoConfig()
        self.random = None
        self.seed = None

    def set_seed(self, seed=None):
        if seed is None:
            # Generate new seed if not given
            self.seed = random.randint(0, 10000)
        else:
            self.seed = seed
        self.random = random.Random(self.seed)
        logger.info("Using seed: {}".format(self.seed))

    @staticmethod
    def _check_model(model):
        """ Check that model is valid"""
        if not hasattr(model, '__class__'):
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
    def test_failure_strategy(self):
        return self._config.test_failure_strategy

    @test_failure_strategy.setter
    def test_failure_strategy(self, value):
        self._config.test_failure_strategy = value

    @property
    def test_suite_failure_strategy(self):
        return self._config.test_suite_failure_strategy

    @test_suite_failure_strategy.setter
    def test_suite_failure_strategy(self, value):
        self._config.test_suite_failure_strategy = value

    def set_test_end_condition(self, end_condition):
        self._config.test_end_condition = end_condition

    def set_suite_end_condition(self, end_condition):
        self._config.test_suite_end_condition = end_condition

    def add_model(self, model):
        """ Add model for osmo """
        logger.debug("Add model:{}".format(model))
        self._check_model(model)
        self.model.add_model(model)

    def _execute_step(self, step):
        """
        Execute step and save it to the history
        :param step: Test step
        :return:
        """
        logger.debug('Execute step: {}'.format(step))
        start_time = time.time()
        try:
            step.execute()
            self.history.add_step(step, time.time() - start_time)
        except Exception as error:
            self.history.add_step(step, time.time() - start_time, error)
            raise error

    def generate(self, seed=None):
        """ Generate / run tests """
        logger.debug('Start generation..')
        self.set_seed(seed)
        # Initialize algorithm
        self.algorithm.inititalize(self.random, self.model)

        self.model.execute_optional('before_suite')
        if not len(self.model.all_steps):
            raise Exception("Empty model!")

        while True:
            try:
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
                    except BaseException as error:
                        self.config.test_failure_strategy.failure_in_test(self.history, self.model, error)
                    self.model.execute_optional('post_{}'.format(step.name))
                    # General after step which is run after each step
                    self.model.execute_optional('after')

                    if self._config.test_end_condition.end_test(self.history, self.model):
                        break
                self.model.execute_optional('after_test')

                if self._config.test_suite_end_condition.end_suite(self.history, self.model):
                    break
            except BaseException as error:
                self.config.test_suite_failure_strategy.failure_in_suite(self.history, self.model, error)
        self.model.execute_optional('after_suite')
        self.history.stop()
