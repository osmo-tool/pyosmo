# pylint: disable=bare-except,broad-except
import logging
from datetime import datetime

from pyosmo.config import OsmoConfig
from pyosmo.history.history import OsmoHistory
from pyosmo.model import OsmoModelCollector, TestStep

logger = logging.getLogger('osmo')


class Osmo(OsmoConfig):
    """ Osmo tester core """

    def __init__(self, model: object = None):
        """ Osmo need at least one model to work """
        super().__init__()
        self.model = OsmoModelCollector()
        if model:
            self.add_model(model)
        self.history = OsmoHistory()

    @staticmethod
    def _check_model(model: object):
        """ Check that model is valid"""
        if not hasattr(model, '__class__'):
            raise Exception("Osmo model need to be instance of model, not just class")

    def add_model(self, model: object):
        """ Add model for osmo """
        logger.debug(f'Add model:{model}')
        self._check_model(model)
        self.model.add_model(model)

    def _run_step(self, step: TestStep):
        """
        Run step and save it to the history
        :param step: Test step
        :return:
        """
        logger.debug(f'Run step: {step}')
        start_time = datetime.now()
        try:
            step.execute()
            self.history.add_step(step, datetime.now() - start_time)
        except Exception as error:
            self.history.add_step(step, datetime.now() - start_time, error)
            raise error

    def run(self):
        """ Same as generate but in online usage this sounds more natural"""
        self.generate()

    def generate(self):
        """ Generate / run tests """
        logger.debug('Start generation..')
        logger.info(f'Using seed: {self.seed}')
        # Initialize algorithm
        self.algorithm.initialize(self.random, self.model)

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
                    step = self.algorithm.choose(self.history, self.model.available_steps)
                    self.model.execute_optional(f'pre_{step}')
                    try:
                        self._run_step(step)
                    except BaseException as error:
                        self.test_error_strategy.failure_in_test(self.history, self.model, error)
                    self.model.execute_optional(f'post_{step.name}')
                    # General after step which is run after each step
                    self.model.execute_optional('after')

                    if self.test_end_condition.end_test(self.history, self.model):
                        break
                self.model.execute_optional('after_test')
            except BaseException as error:
                self.test_suite_error_strategy.failure_in_suite(self.history, self.model, error)
            if self.test_suite_end_condition.end_suite(self.history, self.model):
                break
        self.model.execute_optional('after_suite')
        self.history.stop()
