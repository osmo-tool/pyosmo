# Quick Start Guide

Get started with PyOsmo Model Creator in 5 minutes!

## Installation

```bash
# Navigate to the model-creator directory
cd model-creator

# Install dependencies
pip install -r requirements.txt
```

## Basic Usage

### 1. Create Your First Model

```bash
python -m model-creator create https://httpbin.org -o my_first_model.py --max-pages 10
```

This will:
- Crawl httpbin.org (a great test site)
- Generate a PyOsmo model
- Save it to `my_first_model.py`

### 2. Review the Generated Model

Open `my_first_model.py` and examine:
- State variables (current_page, etc.)
- Step methods (actions the model can take)
- Guard methods (preconditions for actions)

### 3. Run the Model with PyOsmo

```bash
# Run model exploration with PyOsmo
python -m osmo.explorer -m my_first_model.py:WebsiteModel --steps 50
```

### 4. Update the Model (Optional)

If the website changes:

```bash
python -m model-creator update my_first_model.py https://httpbin.org --yes
```

## Real-World Example

Let's create a model for a demo e-commerce site:

```bash
# Create model with more pages
python -m model-creator create https://demo.opencart.com \
    -o models/opencart_model.py \
    --max-pages 50 \
    --delay 1.0 \
    --class-name OpenCartModel \
    --save-crawl

# This will:
# 1. Crawl up to 50 pages
# 2. Wait 1 second between requests (be polite!)
# 3. Generate OpenCartModel class
# 4. Save crawl data to opencart_model.crawl.json
```

## Tips for Success

1. **Start Small**: Begin with `--max-pages 20` to test
2. **Be Polite**: Use `--delay 1.0` or higher for production sites
3. **Review Code**: Always review generated models before running
4. **Customize**: Add custom weights, guards, and verification logic

## Common Patterns

### Testing a Login Flow

```bash
python -m model-creator create https://example.com/login \
    -o models/login_test.py \
    --username testuser \
    --password testpass
```

### Updating After Site Changes

```bash
# Original model
python -m model-creator create https://example.com -o models/site.py

# ... site changes ...

# Update model
python -m model-creator update models/site.py https://example.com
```

### Crawling Internal Sites

```bash
python -m model-creator create http://localhost:8080 \
    -o models/local_app.py \
    --max-pages 100 \
    --delay 0.1
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [examples/](examples/) for sample generated models
- Customize generated models for your specific needs
- Add weights to control action frequency
- Add custom verification in the `after()` method

## Troubleshooting

**No pages crawled?**
- Check the URL is accessible
- Verify no authentication is required
- Try increasing `--max-pages`

**Model has no actions?**
- Site may be JavaScript-heavy (not supported)
- Try crawling from different start URLs
- Check if site has forms and links

**Import errors?**
```bash
pip install requests beautifulsoup4
```

## Getting Help

- Check the [README.md](README.md) for full documentation
- Review example models in [examples/](examples/)
- Check test files for usage patterns
