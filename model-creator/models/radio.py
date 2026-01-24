"""
Auto-generated PyOsmo model for website testing.
Base URL: http://127.0.0.1:8000/radio/
"""

import random
from typing import Optional

try:
    import requests
except ImportError:
    raise ImportError(
        "Model requires requests library. Install with: pip install requests"
    )

from pyosmo import Osmo
from pyosmo.decorators import step, guard


class WebsiteModel:
    """
    Model-based testing for http://127.0.0.1:8000/radio/
    """

    def __init__(self):
        """Initialize the model state."""
        self.base_url = "http://127.0.0.1:8000/radio/"
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

    @step
    @guard(lambda self: not self.logged_in)
    def submit_action(self):
        """Submit the submit action form."""
        data = {
            "csrfmiddlewaretoken": "HK8TvhajxGsMd6jiIGGihCLWyLUFHUecntoyitbhL6CBN7j0MDvHD7m4IHMbgLMa",
            "username": "testuser",
            "password": "testpassword123",
        }

        self.response = self.session.post(
            "http://127.0.0.1:8000/",
            data=data,
        )

        # Update login state on success
        if self.response.status_code == 200:
            self.logged_in = True
            self.current_user = data.get("username") or data.get("email")
        self.current_page = "http__1270018000_radio"
        print(f"Executed: submit_action")

    @step
    def submit_send_password(self):
        """Submit the submit send password form."""
        data = {
            "csrfmiddlewaretoken": "9vzl8L3Hrmai1snQ5U9WIEFyYkvnVHNtPeP0VX4FFMk7Btny9RYl49gG8gnTuylr",
            "email": "test@example.com",
        }

        self.response = self.session.post(
            "http://127.0.0.1:8000/send_password/",
            data=data,
        )

        self.current_page = "http__1270018000_send_password"
        print(f"Executed: submit_send_password")

    @step
    @guard(lambda self: not self.logged_in)
    def submit_login(self):
        """Submit the submit login form."""
        data = {
            "csrfmiddlewaretoken": "R5SiN04jB7GaJtA9UM2ocP088Ts8i2gNxO8XAc5hPxQZjuARYJRNykBgiPkERTOL",
            "username": "testuser",
            "password": "testpassword123",
        }

        self.response = self.session.post(
            "http://127.0.0.1:8000/login/",
            data=data,
        )

        # Update login state on success
        if self.response.status_code == 200:
            self.logged_in = True
            self.current_user = data.get("username") or data.get("email")
        self.current_page = "http__1270018000_login"
        print(f"Executed: submit_login")

    @step
    def navigate_to_http__1270018000_send_password(self):
        """Navigate to http__1270018000_send_password."""
        self.response = self.session.get("http://127.0.0.1:8000/send_password/")
        self.current_page = "http__1270018000_send_password"
        print(f"Navigated to: http__1270018000_send_password")

    @step
    def navigate_to_http__1270018000_static_files_tietosuojaseloste_srk_kesaseuraviestinta_22082025pdf(self):
        """Navigate to http__1270018000_static_files_tietosuojaseloste_srk_kesaseuraviestinta_22082025pdf."""
        self.response = self.session.get("http://127.0.0.1:8000/static/files/Tietosuojaseloste_SRK_Kesaseuraviestinta_22082025.pdf")
        self.current_page = "http__1270018000_static_files_tietosuojaseloste_srk_kesaseuraviestinta_22082025pdf"
        print(f"Navigated to: http__1270018000_static_files_tietosuojaseloste_srk_kesaseuraviestinta_22082025pdf")

    @step
    def navigate_to_http__1270018000_login(self):
        """Navigate to http__1270018000_login."""
        self.response = self.session.get("http://127.0.0.1:8000/login/")
        self.current_page = "http__1270018000_login"
        print(f"Navigated to: http__1270018000_login")



def main():
    """Run the model with PyOsmo."""
    model = WebsiteModel()

    osmo = (
        Osmo(model)
        .weighted_algorithm()
        .stop_after_steps(100)
        .run_tests(1)
    )

    print(f"Starting test generation for {model.base_url}")
    osmo.generate()

    # Print summary
    stats = osmo.history.statistics()
    print("\n" + "=" * 50)
    print("Test generation complete!")
    print(stats)


if __name__ == "__main__":
    main()