# PyOsmo Reporting API

The Reporting API provides a simple and powerful way to export test execution results in various formats. Whether you need interactive HTML reports for stakeholders, JSON data for analysis, or JUnit XML for CI/CD integration, PyOsmo has you covered.

## Quick Start

```python
from pyosmo import Osmo
from pyosmo.reporting import Format

# Run your tests
osmo = Osmo(model)
osmo.run()

# Generate a single report
osmo.save_report("report.html", format=Format.HTML)

# Generate multiple reports at once
osmo.save_reports("reports/test_run", formats=[Format.HTML, Format.JSON, Format.JUNIT])
```

## Supported Formats

PyOsmo supports five report formats:

| Format | Extension | Best For |
|--------|-----------|----------|
| **HTML** | `.html` | Interactive reports with charts and visualizations |
| **JSON** | `.json` | Programmatic access and data analysis |
| **JUnit XML** | `.xml` | CI/CD integration (Jenkins, GitLab, GitHub Actions) |
| **Markdown** | `.md` | Documentation and version control |
| **CSV** | `.csv` | Spreadsheet analysis and data processing |

## Basic Usage

### Single Report

Save a report in a specific format:

```python
from pyosmo import Osmo
from pyosmo.reporting import Format

osmo = Osmo(model)
osmo.run()

# HTML report with interactive charts
osmo.save_report("report.html", format=Format.HTML)

# JSON report for data analysis
osmo.save_report("results.json", format=Format.JSON)

# JUnit XML for CI/CD
osmo.save_report("junit-results.xml", format=Format.JUNIT)

# Markdown report for documentation
osmo.save_report("report.md", format=Format.MARKDOWN)

# CSV report for spreadsheets
osmo.save_report("data.csv", format=Format.CSV)
```

### Multiple Reports

Generate multiple formats at once:

```python
from pyosmo import Osmo
from pyosmo.reporting import Format

osmo = Osmo(model)
osmo.run()

# Generate all formats (default)
osmo.save_reports("reports/test_run")
# Creates: test_run.html, test_run.json, test_run.xml, test_run.md, test_run.csv

# Generate specific formats only
osmo.save_reports(
    "reports/test_run",
    formats=[Format.HTML, Format.JSON, Format.JUNIT]
)
# Creates: test_run.html, test_run.json, test_run.xml
```

## Advanced Configuration

Customize reports using `ReportConfig`:

```python
from pyosmo import Osmo
from pyosmo.reporting import Format, ReportConfig

osmo = Osmo(model)
osmo.run()

# Configure the report
config = ReportConfig(
    title="E-Commerce Test Suite",
    include_charts=True,
    include_timeline=True,
    include_statistics=True,
    theme="dark"  # or "light"
)

# Generate with custom configuration
osmo.save_report("report.html", format=Format.HTML, config=config)
```

### Report Configuration Options

```python
@dataclass
class ReportConfig:
    title: str = "PyOsmo Test Report"
    include_charts: bool = True          # Show visualizations (HTML only)
    include_timeline: bool = True        # Show test case timeline
    include_statistics: bool = True      # Show detailed statistics
    theme: str = "light"                 # "light" or "dark" (HTML only)
    custom_css: Optional[str] = None     # Path to custom CSS (HTML only)
```

## Report Formats in Detail

### HTML Report

The HTML format provides an interactive, visual report with:
- Summary cards showing key metrics
- Interactive charts (step frequency, coverage timeline, execution times)
- Detailed test case table
- Step statistics with execution times
- Dark/light theme support

**Features:**
- 📊 Interactive charts using Chart.js
- 🎨 Beautiful, responsive design
- 🌓 Dark and light themes
- 📱 Mobile-friendly

**Example:**

```python
from pyosmo.reporting import Format, ReportConfig

config = ReportConfig(
    title="Shopping Cart Test Suite",
    theme="dark",
    include_charts=True
)

osmo.save_report("shopping_cart_report.html", format=Format.HTML, config=config)
```

### JSON Report

The JSON format provides structured data for programmatic access:

```json
{
  "summary": {
    "total_tests": 5,
    "total_steps": 237,
    "unique_steps": 12,
    "duration_seconds": 4.567,
    "error_count": 0
  },
  "statistics": {
    "step_frequency": {...},
    "step_execution_times": {...}
  },
  "test_cases": [...]
}
```

**Use cases:**
- Data analysis with pandas
- Integration with custom tools
- Automated processing
- Long-term data storage

**Example:**

```python
import json
import pandas as pd

# Generate JSON report
osmo.save_report("results.json", format=Format.JSON)

# Load and analyze
with open("results.json") as f:
    data = json.load(f)

# Convert to DataFrame for analysis
df = pd.DataFrame(data["test_cases"])
print(df.describe())
```

### JUnit XML Report

The JUnit XML format is compatible with most CI/CD systems:

```xml
<?xml version="1.0" ?>
<testsuites name="PyOsmo Test Report" tests="5" failures="0">
  <testsuite name="PyOsmo Test Suite" tests="5" failures="0">
    <testcase classname="PyOsmo" name="TestCase_1" time="0.923"/>
    <testcase classname="PyOsmo" name="TestCase_2" time="0.891"/>
  </testsuite>
</testsuites>
```

**Integrations:**
- ✓ Jenkins
- ✓ GitLab CI
- ✓ GitHub Actions
- ✓ Azure Pipelines
- ✓ CircleCI

**Example (GitHub Actions):**

```yaml
# .github/workflows/test.yml
- name: Run PyOsmo Tests
  run: python run_tests.py

- name: Publish Test Results
  uses: EnricoMi/publish-unit-test-result-action@v2
  if: always()
  with:
    files: junit-results.xml
```

### Markdown Report

The Markdown format creates human-readable documentation:

```markdown
# PyOsmo Test Report

## Summary
- **Total Tests**: 5
- **Total Steps**: 237
- **Duration**: 0:00:04.567000

## Step Execution Frequency
| Step Name | Execution Count | Avg Duration (s) |
|-----------|-----------------|------------------|
| browse_products | 45 | 0.0234 |
| add_to_cart | 32 | 0.0156 |
```

**Use cases:**
- Include in README files
- Add to documentation sites
- Commit to version control
- Share in pull requests

### CSV Report

The CSV format provides tabular data for spreadsheet analysis:

```csv
test_case_id,step_index,step_name,timestamp,duration_seconds,has_error
1,1,login,2025-01-15T10:30:45.123,0.023,No
1,2,browse_products,2025-01-15T10:30:45.150,0.034,No
```

**Use cases:**
- Excel/Google Sheets analysis
- Database imports
- Statistical analysis
- Custom visualizations

## Direct Reporter Usage

For more control, use reporters directly:

```python
from pyosmo.reporting import HTMLReporter, JSONReporter, ReportConfig

# Get history after test execution
osmo.run()
history = osmo.history

# Create custom reporter
config = ReportConfig(title="Custom Report")
reporter = HTMLReporter(history, config)

# Get report content as string
html_content = reporter.generate()

# Save to file
reporter.save("custom_report.html")
```

## Programmatic Data Access

Access test data programmatically without generating reports:

```python
# Get statistics object
stats = osmo.history.statistics()

print(f"Total steps: {stats.total_steps}")
print(f"Unique steps: {stats.unique_steps}")
print(f"Duration: {stats.duration}")
print(f"Most executed: {stats.most_executed_step}")

# Get step frequency
frequency = osmo.history.step_frequency()
print(f"Step frequency: {frequency}")

# Get step pairs (transitions)
pairs = osmo.history.step_pairs()
print(f"Most common transition: {max(pairs.items(), key=lambda x: x[1])}")

# Get coverage timeline
timeline = osmo.history.coverage_timeline()
print(f"Coverage progression: {timeline}")

# Get failed tests
failed = osmo.history.failed_tests()
print(f"Failed test count: {len(failed)}")
```

## CI/CD Integration Examples

### GitHub Actions

```yaml
name: PyOsmo Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install pyosmo
      - name: Run tests
        run: python run_tests.py
      - name: Publish Test Results
        uses: EnricoMi/publish-unit-test-result-action@v2
        if: always()
        with:
          files: junit-results.xml
      - name: Upload HTML Report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-report
          path: report.html
```

### GitLab CI

```yaml
test:
  script:
    - pip install pyosmo
    - python run_tests.py
  artifacts:
    when: always
    reports:
      junit: junit-results.xml
    paths:
      - report.html
```

### Jenkins

```groovy
pipeline {
    agent any
    stages {
        stage('Test') {
            steps {
                sh 'pip install pyosmo'
                sh 'python run_tests.py'
            }
            post {
                always {
                    junit 'junit-results.xml'
                    publishHTML([
                        reportDir: '.',
                        reportFiles: 'report.html',
                        reportName: 'PyOsmo Test Report'
                    ])
                }
            }
        }
    }
}
```

## Best Practices

### 1. Generate Multiple Formats

Generate multiple formats to serve different audiences:

```python
osmo.save_reports(
    "reports/nightly_run",
    formats=[
        Format.HTML,    # For human review
        Format.JSON,    # For data analysis
        Format.JUNIT,   # For CI/CD
    ]
)
```

### 2. Use Meaningful Report Titles

```python
from datetime import datetime

config = ReportConfig(
    title=f"Shopping Cart Tests - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
)
osmo.save_report("report.html", config=config)
```

### 3. Organize Reports by Date

```python
from datetime import datetime
from pathlib import Path

# Create date-based directory
report_dir = Path(f"reports/{datetime.now().strftime('%Y-%m-%d')}")
report_dir.mkdir(parents=True, exist_ok=True)

# Save reports
osmo.save_reports(f"{report_dir}/test_run")
```

### 4. Compare Reports Over Time

```python
import json

# Save JSON for historical comparison
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
osmo.save_report(f"history/results_{timestamp}.json", format=Format.JSON)

# Later: compare metrics over time
def compare_runs(file1, file2):
    with open(file1) as f1, open(file2) as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)

    coverage_change = (
        data2['summary']['unique_steps'] -
        data1['summary']['unique_steps']
    )
    print(f"Coverage change: {coverage_change} steps")
```

## Examples

### Complete Example

```python
from pyosmo import Osmo
from pyosmo.decorators import step, guard
from pyosmo.end_conditions import Length
from pyosmo.reporting import Format, ReportConfig

# Define model
class ShoppingModel:
    def __init__(self):
        self.cart = []
        self.logged_in = False

    @step
    def step_login(self):
        self.logged_in = True

    @guard("step_add_to_cart")
    def guard_add_to_cart(self):
        return self.logged_in

    @step
    def step_add_to_cart(self):
        self.cart.append("item")

# Run tests
osmo = Osmo(ShoppingModel())
osmo.test_end_condition = Length(50)
osmo.test_suite_end_condition = Length(3)
osmo.run()

# Generate reports
config = ReportConfig(
    title="Shopping Cart Test Suite",
    theme="light",
    include_charts=True
)

# Save multiple formats
osmo.save_reports(
    "reports/shopping_cart",
    formats=[Format.HTML, Format.JSON, Format.JUNIT],
    config=config
)

print("Reports generated successfully!")
print(f"Tests: {osmo.history.test_case_count}")
print(f"Steps: {osmo.history.total_amount_of_steps}")
print(f"Duration: {osmo.history.duration}")
```

## API Reference

### Osmo Methods

#### `save_report(path, format, config)`

Save a single report.

**Parameters:**
- `path` (str): File path where report should be saved
- `format` (Format): Report format (HTML, JSON, JUNIT, MARKDOWN, CSV)
- `config` (ReportConfig, optional): Configuration for report generation

#### `save_reports(base_path, formats, config)`

Save multiple reports at once.

**Parameters:**
- `base_path` (str): Base file path without extension
- `formats` (List[Format], optional): List of formats (defaults to all)
- `config` (ReportConfig, optional): Configuration for report generation

### ReportConfig

Configuration for report generation.

**Attributes:**
- `title` (str): Report title (default: "PyOsmo Test Report")
- `include_charts` (bool): Include visualizations (default: True)
- `include_timeline` (bool): Include test timeline (default: True)
- `include_statistics` (bool): Include detailed stats (default: True)
- `theme` (str): "light" or "dark" (default: "light")
- `custom_css` (str, optional): Path to custom CSS file

### Reporter Classes

All reporters inherit from the base `Reporter` class:

- `HTMLReporter`: Interactive HTML reports with charts
- `JSONReporter`: Structured JSON data
- `JUnitReporter`: JUnit XML for CI/CD
- `MarkdownReporter`: Markdown documentation
- `CSVReporter`: CSV tabular data

**Common Methods:**
- `generate()`: Generate report content as string
- `save(path)`: Save report to file

## Troubleshooting

### Charts Not Showing in HTML

Make sure you have internet connection for loading Chart.js from CDN, or the charts won't render.

### Large CSV Files

For very long test runs, CSV files can become large. Consider using JSON and processing with pandas instead.

### Custom Styling

To customize HTML report appearance, create a custom CSS file and reference it:

```python
config = ReportConfig(
    theme="light",
    custom_css="path/to/custom.css"
)
```

## Next Steps

- Learn about [Test History and Statistics](./history_and_statistics.md)
- Explore [CI/CD Integration](./ci_cd_integration.md)
- Check out [Complete Examples](../examples/)

---

*For more information, see the [PyOsmo documentation](../README.md).*
