class Function:

    def __init__(self, function_name, object_instance):
        self.function_name = function_name
        self.object_instance = object_instance  # Instance of model class

    def execute(self):
        try:
            return getattr(self.object_instance, self.function_name)()
        except AttributeError:
            raise Exception(
                "Osmo cannot find function {}.{} from model".format(self.object_instance, self.function_name))

    def __str__(self):
        return "{}.{}()".format(self.object_instance, self.function_name)


class TestStep(Function):

    def __init__(self, function_name, model):
        assert function_name.startswith('step_'), 'Wrong name function'
        super().__init__(function_name, model)

    @property
    def name(self):
        """ name means the part after 'step_' """
        return self.function_name[5:]

    @property
    def guard_name(self):
        return 'guard_{}'.format(self.name)

    @property
    def weight_name(self):
        return 'weight_{}'.format(self.name)

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
    default_weight = 50

    def __init__(self):
        # Format: functions[function_name] = link_of_instance
        self.sub_models = list()
        self.debug = False

    def p(self, text):
        """ Print debugging texts if debug is enabled """
        if self.debug:
            print(text)

    def set_debug(self, debug):
        self.debug = debug

    @property
    def all_steps(self):
        return [TestStep(f, sub_model) for sub_model in self.sub_models for f in dir(sub_model) if
                hasattr(getattr(sub_model, f), '__call__') and f.startswith('step_')]

    def all_functions_by_name(self, name):
        return [Function(f, sub_model) for sub_model in self.sub_models for f in dir(sub_model) if
                hasattr(getattr(sub_model, f), '__call__') and f == name]

    def add_model(self, model):
        """ Add model for osmo """
        try:
            model.__class__
        except AttributeError:
            # If not instance of class, create instance of it
            model = model()

        self.sub_models.append(model)
        self.p('Loaded model: {}'.format(model.__class__))

    def execute_optional(self, function_name):
        """ Execute all this name functions if available """

        for function in self.all_functions_by_name(function_name):
            return function.execute()

    def get_list_of_available_steps(self):
        available_steps = []
        for step in self.all_steps:
            # If cannot find guard expect that state is always possible
            if step.guard_function is None or step.guard_function.execute():
                available_steps.append(step)

        if not available_steps:
            raise Exception('Cannot find any available states')
        return available_steps

    def get_step_weight(self, step):
        if step.weight_function:
            return float(step.weight_function.execute())
        # Return default weight
        return self.default_weight
