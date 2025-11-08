"""
Example of a generated PyOsmo model for website testing.
This is a demonstration of what the model creator generates.

Base URL: https://example.com
Generated: Example model for demonstration
"""

import random
from typing import Optional

try:
    import requests
except ImportError:
    raise ImportError(
        "Model requires requests library. Install with: pip install requests"
    )


class ExampleWebsiteModel:
    """
    Model-based testing for https://example.com

    This is an example generated model showing the structure and
    patterns used by the PyOsmo model creator.
    """

    def __init__(self):
        """Initialize the model state."""
        self.base_url = "https://example.com"
        self.session = requests.Session()
        self.logged_in = False
        self.current_user: Optional[str] = None
        self.current_page = "home"
        self.response = None
        self.last_error: Optional[str] = None

    def before_test(self):
        """Called before each test run."""
        self.session = requests.Session()
        self.logged_in = False
        self.current_page = "home"
        self.current_user = None
        self.last_error = None
        print("Starting new test run")

    def after_test(self):
        """Called after each test run."""
        self.session.close()
        print("Test run completed")

    def after(self):
        """Called after each step - verification point."""
        if self.response is not None:
            # Verify response is valid
            assert self.response.status_code < 500, \
                f"Server error: {self.response.status_code}"

            # Check for error messages if we expect success
            if self.response.status_code == 200:
                # Could add more sophisticated error checking here
                pass

    # --- Form Submission Actions ---

    def step_submit_login(self):
        """Submit the login form."""
        data = {
            "username": "testuser",
            "password": "testpassword123",
        }

        self.response = self.session.post(
            "https://example.com/auth/login",
            data=data,
        )

        # Update login state on success
        if self.response.status_code == 200:
            self.logged_in = True
            self.current_user = data.get("username")

        self.current_page = "login"
        print("Executed: submit_login")

    def guard_submit_login(self):
        """Guard for submit_login."""
        # Can only login when not logged in
        return not self.logged_in

    def step_submit_register(self):
        """Submit the registration form."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "confirm_password": "testpassword123",
        }

        self.response = self.session.post(
            "https://example.com/auth/register",
            data=data,
        )

        self.current_page = "register"
        print("Executed: submit_register")

    def guard_submit_register(self):
        """Guard for submit_register."""
        # Can only register when not logged in
        return not self.logged_in

    def step_submit_logout(self):
        """Submit the logout form."""
        data = {}

        self.response = self.session.post(
            "https://example.com/auth/logout",
            data=data,
        )

        # Update logout state
        self.logged_in = False
        self.current_user = None
        self.current_page = "logout"
        print("Executed: submit_logout")

    def guard_submit_logout(self):
        """Guard for submit_logout."""
        # Can only logout when logged in
        return self.logged_in

    def step_submit_contact(self):
        """Submit the contact form."""
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "message": "test_message",
        }

        self.response = self.session.post(
            "https://example.com/contact",
            data=data,
        )

        self.current_page = "contact"
        print("Executed: submit_contact")

    def guard_submit_contact(self):
        """Guard for submit_contact."""
        return True

    def step_submit_search(self):
        """Submit the search form."""
        data = {
            "q": "test_q",
        }

        self.response = self.session.get(
            "https://example.com/search",
            params=data,
        )

        self.current_page = "search"
        print("Executed: submit_search")

    def guard_submit_search(self):
        """Guard for submit_search."""
        return True

    # --- Navigation Actions ---

    def step_navigate_to_home(self):
        """Navigate to home."""
        self.response = self.session.get("https://example.com")
        self.current_page = "home"
        print("Navigated to: home")

    def guard_navigate_to_home(self):
        """Guard for navigate_to_home."""
        return True

    def step_navigate_to_about(self):
        """Navigate to about."""
        self.response = self.session.get("https://example.com/about")
        self.current_page = "about"
        print("Navigated to: about")

    def guard_navigate_to_about(self):
        """Guard for navigate_to_about."""
        return True

    def step_navigate_to_contact(self):
        """Navigate to contact."""
        self.response = self.session.get("https://example.com/contact")
        self.current_page = "contact"
        print("Navigated to: contact")

    def guard_navigate_to_contact(self):
        """Guard for navigate_to_contact."""
        return True

    def step_navigate_to_login(self):
        """Navigate to login."""
        self.response = self.session.get("https://example.com/login")
        self.current_page = "login"
        print("Navigated to: login")

    def guard_navigate_to_login(self):
        """Guard for navigate_to_login."""
        # Only show login page when not logged in
        return not self.logged_in

    def step_navigate_to_dashboard(self):
        """Navigate to dashboard."""
        self.response = self.session.get("https://example.com/dashboard")
        self.current_page = "dashboard"
        print("Navigated to: dashboard")

    def guard_navigate_to_dashboard(self):
        """Guard for navigate_to_dashboard."""
        # Dashboard requires authentication
        return self.logged_in

    # --- Optional: Custom Methods ---

    def weight_submit_login(self):
        """Make login more likely when not logged in."""
        return 10 if not self.logged_in else 1

    def weight_navigate_to_dashboard(self):
        """Dashboard is important - visit it more often when logged in."""
        return 15 if self.logged_in else 0
