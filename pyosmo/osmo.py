# pylint: disable=bare-except,broad-except
import logging
import time

from pyosmo.config import OsmoConfig
from pyosmo.history.history import OsmoHistory
from pyosmo.model import Model

logger = logging.getLogger('osmo')


class Osmo(OsmoConfig):
    """ Osmo tester core """

    def __init__(self, model=None):
        """ Osmo need at least one model to work """
        super().__init__()
        self.model = Model()
        if model:
            self.add_model(model)
        self.history = OsmoHistory()

    @staticmethod
    def _check_model(model):
        """ Check that model is valid"""
        if not hasattr(model, '__class__'):
            raise Exception("Osmo model need to be instance of model, not just class")

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

    def generate(self):
        """ Generate / run tests """
        logger.debug('Start generation..')
        logger.info("Using seed: {}".format(self.seed))
        # Initialize algorithm
        self.algorithm.inititalize(self.random, self.model)

        self.model.execute_optional('before_suite')
        if not self.model.all_steps:
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
                        self.test_error_strategy.failure_in_test(self.history, self.model, error)
                    self.model.execute_optional('post_{}'.format(step.name))
                    # General after step which is run after each step
                    self.model.execute_optional('after')

                    if self.test_end_condition.end_test(self.history, self.model):
                        break
                self.model.execute_optional('after_test')

                if self.test_suite_end_condition.end_suite(self.history, self.model):
                    break
            except BaseException as error:
                self.test_suite_error_strategy.failure_in_suite(self.history, self.model, error)
        self.model.execute_optional('after_suite')
        self.history.stop()
