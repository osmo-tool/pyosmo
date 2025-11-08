# PyOsmo Model Creator

Autonomous website model generation tool for PyOsmo. This tool automatically crawls websites and generates PyOsmo models for model-based testing.

## Features

- **Autonomous Web Crawling**: Automatically explores websites and discovers pages, forms, and links
- **Smart Model Generation**: Analyzes website structure and generates PyOsmo models with:
  - State variables (logged in status, current page, etc.)
  - Step methods for form submissions and navigation
  - Guard methods for valid state transitions
  - Lifecycle hooks for setup and verification
- **Model Updates**: Can update existing models with newly discovered actions
- **Authentication Support**: Handles basic authentication for protected sites
- **Customizable Crawling**: Configure max pages, crawl delay, and more

## Installation

### Dependencies

The model creator requires additional dependencies:

```bash
pip install requests beautifulsoup4
```

## Usage

### Creating a New Model

Generate a new PyOsmo model from a website:

```bash
python -m model-creator create https://example.com -o models/example_model.py
```

**Options:**

- `-o, --output PATH`: Output path for the generated model (required)
- `-c, --class-name NAME`: Name of the model class (default: WebsiteModel)
- `-m, --max-pages N`: Maximum number of pages to crawl (default: 50)
- `-d, --delay SECONDS`: Delay between requests (default: 0.5)
- `--follow-external`: Follow external links
- `--username USER`: Username for basic authentication
- `--password PASS`: Password for basic authentication
- `--save-crawl`: Save crawl data to JSON file

**Example with authentication:**

```bash
python -m model-creator create https://example.com \
    -o models/example_model.py \
    --username testuser \
    --password testpass \
    --max-pages 100
```

### Updating an Existing Model

Update an existing model with newly discovered pages and actions:

```bash
python -m model-creator update models/example_model.py https://example.com
```

**Options:**

- `-m, --max-pages N`: Maximum number of pages to crawl (default: 50)
- `-d, --delay SECONDS`: Delay between requests (default: 0.5)
- `-y, --yes`: Skip confirmation prompt
- `--no-backup`: Don't create backup of existing model
- `--username USER`: Username for basic authentication
- `--password PASS`: Password for basic authentication

**Example:**

```bash
python -m model-creator update models/example_model.py https://example.com \
    --max-pages 50 \
    --yes
```

## Generated Model Structure

The generated models follow PyOsmo conventions and include:

### State Variables

```python
def __init__(self):
    self.base_url = "https://example.com"
    self.session = requests.Session()
    self.logged_in = False           # Authentication state
    self.current_user = None          # Current user info
    self.current_page = "home"        # Current page
    self.response = None              # Last HTTP response
    self.last_error = None            # Last error message
```

### Lifecycle Methods

```python
def before_test(self):
    """Called before each test run."""
    # Reset state and session

def after_test(self):
    """Called after each test run."""
    # Cleanup

def after(self):
    """Called after each step - verification point."""
    # Verify response is valid
    assert self.response.status_code < 500
```

### Step Methods (Actions)

Form submission:
```python
def step_submit_login(self):
    """Submit the login form."""
    data = {
        "username": "testuser",
        "password": "testpassword123",
    }
    self.response = self.session.post(
        "https://example.com/auth",
        data=data,
    )
    if self.response.status_code == 200:
        self.logged_in = True
        self.current_user = data.get("username")
    print("Executed: submit_login")
```

Navigation:
```python
def step_navigate_to_about(self):
    """Navigate to about page."""
    self.response = self.session.get("https://example.com/about")
    self.current_page = "about"
    print("Navigated to: about")
```

### Guard Methods (Preconditions)

```python
def guard_submit_login(self):
    """Guard for login - can only login when not logged in."""
    return not self.logged_in

def guard_submit_logout(self):
    """Guard for logout - can only logout when logged in."""
    return self.logged_in
```

## Running Generated Models

Once you have a generated model, you can run it with PyOsmo:

```bash
# Run model exploration
python -m osmo.explorer -m models/example_model.py:WebsiteModel

# Run with specific seed for reproducibility
python -m osmo.explorer -m models/example_model.py:WebsiteModel --seed 42

# Run with step limit
python -m osmo.explorer -m models/example_model.py:WebsiteModel --steps 100
```

## Architecture

### Components

1. **WebsiteCrawler** (`crawler.py`):
   - Crawls websites using requests and BeautifulSoup
   - Discovers pages, forms, links, and interactions
   - Detects login/logout forms, error messages, and success messages
   - Respects robots.txt and rate limiting

2. **ModelGenerator** (`generator.py`):
   - Analyzes crawled data to identify actions
   - Generates PyOsmo model code with steps, guards, and state
   - Creates meaningful action names and default values
   - Handles authentication flows

3. **ModelUpdater** (`updater.py`):
   - Parses existing model files using AST
   - Identifies new actions from fresh crawls
   - Merges new methods into existing models
   - Preserves custom code and modifications

4. **CLI** (`cli.py`):
   - Command-line interface for create and update operations
   - Progress reporting and statistics
   - Interactive confirmation for updates

### Data Flow

```
Website URL
    ↓
WebsiteCrawler (crawls and discovers)
    ↓
Page objects (forms, links, metadata)
    ↓
ModelGenerator (analyzes and generates)
    ↓
PyOsmo Model Code
    ↓
ModelUpdater (optional - for updates)
    ↓
Updated Model Code
```

## Examples

### Example 1: E-commerce Site

```bash
python -m model-creator create https://shop.example.com \
    -o models/shop_model.py \
    --max-pages 100 \
    --save-crawl
```

Generated model will include:
- Login/logout actions
- Product browsing actions
- Cart management actions
- Checkout flow actions

### Example 2: Blog with Authentication

```bash
python -m model-creator create https://blog.example.com \
    -o models/blog_model.py \
    --username admin \
    --password secret123 \
    --max-pages 50
```

Generated model will include:
- Login/logout for admin
- Post creation/editing actions
- Comment submission actions
- Navigation between pages

### Example 3: Updating After Site Changes

```bash
# Initial model creation
python -m model-creator create https://example.com -o models/example.py

# ... time passes, site changes ...

# Update the model with new discoveries
python -m model-creator update models/example.py https://example.com --yes
```

## Customization

### Extending Generated Models

Generated models can be customized after creation:

1. **Add custom verification logic** in the `after()` method
2. **Customize default values** in form submission steps
3. **Add weights** to control action frequency:
   ```python
   def weight_submit_login(self):
       return 5  # Higher weight = more frequent
   ```
4. **Add invariants** for state checking
5. **Customize guards** for complex preconditions

### Configuration

You can modify crawler behavior by editing the generator code or using CLI options:

- `delay`: Time between requests (be respectful!)
- `max_pages`: Limit crawl depth
- `follow_external`: Whether to follow external links
- Pattern matching for login/logout/errors in `crawler.py`

## Limitations

- Only supports form-based interactions (no JavaScript rendering)
- Cannot handle CAPTCHA or complex authentication flows
- Generated models may need manual refinement for complex sites
- Default values are generic and may need customization
- Does not execute JavaScript (consider using Selenium for JS-heavy sites)

## Best Practices

1. **Start small**: Begin with `--max-pages 20` to test
2. **Respect rate limits**: Use `--delay` appropriately
3. **Review generated code**: Always review and test generated models
4. **Customize as needed**: Add custom logic for your specific needs
5. **Use authentication**: Crawl protected areas with `--username` and `--password`
6. **Keep backups**: Updates create backups by default
7. **Version control**: Commit models to git for change tracking

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest model-creator/tests/

# Run specific test file
python -m pytest model-creator/tests/test_crawler.py

# Run with coverage
python -m pytest model-creator/tests/ --cov=model-creator
```

## Troubleshooting

### "No pages were crawled"

- Check the URL is accessible
- Try increasing `--max-pages`
- Check for authentication requirements
- Verify network connectivity

### "Generated model has no actions"

- Site may be JavaScript-heavy (not supported)
- Try crawling more pages with `--max-pages`
- Check if pages have forms and links

### "Import errors when running model"

- Install dependencies: `pip install requests`
- Ensure PyOsmo is installed: `pip install osmo`

## Contributing

Contributions are welcome! Areas for improvement:

- JavaScript rendering support (Selenium/Playwright integration)
- AJAX request detection
- API endpoint discovery
- Smarter form field analysis
- Better error handling and recovery
- Enhanced pattern matching for actions

## License

This tool is part of the PyOsmo project and follows the same license.

## See Also

- [PyOsmo Documentation](../README.md)
- [Model-Based Testing Guide](../docs/model-based-testing.md)
- [PyOsmo Examples](../examples/)
