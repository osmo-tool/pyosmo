import logging
from functools import cached_property
from typing import List

logger = logging.getLogger('osmo')


class Function:

    def __init__(self, function_name, object_instance):
        self.function_name = function_name
        self.object_instance = object_instance  # Instance of model class

    def execute(self):
        try:
            return getattr(self.object_instance, self.function_name)()
        except AttributeError as e:
            raise Exception(
                f"Osmo cannot find function {self.object_instance}.{self.function_name} from model") from e

    def __str__(self):
        return f"{type(self.object_instance).__name__}.{self.function_name}()"


class TestStep(Function):

    def __init__(self, function_name, object_instance):
        assert function_name.startswith('step_'), 'Wrong name function'
        super().__init__(function_name, object_instance)

    @property
    def name(self):
        """ name means the part after 'step_' """
        return self.function_name[5:]

    @property
    def guard_name(self):
        return f'guard_{self.name}'

    @cached_property
    def weight(self):
        if self.weight_function is not None:
            return float(self.weight_function.execute())
        return 1  # The default value

    @property
    def weight_name(self):
        return f'weight_{self.name}'

    @property
    def weight_function(self):
        """ return guard function if exists """
        return self.return_function_if_exits(self.weight_name)

    @property
    def guard_function(self):
        """ return guard function if exists """
        return self.return_function_if_exits(self.guard_name)

    def return_function_if_exits(self, name):
        if name in dir(self.object_instance):
            return Function(name, self.object_instance)
        return None


class Model:
    """ The whole model that osmo has in "mind" which may contain multiple partial models """

    def __init__(self):
        # Format: functions[function_name] = link_of_instance
        self.sub_models = []
        self.debug = False

    @property
    def all_steps(self):
        return [TestStep(f, sub_model) for sub_model in self.sub_models for f in dir(sub_model) if
                hasattr(getattr(sub_model, f), '__call__') and f.startswith('step_')]

    def get_step_by_name(self, name):
        """ Get step by function name """
        steps = [TestStep(f, sub_model) for sub_model in self.sub_models for f in dir(sub_model) if
                 hasattr(getattr(sub_model, f), '__call__') and f == name]
        if steps:
            return steps[0]
        return None

    def functions_by_name(self, name: str) -> iter:
        return (Function(f, sub_model) for sub_model in self.sub_models for f in dir(sub_model) if
                hasattr(getattr(sub_model, f), '__call__') and f == name)

    def add_model(self, model):
        """ Add model for osmo """
        try:
            model.__class__
        except AttributeError:
            # If not instance of class, create instance of it
            model = model()

        self.sub_models.append(model)
        logger.debug(f'Loaded model: {model.__class__}')

    def execute_optional(self, function_name):
        """ Execute all this name functions if available """
        for function in self.functions_by_name(function_name):
            logger.debug(f'Execute: {function}')
            function.execute()

    def available_steps(self) -> List[TestStep]:
        available_steps = []
        for step in self.all_steps:
            # If cannot find guard expect that state is always possible
            if step.guard_function is None or step.guard_function.execute():
                available_steps.append(step)

        if not available_steps:
            raise Exception('Cannot find any available states')
        return available_steps
