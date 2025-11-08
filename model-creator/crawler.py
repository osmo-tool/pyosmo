"""
Web crawler for discovering website structure and interactions.
"""

import re
import time
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
from collections import defaultdict

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    raise ImportError(
        'Website crawler requires additional dependencies. Install with:\npip install requests beautifulsoup4'
    )


@dataclass
class FormField:
    """Represents a form field."""

    name: str
    field_type: str
    required: bool = False
    options: List[str] = field(default_factory=list)
    default_value: Optional[str] = None


@dataclass
class Form:
    """Represents a form on a webpage."""

    action: str
    method: str = 'GET'
    fields: List[FormField] = field(default_factory=list)
    page_url: str = ''


@dataclass
class Link:
    """Represents a link on a webpage."""

    url: str
    text: str
    source_page: str


@dataclass
class Page:
    """Represents a discovered webpage."""

    url: str
    title: str
    forms: List[Form] = field(default_factory=list)
    links: List[Link] = field(default_factory=list)
    has_login: bool = False
    has_logout: bool = False
    requires_auth: bool = False
    status_code: int = 200
    error_messages: List[str] = field(default_factory=list)
    success_messages: List[str] = field(default_factory=list)


class WebsiteCrawler:
    """
    Crawls a website to discover its structure and behavior.
    """

    def __init__(
        self,
        base_url: str,
        max_pages: int = 50,
        delay: float = 0.5,
        follow_external: bool = False,
        auth: Optional[Tuple[str, str]] = None,
    ):
        """
        Initialize the crawler.

        Args:
            base_url: The base URL to start crawling from
            max_pages: Maximum number of pages to crawl
            delay: Delay between requests in seconds
            follow_external: Whether to follow external links
            auth: Optional tuple of (username, password) for basic auth
        """
        self.base_url = base_url.rstrip('/')
        self.max_pages = max_pages
        self.delay = delay
        self.follow_external = follow_external
        self.auth = auth

        self.visited_urls: Set[str] = set()
        self.pages: Dict[str, Page] = {}
        self.session = requests.Session()

        if auth:
            self.session.auth = auth

        # Patterns for detecting special elements
        self.login_patterns = [r'login', r'signin', r'log.in', r'sign.in', r'authenticate', r'auth']
        self.logout_patterns = [r'logout', r'signout', r'log.out', r'sign.out']
        self.error_patterns = [r'error', r'invalid', r'failed', r'incorrect', r'wrong', r'denied', r'forbidden']
        self.success_patterns = [r'success', r'successful', r'welcome', r'thank you', r'confirmed', r'completed']

    def normalize_url(self, url: str, base: Optional[str] = None) -> str:
        """Normalize a URL by joining with base and removing fragments."""
        if base:
            url = urljoin(base, url)
        # Remove fragment
        parsed = urlparse(url)
        return f'{parsed.scheme}://{parsed.netloc}{parsed.path}'

    def is_same_domain(self, url: str) -> bool:
        """Check if URL belongs to the same domain as base_url."""
        base_domain = urlparse(self.base_url).netloc
        url_domain = urlparse(url).netloc
        return base_domain == url_domain

    def extract_forms(self, soup: BeautifulSoup, page_url: str) -> List[Form]:
        """Extract all forms from a page."""
        forms = []

        for form_elem in soup.find_all('form'):
            action = form_elem.get('action', '')
            action = self.normalize_url(action, page_url)
            method = form_elem.get('method', 'GET').upper()

            fields = []
            for input_elem in form_elem.find_all(['input', 'select', 'textarea']):
                name = input_elem.get('name')
                if not name:
                    continue

                field_type = input_elem.get('type', 'text').lower()
                required = input_elem.get('required') is not None
                default_value = input_elem.get('value')

                options = []
                if input_elem.name == 'select':
                    options = [opt.get('value', opt.text) for opt in input_elem.find_all('option')]

                fields.append(
                    FormField(
                        name=name,
                        field_type=field_type,
                        required=required,
                        options=options,
                        default_value=default_value,
                    )
                )

            forms.append(Form(action=action, method=method, fields=fields, page_url=page_url))

        return forms

    def extract_links(self, soup: BeautifulSoup, page_url: str) -> List[Link]:
        """Extract all links from a page."""
        links = []

        for a_elem in soup.find_all('a', href=True):
            href = a_elem['href']
            text = a_elem.get_text(strip=True)

            # Skip javascript links, anchors, etc.
            if href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                continue

            url = self.normalize_url(href, page_url)

            # Skip if external and we're not following external links
            if not self.follow_external and not self.is_same_domain(url):
                continue

            links.append(Link(url=url, text=text, source_page=page_url))

        return links

    def detect_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any of the given patterns."""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in patterns)

    def analyze_page(self, url: str, html: str) -> Page:
        """Analyze a page's HTML and extract information."""
        soup = BeautifulSoup(html, 'html.parser')

        # Extract title
        title = soup.title.string if soup.title else url

        # Extract forms and links
        forms = self.extract_forms(soup, url)
        links = self.extract_links(soup, url)

        # Detect login/logout
        page_text = soup.get_text()
        has_login = self.detect_patterns(page_text, self.login_patterns)
        has_logout = self.detect_patterns(page_text, self.logout_patterns)

        # Check for login forms
        if not has_login:
            for form in forms:
                form_fields = {f.name.lower() for f in form.fields}
                if any(field in form_fields for field in ['username', 'password', 'email', 'login']):
                    has_login = True
                    break

        # Detect error/success messages
        error_messages = []
        success_messages = []

        for elem in soup.find_all(['div', 'p', 'span'], class_=True):
            classes = ' '.join(elem.get('class', []))
            text = elem.get_text(strip=True)

            if self.detect_patterns(classes + ' ' + text, self.error_patterns):
                error_messages.append(text)
            elif self.detect_patterns(classes + ' ' + text, self.success_patterns):
                success_messages.append(text)

        return Page(
            url=url,
            title=title,
            forms=forms,
            links=links,
            has_login=has_login,
            has_logout=has_logout,
            error_messages=error_messages,
            success_messages=success_messages,
        )

    def crawl_page(self, url: str) -> Optional[Page]:
        """Crawl a single page."""
        if url in self.visited_urls:
            return None

        if len(self.visited_urls) >= self.max_pages:
            return None

        try:
            print(f'Crawling: {url}')
            response = self.session.get(url, timeout=10)
            self.visited_urls.add(url)

            # Check if authentication is required
            requires_auth = response.status_code == 401

            page = self.analyze_page(url, response.text)
            page.status_code = response.status_code
            page.requires_auth = requires_auth

            self.pages[url] = page

            # Delay before next request
            time.sleep(self.delay)

            return page

        except Exception as e:
            print(f'Error crawling {url}: {e}')
            self.visited_urls.add(url)
            return None

    def crawl(self, start_url: Optional[str] = None) -> Dict[str, Page]:
        """
        Crawl the website starting from the given URL.

        Args:
            start_url: URL to start from (defaults to base_url)

        Returns:
            Dictionary of URL to Page objects
        """
        if start_url is None:
            start_url = self.base_url

        to_visit = [start_url]

        while to_visit and len(self.visited_urls) < self.max_pages:
            url = to_visit.pop(0)

            page = self.crawl_page(url)
            if not page:
                continue

            # Add discovered links to the queue
            for link in page.links:
                if link.url not in self.visited_urls and link.url not in to_visit:
                    to_visit.append(link.url)

        print(f'\nCrawling complete. Discovered {len(self.pages)} pages.')
        return self.pages

    def get_statistics(self) -> Dict:
        """Get statistics about the crawled website."""
        total_forms = sum(len(page.forms) for page in self.pages.values())
        total_links = sum(len(page.links) for page in self.pages.values())
        pages_with_forms = sum(1 for page in self.pages.values() if page.forms)
        pages_with_login = sum(1 for page in self.pages.values() if page.has_login)
        pages_with_logout = sum(1 for page in self.pages.values() if page.has_logout)

        return {
            'total_pages': len(self.pages),
            'total_forms': total_forms,
            'total_links': total_links,
            'pages_with_forms': pages_with_forms,
            'pages_with_login': pages_with_login,
            'pages_with_logout': pages_with_logout,
        }
