"""Test guard_all model-level guard and @model_guard decorator"""

from pyosmo import Osmo, guard, model_guard, step
from pyosmo.end_conditions import Length


class SimpleGuardAllModel:
    """Model with guard_all that controls all steps."""

    def __init__(self):
        self.active = True
        self.step_a_count = 0
        self.step_b_count = 0

    def guard_all(self):
        return self.active

    @step
    def step_a(self):
        self.step_a_count += 1

    @step
    def step_b(self):
        self.step_b_count += 1


def test_guard_all_allows_steps():
    """Steps are available when guard_all returns True."""
    model = SimpleGuardAllModel()
    osmo = Osmo(model)

    available = osmo.model.available_steps
    names = [s.name for s in available]
    assert 'step_a' in names
    assert 'step_b' in names


def test_guard_all_blocks_steps():
    """All steps are blocked when guard_all returns False."""
    model = SimpleGuardAllModel()
    model.active = False
    osmo = Osmo(model)

    available = osmo.model.available_steps
    assert len(available) == 0


def test_guard_all_dynamic_state():
    """guard_all responds to state changes during execution."""
    model = SimpleGuardAllModel()
    osmo = Osmo(model)

    # Initially available
    assert len(osmo.model.available_steps) == 2

    # Disable
    model.active = False
    assert len(osmo.model.available_steps) == 0

    # Re-enable
    model.active = True
    assert len(osmo.model.available_steps) == 2


def test_guard_all_with_per_step_guard():
    """guard_all and per-step guards both must pass."""

    class CombinedGuardModel:
        def __init__(self):
            self.model_active = True
            self.step_ready = True
            self.always_count = 0
            self.guarded_count = 0

        def guard_all(self):
            return self.model_active

        @step
        @guard(lambda self: self.step_ready)
        def guarded_step(self):
            self.guarded_count += 1

        @step
        def always_step(self):
            self.always_count += 1

    model = CombinedGuardModel()
    osmo = Osmo(model)

    # Both active: both steps available
    names = [s.name for s in osmo.model.available_steps]
    assert 'guarded_step' in names
    assert 'always_step' in names

    # guard_all True, per-step guard False: only always_step
    model.step_ready = False
    names = [s.name for s in osmo.model.available_steps]
    assert 'guarded_step' not in names
    assert 'always_step' in names

    # guard_all False: nothing available regardless of per-step guard
    model.model_active = False
    model.step_ready = True
    names = [s.name for s in osmo.model.available_steps]
    assert len(names) == 0


def test_guard_all_with_naming_convention_guard():
    """guard_all works with naming convention guards."""

    class NamingConventionModel:
        def __init__(self):
            self.model_active = True
            self.step_ready = True

        def guard_all(self):
            return self.model_active

        def step_action(self):
            pass

        def guard_action(self):
            return self.step_ready

    model = NamingConventionModel()
    osmo = Osmo(model)

    # Both pass
    names = [s.name for s in osmo.model.available_steps]
    assert 'action' in names

    # guard_all False
    model.model_active = False
    names = [s.name for s in osmo.model.available_steps]
    assert 'action' not in names

    # guard_all True, per-step False
    model.model_active = True
    model.step_ready = False
    names = [s.name for s in osmo.model.available_steps]
    assert 'action' not in names


def test_multi_model_guard_all():
    """Only the active model's steps are available in multi-model setup."""

    class ModelA:
        def __init__(self, state):
            self.state = state

        def guard_all(self):
            return self.state['active'] == 'A'

        @step
        def action_a(self):
            self.state['active'] = 'B'

    class ModelB:
        def __init__(self, state):
            self.state = state

        def guard_all(self):
            return self.state['active'] == 'B'

        @step
        def action_b(self):
            self.state['active'] = 'A'

    state = {'active': 'A'}
    model_a = ModelA(state)
    model_b = ModelB(state)
    osmo = Osmo([model_a, model_b])

    # Only model A steps available
    names = [s.name for s in osmo.model.available_steps]
    assert 'action_a' in names
    assert 'action_b' not in names

    # Switch state
    state['active'] = 'B'
    names = [s.name for s in osmo.model.available_steps]
    assert 'action_a' not in names
    assert 'action_b' in names


def test_multi_model_page_transitions():
    """Full page transition scenario with guard_all."""

    class PageHome:
        def __init__(self, state):
            self.state = state

        def guard_all(self):
            return self.state['page'] == 'home'

        @step
        def go_to_login(self):
            self.state['page'] = 'login'

    class PageLogin:
        def __init__(self, state):
            self.state = state

        def guard_all(self):
            return self.state['page'] == 'login'

        @step
        def do_login(self):
            self.state['page'] = 'dashboard'

        @step
        def go_back(self):
            self.state['page'] = 'home'

    class PageDashboard:
        def __init__(self, state):
            self.state = state

        def guard_all(self):
            return self.state['page'] == 'dashboard'

        @step
        def do_logout(self):
            self.state['page'] = 'home'

    state = {'page': 'home'}
    osmo = Osmo([PageHome(state), PageLogin(state), PageDashboard(state)])
    osmo.test_end_condition = Length(10)
    osmo.seed = 42

    osmo.run()

    # Test completed without error, transitions worked
    history = osmo.history
    assert len(history.test_cases) == 1
    assert len(history.test_cases[0].steps_log) == 10


def test_backward_compatibility_no_guard_all():
    """Models without guard_all work exactly as before."""

    class PlainModel:
        def __init__(self):
            self.count = 0

        @step
        def action(self):
            self.count += 1

    model = PlainModel()
    osmo = Osmo(model)
    osmo.test_end_condition = Length(5)

    osmo.run()

    assert model.count == 5


def test_model_guard_decorator():
    """@model_guard class decorator works like guard_all method."""

    @model_guard(lambda self: self.active)
    class DecoratedModel:
        def __init__(self):
            self.active = True
            self.count = 0

        @step
        def action(self):
            self.count += 1

    model = DecoratedModel()
    osmo = Osmo(model)

    # Active: step available
    names = [s.name for s in osmo.model.available_steps]
    assert 'action' in names

    # Inactive: step blocked
    model.active = False
    names = [s.name for s in osmo.model.available_steps]
    assert len(names) == 0


def test_model_guard_decorator_with_per_step_guard():
    """@model_guard combines with per-step guards."""

    @model_guard(lambda self: self.model_ok)
    class DecoratedGuardModel:
        def __init__(self):
            self.model_ok = True
            self.step_ok = True

        @step
        @guard(lambda self: self.step_ok)
        def guarded(self):
            pass

        @step
        def unguarded(self):
            pass

    model = DecoratedGuardModel()
    osmo = Osmo(model)

    # Both pass
    names = [s.name for s in osmo.model.available_steps]
    assert 'guarded' in names
    assert 'unguarded' in names

    # model_guard True, per-step False
    model.step_ok = False
    names = [s.name for s in osmo.model.available_steps]
    assert 'guarded' not in names
    assert 'unguarded' in names

    # model_guard False: nothing
    model.model_ok = False
    model.step_ok = True
    assert len(osmo.model.available_steps) == 0


def test_guard_all_naming_convention_steps():
    """guard_all works with naming convention steps (step_* methods)."""

    class NamingModel:
        def __init__(self):
            self.active = True
            self.count = 0

        def guard_all(self):
            return self.active

        def step_do_thing(self):
            self.count += 1

        def step_do_other(self):
            self.count += 1

    model = NamingModel()
    osmo = Osmo(model)

    names = [s.name for s in osmo.model.available_steps]
    assert 'do_thing' in names
    assert 'do_other' in names

    model.active = False
    assert len(osmo.model.available_steps) == 0
