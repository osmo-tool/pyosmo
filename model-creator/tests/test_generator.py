"""
Tests for the model generator.
"""

import unittest
import ast
from model_creator.generator import ModelGenerator
from model_creator.crawler import Page, Form, FormField, Link


class TestModelGenerator(unittest.TestCase):
    """Tests for ModelGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_url = 'https://example.com'
        self.pages = {
            'https://example.com': Page(
                url='https://example.com',
                title='Home Page',
                forms=[],
                links=[Link(url='https://example.com/about', text='About', source_page='https://example.com')],
            ),
            'https://example.com/login': Page(
                url='https://example.com/login',
                title='Login',
                forms=[
                    Form(
                        action='https://example.com/auth',
                        method='POST',
                        fields=[
                            FormField(name='username', field_type='text', required=True),
                            FormField(name='password', field_type='password', required=True),
                        ],
                        page_url='https://example.com/login',
                    )
                ],
                links=[],
                has_login=True,
            ),
            'https://example.com/about': Page(
                url='https://example.com/about',
                title='About Us',
                forms=[],
                links=[Link(url='https://example.com', text='Home', source_page='https://example.com/about')],
            ),
        }
        self.generator = ModelGenerator(self.pages, self.base_url)

    def test_initialization(self):
        """Test generator initialization."""
        self.assertEqual(self.generator.base_url, self.base_url)
        self.assertEqual(len(self.generator.pages), 3)
        self.assertEqual(len(self.generator.actions), 0)

    def test_sanitize_name(self):
        """Test name sanitization."""
        self.assertEqual(self.generator.sanitize_name('Hello World'), 'hello_world')
        self.assertEqual(self.generator.sanitize_name('test-page'), 'test_page')
        self.assertEqual(self.generator.sanitize_name('123test'), 'test')
        self.assertEqual(self.generator.sanitize_name('test@#$page'), 'testpage')
        self.assertEqual(self.generator.sanitize_name(''), 'action')

    def test_get_page_name(self):
        """Test page name generation."""
        self.assertEqual(self.generator.get_page_name('https://example.com'), 'home')
        self.assertEqual(self.generator.get_page_name('https://example.com/about'), 'about')
        self.assertEqual(self.generator.get_page_name('https://example.com/user/profile'), 'user_profile')

    def test_is_login_form(self):
        """Test login form detection."""
        login_form = Form(
            action='/login',
            method='POST',
            fields=[
                FormField(name='username', field_type='text'),
                FormField(name='password', field_type='password'),
            ],
        )
        self.assertTrue(self.generator._is_login_form(login_form))

        # Not a login form (no password)
        contact_form = Form(
            action='/contact',
            method='POST',
            fields=[
                FormField(name='name', field_type='text'),
                FormField(name='email', field_type='email'),
            ],
        )
        self.assertFalse(self.generator._is_login_form(contact_form))

    def test_get_form_name(self):
        """Test form name generation."""
        login_form = Form(
            action='/login',
            method='POST',
            fields=[
                FormField(name='username', field_type='text'),
                FormField(name='password', field_type='password'),
            ],
        )
        login_page = self.pages['https://example.com/login']

        name = self.generator._get_form_name(login_form, login_page)
        self.assertEqual(name, 'login')

        # Search form
        search_form = Form(action='/search', method='GET', fields=[FormField(name='search', field_type='text')])
        search_page = Page(url='https://example.com', title='Home', forms=[search_form], links=[])

        name = self.generator._get_form_name(search_form, search_page)
        self.assertEqual(name, 'search')

    def test_get_default_value(self):
        """Test default value generation for form fields."""
        # Email field
        email_field = FormField(name='email', field_type='email')
        self.assertEqual(self.generator._get_default_value(email_field), '"test@example.com"')

        # Password field
        password_field = FormField(name='password', field_type='password')
        self.assertEqual(self.generator._get_default_value(password_field), '"testpassword123"')

        # Username field
        username_field = FormField(name='username', field_type='text')
        self.assertEqual(self.generator._get_default_value(username_field), '"testuser"')

        # Number field
        number_field = FormField(name='age', field_type='number')
        self.assertEqual(self.generator._get_default_value(number_field), '42')

        # Checkbox
        checkbox_field = FormField(name='agree', field_type='checkbox')
        self.assertEqual(self.generator._get_default_value(checkbox_field), 'True')

        # Select with options
        select_field = FormField(name='country', field_type='select', options=['US', 'UK'])
        self.assertEqual(self.generator._get_default_value(select_field), '"US"')

    def test_analyze_forms(self):
        """Test form analysis."""
        self.generator.analyze_forms()

        # Should find the login form
        self.assertGreater(len(self.generator.actions), 0)

        # Find login action
        login_actions = [a for a in self.generator.actions if a.get('is_login')]
        self.assertEqual(len(login_actions), 1)

        login_action = login_actions[0]
        self.assertEqual(login_action['name'], 'submit_login')
        self.assertTrue(login_action['is_login'])
        self.assertEqual(len(login_action['fields']), 2)

        # State variables should include logged_in
        self.assertIn('logged_in', self.generator.state_variables)
        self.assertIn('current_user', self.generator.state_variables)

    def test_analyze_links(self):
        """Test link analysis."""
        self.generator.analyze_links()

        # Should find navigation actions
        self.assertGreater(len(self.generator.actions), 0)

        # Check navigation actions
        nav_actions = [a for a in self.generator.actions if a['type'] == 'navigation']
        self.assertGreater(len(nav_actions), 0)

        # State variables should include current_page
        self.assertIn('current_page', self.generator.state_variables)

    def test_generate_model_class(self):
        """Test model class generation."""
        code = self.generator.generate_model_class('TestModel')

        # Should be valid Python code
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            self.fail(f'Generated code is not valid Python: {e}')

        # Check for class definition
        self.assertIn('class TestModel:', code)
        self.assertIn('def __init__(self):', code)
        self.assertIn('def before_test(self):', code)
        self.assertIn('def after_test(self):', code)
        self.assertIn('def after(self):', code)

        # Check for state variables
        self.assertIn('self.session', code)
        self.assertIn('self.response', code)

        # Check for imports
        self.assertIn('import requests', code)
        self.assertIn('import random', code)

    def test_generate_form_step(self):
        """Test form step generation."""
        action = {
            'type': 'form_submit',
            'name': 'submit_login',
            'form': Form(
                action='https://example.com/auth',
                method='POST',
                fields=[
                    FormField(name='username', field_type='text', required=True),
                    FormField(name='password', field_type='password', required=True),
                ],
            ),
            'page_url': 'https://example.com/login',
            'page_name': 'login',
            'is_login': True,
            'is_logout': False,
            'fields': [],
            'required_fields': [],
        }

        lines = self.generator._generate_form_step(action)
        code = '\n'.join(lines)

        # Check method definition
        self.assertIn('def step_submit_login(self):', code)
        self.assertIn('def guard_submit_login(self):', code)

        # Check form data preparation
        self.assertIn('data = {', code)
        self.assertIn('"username":', code)
        self.assertIn('"password":', code)

        # Check request
        self.assertIn('self.response = self.session.post(', code)

        # Check login state update
        self.assertIn('self.logged_in = True', code)

        # Check guard for login
        self.assertIn('return not self.logged_in', code)

    def test_generate_navigation_step(self):
        """Test navigation step generation."""
        action = {
            'type': 'navigation',
            'name': 'navigate_to_about',
            'target_url': 'https://example.com/about',
            'target_page': 'about',
            'link_text': 'About',
            'requires_auth': False,
        }

        lines = self.generator._generate_navigation_step(action)
        code = '\n'.join(lines)

        # Check method definition
        self.assertIn('def step_navigate_to_about(self):', code)
        self.assertIn('def guard_navigate_to_about(self):', code)

        # Check navigation
        self.assertIn('self.response = self.session.get(', code)
        self.assertIn('https://example.com/about', code)

        # Check guard
        self.assertIn('return True', code)

    def test_get_statistics(self):
        """Test statistics generation."""
        self.generator.analyze_forms()
        self.generator.analyze_links()

        stats = self.generator.get_statistics()

        self.assertIn('total_actions', stats)
        self.assertIn('form_actions', stats)
        self.assertIn('navigation_actions', stats)
        self.assertIn('state_variables', stats)
        self.assertIn('login_actions', stats)

        self.assertGreater(stats['total_actions'], 0)


if __name__ == '__main__':
    unittest.main()
