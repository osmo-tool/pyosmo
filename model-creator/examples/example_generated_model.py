"""
Example of a generated PyOsmo model for website testing.
This is a demonstration of what the model creator generates.

Base URL: https://example.com
Generated: Example model for demonstration
"""

try:
    import requests
except ImportError:
    raise ImportError('Model requires requests library. Install with: pip install requests')

from pyosmo import Osmo
from pyosmo.decorators import guard, step


class ExampleWebsiteModel:
    """
    Model-based testing for https://example.com

    This is an example generated model showing the structure and
    patterns used by the PyOsmo model creator.
    """

    def __init__(self):
        """Initialize the model state."""
        self.base_url = 'https://example.com'
        self.session = requests.Session()
        self.logged_in = False
        self.current_user: str | None = None
        self.current_page = 'home'
        self.response = None
        self.last_error: str | None = None

    def before_test(self):
        """Called before each test run."""
        self.session = requests.Session()
        self.logged_in = False
        self.current_page = 'home'
        self.current_user = None
        self.last_error = None
        print('Starting new test run')

    def after_test(self):
        """Called after each test run."""
        self.session.close()
        print('Test run completed')

    def after(self):
        """Called after each step - verification point."""
        if self.response is not None:
            # Verify response is valid
            assert self.response.status_code < 500, f'Server error: {self.response.status_code}'

            # Could add more sophisticated error checking here
            if self.response.status_code == 200:
                pass

    # --- Form Submission Actions ---

    @step
    @guard(lambda self: not self.logged_in)
    def submit_login(self):
        """Submit the login form."""
        data = {
            'username': 'testuser',
            'password': 'testpassword123',
        }

        self.response = self.session.post(
            'https://example.com/auth/login',
            data=data,
        )

        # Update login state on success
        if self.response.status_code == 200:
            self.logged_in = True
            self.current_user = data.get('username')

        self.current_page = 'login'
        print('Executed: submit_login')

    @step
    @guard(lambda self: not self.logged_in)
    def submit_register(self):
        """Submit the registration form."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'confirm_password': 'testpassword123',
        }

        self.response = self.session.post(
            'https://example.com/auth/register',
            data=data,
        )

        self.current_page = 'register'
        print('Executed: submit_register')

    @step
    @guard(lambda self: self.logged_in)
    def submit_logout(self):
        """Submit the logout form."""
        data = {}

        self.response = self.session.post(
            'https://example.com/auth/logout',
            data=data,
        )

        # Update logout state
        self.logged_in = False
        self.current_user = None
        self.current_page = 'logout'
        print('Executed: submit_logout')

    @step
    def submit_contact(self):
        """Submit the contact form."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'test_message',
        }

        self.response = self.session.post(
            'https://example.com/contact',
            data=data,
        )

        self.current_page = 'contact'
        print('Executed: submit_contact')

    @step
    def submit_search(self):
        """Submit the search form."""
        data = {
            'q': 'test_q',
        }

        self.response = self.session.get(
            'https://example.com/search',
            params=data,
        )

        self.current_page = 'search'
        print('Executed: submit_search')

    # --- Navigation Actions ---

    @step
    def navigate_to_home(self):
        """Navigate to home."""
        self.response = self.session.get('https://example.com')
        self.current_page = 'home'
        print('Navigated to: home')

    @step
    def navigate_to_about(self):
        """Navigate to about."""
        self.response = self.session.get('https://example.com/about')
        self.current_page = 'about'
        print('Navigated to: about')

    @step
    def navigate_to_contact(self):
        """Navigate to contact."""
        self.response = self.session.get('https://example.com/contact')
        self.current_page = 'contact'
        print('Navigated to: contact')

    @step
    @guard(lambda self: not self.logged_in)
    def navigate_to_login(self):
        """Navigate to login."""
        self.response = self.session.get('https://example.com/login')
        self.current_page = 'login'
        print('Navigated to: login')

    @step
    @guard(lambda self: self.logged_in)
    def navigate_to_dashboard(self):
        """Navigate to dashboard."""
        self.response = self.session.get('https://example.com/dashboard')
        self.current_page = 'dashboard'
        print('Navigated to: dashboard')


def main():
    """Run the model with PyOsmo."""
    model = ExampleWebsiteModel()

    osmo = Osmo(model).weighted_algorithm().stop_after_steps(100).run_tests(1)

    print(f'Starting test generation for {model.base_url}')
    osmo.generate()

    # Print summary
    stats = osmo.history.statistics()
    print('\n' + '=' * 50)
    print('Test generation complete!')
    print(f'Steps executed: {stats.total_steps}')
    print(f'Unique steps: {len(stats.step_coverage)}')


if __name__ == '__main__':
    main()
