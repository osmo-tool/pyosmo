"""Page Object Model (POM) example using guard_all.

Demonstrates how to use guard_all to model page-based navigation
where each page is a separate model class. Only the steps belonging
to the current page are available at any time.

Run: python examples/page_object_model.py
"""

from pyosmo import Osmo, guard, step
from pyosmo.end_conditions import Length


class AppState:
    """Shared state across all page models."""

    def __init__(self):
        self.current_page = 'home'
        self.logged_in = False
        self.actions: list[str] = []


class HomePage:
    def __init__(self, state: AppState):
        self.state = state

    def guard_all(self):
        """All steps in this model require being on the home page."""
        return self.state.current_page == 'home'

    @step
    def click_login(self):
        self.state.actions.append('home -> login')
        self.state.current_page = 'login'

    @step
    def click_about(self):
        self.state.actions.append('home -> about')
        self.state.current_page = 'about'


class LoginPage:
    def __init__(self, state: AppState):
        self.state = state

    def guard_all(self):
        return self.state.current_page == 'login'

    @step
    @guard(lambda self: not self.state.logged_in)
    def submit_login(self):
        """Can only log in when not already logged in."""
        self.state.actions.append('login: submit')
        self.state.logged_in = True
        self.state.current_page = 'dashboard'

    @step
    def click_back(self):
        self.state.actions.append('login -> home')
        self.state.current_page = 'home'


class AboutPage:
    def __init__(self, state: AppState):
        self.state = state

    def guard_all(self):
        return self.state.current_page == 'about'

    @step
    def click_home(self):
        self.state.actions.append('about -> home')
        self.state.current_page = 'home'


class DashboardPage:
    def __init__(self, state: AppState):
        self.state = state

    def guard_all(self):
        return self.state.current_page == 'dashboard' and self.state.logged_in

    @step
    def logout(self):
        self.state.actions.append('dashboard: logout')
        self.state.logged_in = False
        self.state.current_page = 'home'

    @step
    def view_profile(self):
        self.state.actions.append('dashboard: view profile')


if __name__ == '__main__':
    state = AppState()
    osmo = Osmo([HomePage(state), LoginPage(state), AboutPage(state), DashboardPage(state)])
    osmo.test_end_condition = Length(20)
    osmo.seed = 42

    osmo.run()

    print('Actions taken:')
    for action in state.actions:
        print(f'  {action}')
    print(f'\nFinal page: {state.current_page}')
    print(f'Logged in: {state.logged_in}')
