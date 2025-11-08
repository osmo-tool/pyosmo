"""
Tests for the website crawler.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from model_creator.crawler import (
    WebsiteCrawler,
    Page,
    Form,
    FormField,
    Link
)


class TestWebsiteCrawler(unittest.TestCase):
    """Tests for WebsiteCrawler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_url = "https://example.com"
        self.crawler = WebsiteCrawler(self.base_url, max_pages=10)

    def test_initialization(self):
        """Test crawler initialization."""
        self.assertEqual(self.crawler.base_url, self.base_url)
        self.assertEqual(self.crawler.max_pages, 10)
        self.assertEqual(len(self.crawler.visited_urls), 0)
        self.assertEqual(len(self.crawler.pages), 0)

    def test_normalize_url(self):
        """Test URL normalization."""
        # Absolute URL
        url = self.crawler.normalize_url("https://example.com/page#section")
        self.assertEqual(url, "https://example.com/page")

        # Relative URL
        url = self.crawler.normalize_url("/about", self.base_url)
        self.assertEqual(url, "https://example.com/about")

        # Remove fragment
        url = self.crawler.normalize_url("https://example.com/page?q=1#top")
        self.assertEqual(url, "https://example.com/page")

    def test_is_same_domain(self):
        """Test domain checking."""
        self.assertTrue(self.crawler.is_same_domain("https://example.com/page"))
        self.assertTrue(self.crawler.is_same_domain("https://example.com"))
        self.assertFalse(self.crawler.is_same_domain("https://other.com"))

    def test_extract_forms(self):
        """Test form extraction from HTML."""
        html = """
        <html>
            <body>
                <form action="/login" method="POST">
                    <input type="text" name="username" required>
                    <input type="password" name="password" required>
                    <input type="submit" value="Login">
                </form>
                <form action="/search" method="GET">
                    <input type="text" name="q">
                    <select name="category">
                        <option value="all">All</option>
                        <option value="docs">Docs</option>
                    </select>
                </form>
            </body>
        </html>
        """

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        forms = self.crawler.extract_forms(soup, self.base_url)

        self.assertEqual(len(forms), 2)

        # Check first form (login)
        login_form = forms[0]
        self.assertEqual(login_form.action, "https://example.com/login")
        self.assertEqual(login_form.method, "POST")
        self.assertEqual(len(login_form.fields), 2)
        self.assertEqual(login_form.fields[0].name, "username")
        self.assertTrue(login_form.fields[0].required)
        self.assertEqual(login_form.fields[1].name, "password")
        self.assertEqual(login_form.fields[1].field_type, "password")

        # Check second form (search)
        search_form = forms[1]
        self.assertEqual(search_form.action, "https://example.com/search")
        self.assertEqual(search_form.method, "GET")
        self.assertEqual(len(search_form.fields), 2)
        self.assertEqual(search_form.fields[1].name, "category")
        self.assertEqual(len(search_form.fields[1].options), 2)

    def test_extract_links(self):
        """Test link extraction from HTML."""
        html = """
        <html>
            <body>
                <a href="/about">About</a>
                <a href="https://example.com/contact">Contact</a>
                <a href="https://external.com">External</a>
                <a href="javascript:void(0)">JS Link</a>
                <a href="mailto:test@example.com">Email</a>
                <a href="#section">Anchor</a>
            </body>
        </html>
        """

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        links = self.crawler.extract_links(soup, self.base_url)

        # Should extract only valid internal links (3: about, contact)
        # External link should be excluded
        self.assertEqual(len(links), 2)
        self.assertEqual(links[0].url, "https://example.com/about")
        self.assertEqual(links[0].text, "About")
        self.assertEqual(links[1].url, "https://example.com/contact")

    def test_detect_patterns(self):
        """Test pattern detection."""
        # Login patterns
        self.assertTrue(self.crawler.detect_patterns(
            "Please login to continue",
            self.crawler.login_patterns
        ))
        self.assertTrue(self.crawler.detect_patterns(
            "Sign in here",
            self.crawler.login_patterns
        ))

        # Logout patterns
        self.assertTrue(self.crawler.detect_patterns(
            "Logout",
            self.crawler.logout_patterns
        ))

        # Error patterns
        self.assertTrue(self.crawler.detect_patterns(
            "Error: Invalid credentials",
            self.crawler.error_patterns
        ))

    def test_analyze_page(self):
        """Test page analysis."""
        html = """
        <html>
            <head><title>Login Page</title></head>
            <body>
                <h1>Please login</h1>
                <form action="/login" method="POST">
                    <input type="text" name="username">
                    <input type="password" name="password">
                </form>
                <a href="/register">Register</a>
                <div class="error">Invalid username or password</div>
            </body>
        </html>
        """

        page = self.crawler.analyze_page(self.base_url, html)

        self.assertEqual(page.url, self.base_url)
        self.assertEqual(page.title, "Login Page")
        self.assertEqual(len(page.forms), 1)
        self.assertTrue(page.has_login)
        self.assertFalse(page.has_logout)
        self.assertEqual(len(page.error_messages), 1)

    @patch('model_creator.crawler.requests.Session')
    def test_crawl_page(self, mock_session_class):
        """Test crawling a single page."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <head><title>Test Page</title></head>
            <body><a href="/page2">Page 2</a></body>
        </html>
        """

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        # Create new crawler with mocked session
        crawler = WebsiteCrawler(self.base_url, max_pages=5, delay=0)
        crawler.session = mock_session

        page = crawler.crawl_page(self.base_url)

        self.assertIsNotNone(page)
        self.assertEqual(page.url, self.base_url)
        self.assertEqual(page.title, "Test Page")
        self.assertIn(self.base_url, crawler.visited_urls)

    def test_get_statistics(self):
        """Test statistics gathering."""
        # Add some mock pages
        self.crawler.pages = {
            "https://example.com": Page(
                url="https://example.com",
                title="Home",
                forms=[Form(action="/login", method="POST")],
                links=[Link(url="https://example.com/about", text="About", source_page="https://example.com")],
                has_login=True,
            ),
            "https://example.com/about": Page(
                url="https://example.com/about",
                title="About",
                forms=[],
                links=[Link(url="https://example.com", text="Home", source_page="https://example.com/about")],
            ),
        }

        stats = self.crawler.get_statistics()

        self.assertEqual(stats["total_pages"], 2)
        self.assertEqual(stats["total_forms"], 1)
        self.assertEqual(stats["total_links"], 2)
        self.assertEqual(stats["pages_with_forms"], 1)
        self.assertEqual(stats["pages_with_login"], 1)
        self.assertEqual(stats["pages_with_logout"], 0)


class TestFormField(unittest.TestCase):
    """Tests for FormField dataclass."""

    def test_creation(self):
        """Test FormField creation."""
        field = FormField(
            name="username",
            field_type="text",
            required=True,
            options=[],
            default_value="test"
        )

        self.assertEqual(field.name, "username")
        self.assertEqual(field.field_type, "text")
        self.assertTrue(field.required)
        self.assertEqual(field.default_value, "test")


if __name__ == "__main__":
    unittest.main()
