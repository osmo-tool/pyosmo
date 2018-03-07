class Model(object):
    default_weight = 50

    def __init__(self):
        # Format: functions[function_name] = link_of_instance
        self.functions = dict()
        self.debug = False

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

    def execute_optional(self, function):
        """ Execute if function is available """
        if function in self.functions:
            return self.execute(function)

    @property
    def function_names(self):
        return self.functions.keys()

    def get_list_of_available_steps(self):
        available_steps = []
        for function in self.function_names:
            if function.startswith('step_'):
                step_name = function[5:]
                guard_name = 'guard_{}'.format(step_name)
                # If cannot find guard expect that state is always possible
                if guard_name not in self.functions.keys() or self.execute(guard_name):
                    available_steps.append(step_name)

        if len(available_steps) == 0:
            raise Exception('Cannot find any available states')
        return available_steps

    def get_step_weight(self, step_ending):
        weight_function = 'weight_{}'.format(step_ending)
        if weight_function in self.function_names:
            weight = self.execute(weight_function)
            try:
                return float(weight)
            except:
                raise Exception("ERROR: {}() have to return integer!".format(weight_function))
        # Return default weight
        return self.default_weight

    def execute(self, function):
        """ Execute a function and return its return value """
        try:
            return getattr(self.functions[function], function)()
        except AttributeError:
            raise Exception("Osmo cannot find function {}.{} from model".format(self.functions[function], function))
