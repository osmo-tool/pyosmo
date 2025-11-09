"""Test decorator-based API"""

from pyosmo import Osmo, guard, post, pre, requires, step, weight
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

    @step('custom_logout')
    def logout_method(self):
        """Logout step with custom name"""
        self.logged_in = False
        self.counter += 1

    @step(weight_value=10)
    def weighted_action(self):
        """Step with decorator-based weight"""
        self.counter += 1

    @pre('login')
    def before_login(self):
        """Pre-hook for login"""
        self.pre_called = True

    @post('custom_logout')
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

    assert 'custom_logout' in step_names
    assert 'logout_method' not in step_names  # Function name should not be used


def test_decorator_weight():
    """Test @step with weight_value"""
    model = DecoratorModel()
    osmo = Osmo(model)

    steps = list(osmo.model.all_steps)
    weighted_step = next(s for s in steps if s.name == 'weighted_action')

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

    assert 'old_style' in step_names
    assert 'new_style' in step_names


def test_requires_decorator():
    """Test @requires decorator attaches metadata"""

    class RequirementsModel:
        @step
        @requires('REQ-001', 'REQ-002')
        def checkout(self):
            pass

    model = RequirementsModel()
    method = model.checkout

    assert hasattr(method, '_osmo_requires')
    assert method._osmo_requires == ['REQ-001', 'REQ-002']


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
    action_step = next(s for s in steps if s.name == 'action')

    # Weight function should be called
    assert action_step.weight == 20


def test_guard_decorator_with_step_name():
    """Test @guard("step_name") decorator"""

    class GuardModel:
        def __init__(self):
            self.ready = False
            self.process_called = False
            self.other_called = False

        @step
        def process(self):
            self.process_called = True

        @guard('process')
        def can_process(self) -> bool:
            return self.ready

        @step
        def other_step(self):
            self.other_called = True

    model = GuardModel()
    osmo = Osmo(model)

    # Process should not be available initially
    available_steps = osmo.model.available_steps
    step_names = [s.name for s in available_steps]
    assert 'process' not in step_names
    assert 'other_step' in step_names

    # Make process available
    model.ready = True
    available_steps = osmo.model.available_steps
    step_names = [s.name for s in available_steps]
    assert 'process' in step_names


def test_guard_decorator_inline():
    """Test @guard with inline lambda"""

    class InlineGuardModel:
        def __init__(self):
            self.counter = 0
            self.limit_reached = False

        @step
        @guard(lambda self: not self.limit_reached)
        def increment(self):
            self.counter += 1
            if self.counter >= 5:
                self.limit_reached = True

        @step
        def other_action(self):
            pass

    model = InlineGuardModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(10)

    osmo.run()

    # Should reach 5 and then stop incrementing due to guard
    assert model.counter == 5


def test_guard_decorator_with_invert():
    """Test @guard with invert parameter"""

    class InvertGuardModel:
        def __init__(self):
            self.blocked = True
            self.action_called = False

        @step
        def action(self):
            self.action_called = True

        @guard('action', invert=True)
        def is_blocked(self) -> bool:
            return self.blocked

    model = InvertGuardModel()
    osmo = Osmo(model)

    # Action should not be available when blocked=True (inverted)
    available_steps = osmo.model.available_steps
    step_names = [s.name for s in available_steps]
    assert 'action' not in step_names

    # Make action available by setting blocked=False
    model.blocked = False
    available_steps = osmo.model.available_steps
    step_names = [s.name for s in available_steps]
    assert 'action' in step_names


def test_guard_decorator_multiple_steps():
    """Test multiple guards for different steps"""

    class MultiGuardModel:
        def __init__(self):
            self.logged_in = False
            self.has_items = False

        @step
        def login(self):
            self.logged_in = True

        @step
        def checkout(self):
            pass

        @guard('login')
        def can_login(self) -> bool:
            return not self.logged_in

        @guard('checkout')
        def can_checkout(self) -> bool:
            return self.logged_in and self.has_items

    model = MultiGuardModel()
    osmo = Osmo(model)

    # Initially, only login is available
    available_steps = osmo.model.available_steps
    step_names = [s.name for s in available_steps]
    assert 'login' in step_names
    assert 'checkout' not in step_names

    # After login, checkout still not available (no items)
    model.logged_in = True
    available_steps = osmo.model.available_steps
    step_names = [s.name for s in available_steps]
    assert 'login' not in step_names  # Can't login again
    assert 'checkout' not in step_names

    # After adding items, checkout is available
    model.has_items = True
    available_steps = osmo.model.available_steps
    step_names = [s.name for s in available_steps]
    assert 'checkout' in step_names


def test_guard_mixing_decorator_and_naming_convention():
    """Test that decorator guards work alongside naming convention guards"""

    class MixedGuardModel:
        def __init__(self):
            self.flag_a = True
            self.flag_b = True

        @step
        def action_a(self):
            pass

        @guard('action_a')
        def guard_for_a(self) -> bool:
            return self.flag_a

        def step_action_b(self):
            pass

        def guard_action_b(self) -> bool:
            return self.flag_b

    model = MixedGuardModel()
    osmo = Osmo(model)

    # Both should be available initially
    available_steps = osmo.model.available_steps
    step_names = [s.name for s in available_steps]
    assert 'action_a' in step_names
    assert 'action_b' in step_names

    # Disable decorator-guarded step
    model.flag_a = False
    available_steps = osmo.model.available_steps
    step_names = [s.name for s in available_steps]
    assert 'action_a' not in step_names
    assert 'action_b' in step_names

    # Disable naming-convention-guarded step
    model.flag_a = True
    model.flag_b = False
    available_steps = osmo.model.available_steps
    step_names = [s.name for s in available_steps]
    assert 'action_a' in step_names
    assert 'action_b' not in step_names
