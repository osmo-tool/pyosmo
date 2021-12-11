import logging
from typing import List

logger = logging.getLogger('osmo')


class OsmoModel:
    pass


class ModelFunction:
    """ Generic function class containing basic functionality of model functions"""

    def __init__(self, function_name, object_instance):
        self.function_name = function_name
        self.object_instance = object_instance  # Instance of model class

    @property
    def default_weight(self):
        try:
            return self.object_instance.weight
        except AttributeError:
            return 0

    @property
    def func(self):
        return getattr(self.object_instance, self.function_name)

    def execute(self):
        try:
            return self.func()
        except AttributeError as e:
            raise Exception(
                f"Osmo cannot find function {self.object_instance}.{self.function_name} from model") from e

    def __str__(self):
        return f"{type(self.object_instance).__name__}.{self.function_name}()"


class TestStep(ModelFunction):

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

    @property
    def weight(self):
        weight_function = self.return_function_if_exits(f'weight_{self.name}')
        if weight_function is not None:
            return float(weight_function.execute())
        if 'weight' in dir(self.func):
            return self.func.weight  # Noqa
        return self.default_weight  # Default value

    @property
    def is_available(self):
        """ Check if step is available right now """
        return True if self.guard_function is None else self.guard_function.execute()

    @property
    def guard_function(self):
        """ return guard function if exists """
        return self.return_function_if_exits(self.guard_name)

    def return_function_if_exits(self, name):
        if name in dir(self.object_instance):
            return ModelFunction(name, self.object_instance)
        return None


class OsmoModelCollector:
    """ The whole model that osmo has in "mind" which may contain multiple partial models """

    def __init__(self):
        # Format: functions[function_name] = link_of_instance
        self.sub_models = []
        self.debug = False

    @property
    def all_steps(self) -> iter:
        return (TestStep(f, sub_model) for sub_model in self.sub_models for f in dir(sub_model) if
                hasattr(getattr(sub_model, f), '__call__') and f.startswith('step_'))

    def get_step_by_name(self, name) -> TestStep:
        """ Get step by function name """
        steps = (TestStep(f, sub_model) for sub_model in self.sub_models for f in dir(sub_model) if
                 hasattr(getattr(sub_model, f), '__call__') and f == name)
        for step in steps:
            return step
        return None  # noqa

    def functions_by_name(self, name: str) -> iter:
        return (ModelFunction(f, sub_model) for sub_model in self.sub_models for f in dir(sub_model) if
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

    def execute_optional(self, function_name) -> None:
        """ Execute all this name functions if available """
        for function in self.functions_by_name(function_name):
            logger.debug(f'Execute: {function}')
            function.execute()

    @property
    def available_steps(self) -> List[TestStep]:
        """ Return iterator for all available steps """
        return list(filter(lambda x: x.is_available, self.all_steps))
