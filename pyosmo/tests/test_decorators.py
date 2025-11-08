"""Test decorator-based API"""

from pyosmo import Osmo, post, pre, requires, step, weight
from pyosmo.end_conditions import Length


class DecoratorModel:
    """Test model using decorator-based API"""

    def __init__(self):
        self.counter = 0
        self.logged_in = False
        self.pre_called = False
        self.post_called = False

    @step
    def login(self):
        """Login step using decorator"""
        self.logged_in = True
        self.counter += 1

    @step("custom_logout")
    def logout_method(self):
        """Logout step with custom name"""
        self.logged_in = False
        self.counter += 1

    @step(weight_value=10)
    def weighted_action(self):
        """Step with decorator-based weight"""
        self.counter += 1

    @pre("login")
    def before_login(self):
        """Pre-hook for login"""
        self.pre_called = True

    @post("custom_logout")
    def after_logout(self):
        """Post-hook for logout"""
        self.post_called = True


class MixedModel:
    """Test model using both naming convention and decorators"""

    def __init__(self):
        self.counter = 0

    # Naming convention
    def step_old_style(self):
        self.counter += 1

    # Decorator-based
    @step
    def new_style(self):
        self.counter += 1


def test_decorator_step():
    """Test basic @step decorator"""
    model = DecoratorModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(5)

    osmo.run()

    # Verify steps were executed
    assert model.counter > 0


def test_decorator_step_with_custom_name():
    """Test @step decorator with custom name"""
    model = DecoratorModel()
    osmo = Osmo(model)

    # Verify the step is discovered with custom name
    steps = list(osmo.model.all_steps)
    step_names = [s.name for s in steps]

    assert "custom_logout" in step_names
    assert "logout_method" not in step_names  # Function name should not be used


def test_decorator_weight():
    """Test @step with weight_value"""
    model = DecoratorModel()
    osmo = Osmo(model)

    steps = list(osmo.model.all_steps)
    weighted_step = next(s for s in steps if s.name == "weighted_action")

    assert weighted_step.weight == 10


def test_mixed_naming_conventions():
    """Test that both naming convention and decorators work together"""
    model = MixedModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(10)

    osmo.run()

    # Verify both steps were executed
    assert model.counter > 0

    # Verify both steps are discovered
    steps = list(osmo.model.all_steps)
    step_names = [s.name for s in steps]

    assert "old_style" in step_names
    assert "new_style" in step_names


def test_requires_decorator():
    """Test @requires decorator attaches metadata"""

    class RequirementsModel:
        @step
        @requires("REQ-001", "REQ-002")
        def checkout(self):
            pass

    model = RequirementsModel()
    method = model.checkout

    assert hasattr(method, "_osmo_requires")
    assert method._osmo_requires == ["REQ-001", "REQ-002"]


def test_legacy_weight_decorator():
    """Test that legacy @weight decorator still works"""

    class LegacyModel:
        def step_action(self):
            pass

        @weight(20)
        def weight_action(self):
            return 20

    model = LegacyModel()
    osmo = Osmo(model)

    steps = list(osmo.model.all_steps)
    action_step = next(s for s in steps if s.name == "action")

    # Weight function should be called
    assert action_step.weight == 20
