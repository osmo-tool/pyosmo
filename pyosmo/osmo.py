__author__ = 'olli-pekka puolitaival'

import random


class Osmo:
    """ Osmo tester core """
    functions = dict()  # functions[function_name] = link_of_instance
    debug = True
    tests_in_a_suite = 10
    steps_in_a_test = 10

    def __init__(self, model):
        """ Osmo need at least one model to work """
        self.add_model(model)

    def p(self, text):
        """ Print debugging texts if debug is enabled """
        if self.debug:
            print(text)

    def set_debug(self, debug):
        self.debug = debug

    def add_model(self, model):
        """ Add model for osmo """
        try:
            model.__class__
        except AttributeError:
            # If not instance of class, create instance of it
            model = model()
        for function in dir(model):
            if '__' not in function:
                self.functions[function] = model
        self.p('Loaded model: {}'.format(model.__class__))
        self.p('Functions: {}'.format(self.functions))

    def _execute_optional(self, function):
        """ Execute if function is available """
        if function in self.functions:
            return self._execute(function)

    def _execute(self, function):
        """ Execute a function and return its return value """
        try:
            return getattr(self.functions[function], function)()
        except AttributeError:
            raise Exception("Osmo cannot find function {}.{} from model".format(self.functions[function], function))

    def _get_list_of_available_steps(self):
        available_steps = []
        for function in self.functions.keys():
            if function.startswith('guard_'):
                if self._execute(function):
                    step_name = function[6:]
                    if 'step_{}'.format(step_name) in self.functions:
                        available_steps.append(step_name)
                    else:
                        raise Exception('OSMO cannot find {} for {}'.format(step_name, function))
        if len(available_steps) == 0:
            raise Exception('Cannot find any available states')
        return available_steps

    def generate(self):
        """ Generate / run tests """
        self._execute_optional('before_suite')
        for _ in range(self.tests_in_a_suite):
            self._execute_optional('before_test')
            for _ in range(self.steps_in_a_test):
                selected = random.choice(self._get_list_of_available_steps())
                self._execute_optional('pre_{}'.format(selected))
                self._execute('step_{}'.format(selected))
                self._execute_optional('post_{}'.format(selected))
            self._execute_optional('after_test')
        self._execute_optional('after_suite')


