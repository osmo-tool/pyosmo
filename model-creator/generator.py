"""
Model generator - Creates PyOsmo models from crawled website data.
"""

import re
from pathlib import Path

from .crawler import Form, FormField, Page


class ModelGenerator:
    """
    Generates PyOsmo model code from crawled website data.
    """

    def __init__(self, pages: dict[str, Page], base_url: str):
        """
        Initialize the model generator.

        Args:
            pages: Dictionary of crawled pages
            base_url: Base URL of the website
        """
        self.pages = pages
        self.base_url = base_url
        self.actions: list[dict] = []
        self.state_variables: set[str] = set()

    def sanitize_name(self, text: str) -> str:
        """Convert text to a valid Python identifier."""
        # Remove or replace special characters
        text = re.sub(r'[^\w\s-]', '', text)
        # Replace spaces and hyphens with underscores
        text = re.sub(r'[-\s]+', '_', text)
        # Remove leading digits
        text = re.sub(r'^\d+', '', text)
        # Convert to lowercase
        text = text.lower().strip('_')
        # Ensure it's not empty
        if not text:
            text = 'action'
        return text

    def get_page_name(self, url: str) -> str:
        """Generate a readable name for a page."""
        path = url.replace(self.base_url, '').strip('/')
        if not path:
            return 'home'
        return self.sanitize_name(path.replace('/', '_'))

    def analyze_forms(self):
        """Analyze forms and generate form submission actions."""
        for page_url, page in self.pages.items():
            for _form_idx, form in enumerate(page.forms):
                # Determine action name based on form fields or page
                form_name = self._get_form_name(form, page)
                action_name = f'submit_{form_name}'

                # Check if it's a login form
                is_login = self._is_login_form(form)
                is_logout = form_name == 'logout'

                # Extract required fields
                required_fields = [f for f in form.fields if f.required]
                all_fields = form.fields

                action = {
                    'type': 'form_submit',
                    'name': action_name,
                    'form': form,
                    'page_url': page_url,
                    'page_name': self.get_page_name(page_url),
                    'is_login': is_login,
                    'is_logout': is_logout,
                    'fields': all_fields,
                    'required_fields': required_fields,
                }

                self.actions.append(action)

                # Track state variables
                if is_login:
                    self.state_variables.add('logged_in')
                    self.state_variables.add('current_user')
                if is_logout:
                    self.state_variables.add('logged_in')

    def _get_form_name(self, form: Form, page: Page) -> str:
        """Determine a meaningful name for a form."""
        # Check field names for hints
        field_names = [f.name.lower() for f in form.fields]

        if any('login' in name or 'signin' in name for name in field_names):
            return 'login'
        if any('register' in name or 'signup' in name for name in field_names):
            return 'register'
        if any('search' in name for name in field_names):
            return 'search'
        if any('contact' in name or 'message' in name for name in field_names):
            return 'contact'
        if any('comment' in name for name in field_names):
            return 'comment'

        # Use page name or action URL
        if 'login' in page.title.lower() or 'signin' in page.title.lower():
            return 'login'
        if 'register' in page.title.lower() or 'signup' in page.title.lower():
            return 'register'

        # Extract from action URL
        action_path = form.action.replace(self.base_url, '').strip('/')
        if action_path:
            return self.sanitize_name(action_path.split('/')[-1])

        return self.get_page_name(page.url)

    def _is_login_form(self, form: Form) -> bool:
        """Check if a form is a login form."""
        field_names = {f.name.lower() for f in form.fields}
        password_fields = [f for f in form.fields if f.field_type == 'password']

        # Has password field and username/email field
        has_password = len(password_fields) > 0
        has_user_field = any(name in field_names for name in ['username', 'email', 'user', 'login'])

        return has_password and has_user_field

    def analyze_links(self):
        """Analyze links and generate navigation actions."""
        # Group links by destination
        link_destinations: dict[str, list] = {}

        for page in self.pages.values():
            for link in page.links:
                if link.url not in link_destinations:
                    link_destinations[link.url] = []
                link_destinations[link.url].append({'text': link.text, 'source': link.source_page})

        # Create navigation actions for important links
        for dest_url, sources in link_destinations.items():
            # Skip if destination wasn't crawled
            if dest_url not in self.pages:
                continue

            dest_page = self.pages[dest_url]
            page_name = self.get_page_name(dest_url)

            # Use most common link text
            if sources:
                link_texts = [s['text'] for s in sources if s['text']]
                common_text = max(set(link_texts), key=link_texts.count) if link_texts else ''
            else:
                common_text = ''

            action_name = f'navigate_to_{page_name}'

            action = {
                'type': 'navigation',
                'name': action_name,
                'target_url': dest_url,
                'target_page': page_name,
                'link_text': common_text,
                'requires_auth': dest_page.requires_auth,
            }

            self.actions.append(action)

            # Track state
            self.state_variables.add('current_page')

    def generate_model_class(self, class_name: str = 'WebsiteModel') -> str:
        """
        Generate the complete model class code.

        Args:
            class_name: Name of the model class

        Returns:
            Python code as a string
        """
        # Analyze the crawled data
        self.analyze_forms()
        self.analyze_links()

        # Start building the code
        lines = []

        # Imports
        lines.extend(
            [
                '"""',
                'Auto-generated PyOsmo model for website testing.',
                f'Base URL: {self.base_url}',
                '"""',
                '',
                'import random',
                'from typing import Optional',
                '',
                'try:',
                '    import requests',
                'except ImportError:',
                '    raise ImportError(',
                '        "Model requires requests library. Install with: pip install requests"',
                '    )',
                '',
                '',
            ]
        )

        # Class definition
        lines.extend(
            [
                f'class {class_name}:',
                '    """',
                f'    Model-based testing for {self.base_url}',
                '    """',
                '',
                '    def __init__(self):',
                '        """Initialize the model state."""',
                f'        self.base_url = "{self.base_url}"',
                '        self.session = requests.Session()',
            ]
        )

        # Initialize state variables
        if 'logged_in' in self.state_variables:
            lines.append('        self.logged_in = False')
        if 'current_user' in self.state_variables:
            lines.append('        self.current_user: Optional[str] = None')
        if 'current_page' in self.state_variables:
            lines.append('        self.current_page = "home"')

        lines.extend(
            [
                '        self.response = None',
                '        self.last_error: Optional[str] = None',
                '',
            ]
        )

        # Add lifecycle methods
        lines.extend(
            [
                '    def before_test(self):',
                '        """Called before each test run."""',
                '        self.session = requests.Session()',
                '        self.logged_in = False' if 'logged_in' in self.state_variables else '',
                '        self.current_page = "home"' if 'current_page' in self.state_variables else '',
                '        print("Starting new test run")',
                '',
                '    def after_test(self):',
                '        """Called after each test run."""',
                '        self.session.close()',
                '        print("Test run completed")',
                '',
                '    def after(self):',
                '        """Called after each step - verification point."""',
                '        if self.response is not None:',
                '            # Verify response is valid',
                '            assert self.response.status_code < 500, \\',
                '                f"Server error: {self.response.status_code}"',
                '',
            ]
        )

        # Generate step methods
        for action in self.actions:
            lines.extend(self._generate_step_method(action))
            lines.append('')

        return '\n'.join(line for line in lines if line is not None)

    def _generate_step_method(self, action: dict) -> list[str]:
        """Generate a step method for an action."""
        lines = []

        if action['type'] == 'form_submit':
            lines.extend(self._generate_form_step(action))
        elif action['type'] == 'navigation':
            lines.extend(self._generate_navigation_step(action))

        return lines

    def _generate_form_step(self, action: dict) -> list[str]:
        """Generate a form submission step."""
        lines = []
        method_name = action['name']
        form = action['form']

        # Method signature
        lines.append(f'    def step_{method_name}(self):')
        lines.append(f'        """Submit the {method_name.replace("_", " ")} form."""')

        # Prepare form data
        lines.append('        data = {')
        for field in form.fields:
            default = self._get_default_value(field)
            lines.append(f'            "{field.name}": {default},')
        lines.append('        }')
        lines.append('')

        # Make request
        method = form.method.lower()
        lines.append(f'        self.response = self.session.{method}(')
        lines.append(f'            "{form.action}",')
        if method == 'post':
            lines.append('            data=data,')
        else:
            lines.append('            params=data,')
        lines.append('        )')
        lines.append('')

        # Update state for login/logout
        if action['is_login']:
            lines.append('        # Update login state on success')
            lines.append('        if self.response.status_code == 200:')
            lines.append('            self.logged_in = True')
            lines.append('            self.current_user = data.get("username") or data.get("email")')
        elif action['is_logout']:
            lines.append('        # Update logout state')
            lines.append('        self.logged_in = False')
            lines.append('        self.current_user = None')

        if 'current_page' in self.state_variables:
            lines.append(f'        self.current_page = "{action["page_name"]}"')

        lines.append(f'        print(f"Executed: {method_name}")')

        # Guard method
        lines.append('')
        lines.append(f'    def guard_{method_name}(self):')
        lines.append(f'        """Guard for {method_name}."""')

        if action['is_login']:
            lines.append('        # Can only login when not logged in')
            lines.append('        return not self.logged_in')
        elif action['is_logout']:
            lines.append('        # Can only logout when logged in')
            lines.append('        return self.logged_in')
        else:
            # Check if requires login
            page = self.pages.get(action['page_url'])
            if page and page.requires_auth:
                lines.append('        return self.logged_in')
            else:
                lines.append('        return True')

        return lines

    def _generate_navigation_step(self, action: dict) -> list[str]:
        """Generate a navigation step."""
        lines = []
        method_name = action['name']

        lines.append(f'    def step_{method_name}(self):')
        lines.append(f'        """Navigate to {action["target_page"]}."""')
        lines.append(f'        self.response = self.session.get("{action["target_url"]}")')

        if 'current_page' in self.state_variables:
            lines.append(f'        self.current_page = "{action["target_page"]}"')

        lines.append(f'        print(f"Navigated to: {action["target_page"]}")')

        # Guard
        lines.append('')
        lines.append(f'    def guard_{method_name}(self):')
        lines.append(f'        """Guard for {method_name}."""')

        if action['requires_auth']:
            lines.append('        return self.logged_in')
        else:
            lines.append('        return True')

        return lines

    def _get_default_value(self, field: FormField) -> str:
        """Get a default value for a form field."""
        if field.default_value:
            return f'"{field.default_value}"'

        field_name_lower = field.name.lower()

        # Type-specific defaults
        if field.field_type == 'email' or 'email' in field_name_lower:
            return '"test@example.com"'
        if field.field_type == 'password' or 'password' in field_name_lower:
            return '"testpassword123"'
        if 'username' in field_name_lower or 'user' in field_name_lower:
            return '"testuser"'
        if 'name' in field_name_lower:
            return '"Test User"'
        if 'phone' in field_name_lower:
            return '"555-1234"'
        if field.field_type == 'number':
            return '42'
        if field.field_type == 'checkbox':
            return 'True'
        if field.field_type == 'radio' and field.options or field.field_type == 'select' and field.options:
            return f'"{field.options[0]}"'
        return f'"test_{field.name}"'

    def save_model(self, output_path: Path, class_name: str = 'WebsiteModel'):
        """
        Generate and save the model to a file.

        Args:
            output_path: Path to save the model file
            class_name: Name of the model class
        """
        code = self.generate_model_class(class_name)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(code)

        print(f'Model saved to: {output_path}')

    def get_statistics(self) -> dict:
        """Get statistics about the generated model."""
        return {
            'total_actions': len(self.actions),
            'form_actions': len([a for a in self.actions if a['type'] == 'form_submit']),
            'navigation_actions': len([a for a in self.actions if a['type'] == 'navigation']),
            'state_variables': len(self.state_variables),
            'login_actions': len([a for a in self.actions if a.get('is_login')]),
            'logout_actions': len([a for a in self.actions if a.get('is_logout')]),
        }