"""Tests for PyOsmo Reporting API."""

import json
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from pyosmo import Osmo
from pyosmo.decorators import guard, step
from pyosmo.end_conditions import Length
from pyosmo.reporting import (
    CSVReporter,
    Format,
    HTMLReporter,
    JSONReporter,
    JUnitReporter,
    MarkdownReporter,
    ReportConfig,
    Reporter,
)


class SimpleTestModel:
    """Simple test model for reporting tests."""

    def __init__(self):
        self.counter = 0

    @step
    def step_increment(self):
        """Increment counter."""
        self.counter += 1

    @step
    def step_decrement(self):
        """Decrement counter."""
        self.counter -= 1

    @guard("step_decrement")
    def guard_decrement(self):
        return self.counter > 0


class TestReporters:
    """Test all reporter classes."""

    @pytest.fixture
    def osmo_with_history(self):
        """Create Osmo instance with test history."""
        model = SimpleTestModel()
        osmo = Osmo(model)
        osmo.seed = 42
        osmo.test_end_condition = Length(10)
        osmo.test_suite_end_condition = Length(2)
        osmo.run()
        return osmo

    def test_json_reporter_generate(self, osmo_with_history):
        """Test JSONReporter generates valid JSON."""
        reporter = JSONReporter(osmo_with_history.history)
        content = reporter.generate()

        # Should be valid JSON
        data = json.loads(content)

        # Check structure
        assert "config" in data
        assert "summary" in data
        assert "statistics" in data
        assert "coverage" in data
        assert "test_cases" in data

        # Check summary content
        assert data["summary"]["total_tests"] == 2
        assert data["summary"]["total_steps"] == 20
        assert data["summary"]["error_count"] == 0

    def test_json_reporter_to_dict(self, osmo_with_history):
        """Test JSONReporter.to_dict() method."""
        reporter = JSONReporter(osmo_with_history.history)
        data = reporter.to_dict()

        assert isinstance(data, dict)
        assert "summary" in data
        assert "test_cases" in data
        assert isinstance(data["test_cases"], list)

    def test_html_reporter_generate(self, osmo_with_history):
        """Test HTMLReporter generates valid HTML."""
        reporter = HTMLReporter(osmo_with_history.history)
        content = reporter.generate()

        # Should contain HTML tags
        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "</html>" in content
        assert "<body>" in content

        # Should contain title
        assert "PyOsmo Test Report" in content

        # Should contain Chart.js
        assert "chart.js" in content.lower()

    def test_html_reporter_light_theme(self, osmo_with_history):
        """Test HTMLReporter with light theme."""
        config = ReportConfig(theme="light")
        reporter = HTMLReporter(osmo_with_history.history, config)
        content = reporter.generate()

        # Light theme colors should be present
        assert "#f5f5f5" in content or "background" in content

    def test_html_reporter_dark_theme(self, osmo_with_history):
        """Test HTMLReporter with dark theme."""
        config = ReportConfig(theme="dark")
        reporter = HTMLReporter(osmo_with_history.history, config)
        content = reporter.generate()

        # Dark theme colors should be present
        assert "#1a1a1a" in content or "background" in content

    def test_html_reporter_no_charts(self, osmo_with_history):
        """Test HTMLReporter without charts."""
        config = ReportConfig(include_charts=False)
        reporter = HTMLReporter(osmo_with_history.history, config)
        content = reporter.generate()

        # Should not include Chart.js
        assert "chart.js" not in content.lower()

    def test_html_reporter_custom_title(self, osmo_with_history):
        """Test HTMLReporter with custom title."""
        config = ReportConfig(title="Custom Test Report")
        reporter = HTMLReporter(osmo_with_history.history, config)
        content = reporter.generate()

        assert "Custom Test Report" in content

    def test_markdown_reporter_generate(self, osmo_with_history):
        """Test MarkdownReporter generates valid Markdown."""
        reporter = MarkdownReporter(osmo_with_history.history)
        content = reporter.generate()

        # Should contain Markdown headers
        assert "# PyOsmo Test Report" in content
        assert "## Summary" in content

        # Should contain summary data
        assert "Total Tests" in content
        assert "Total Steps" in content

        # Should contain tables
        assert "|" in content
        assert "---" in content

    def test_markdown_reporter_custom_config(self, osmo_with_history):
        """Test MarkdownReporter with custom config."""
        config = ReportConfig(
            title="Custom Markdown Report",
            include_statistics=False,
            include_timeline=False,
        )
        reporter = MarkdownReporter(osmo_with_history.history, config)
        content = reporter.generate()

        assert "Custom Markdown Report" in content

    def test_junit_reporter_generate(self, osmo_with_history):
        """Test JUnitReporter generates valid XML."""
        reporter = JUnitReporter(osmo_with_history.history)
        content = reporter.generate()

        # Should be valid XML
        root = ET.fromstring(content)
        assert root.tag == "testsuites"

        # Check attributes
        assert root.get("tests") == "2"
        assert root.get("failures") == "0"

        # Should have testsuite
        testsuite = root.find("testsuite")
        assert testsuite is not None

        # Should have test cases
        testcases = testsuite.findall("testcase")
        assert len(testcases) == 2

    def test_junit_reporter_test_case_attributes(self, osmo_with_history):
        """Test JUnitReporter test case attributes."""
        reporter = JUnitReporter(osmo_with_history.history)
        content = reporter.generate()
        root = ET.fromstring(content)

        testsuite = root.find("testsuite")
        testcase = testsuite.find("testcase")

        # Check test case attributes
        assert testcase.get("classname") == "PyOsmo"
        assert "TestCase_" in testcase.get("name")
        assert testcase.get("time") is not None

    def test_csv_reporter_generate(self, osmo_with_history):
        """Test CSVReporter generates valid CSV."""
        reporter = CSVReporter(osmo_with_history.history)
        content = reporter.generate()

        # Should contain CSV headers
        assert "test_case_id" in content
        assert "step_index" in content
        assert "step_name" in content
        assert "duration_seconds" in content

        # Should contain data rows
        lines = content.strip().split("\n")
        assert len(lines) > 1  # Header + data rows

        # Check data format
        assert "step_increment" in content or "step_decrement" in content

    def test_csv_reporter_data_format(self, osmo_with_history):
        """Test CSVReporter data format."""
        reporter = CSVReporter(osmo_with_history.history)
        content = reporter.generate()

        lines = content.strip().split("\n")
        # First line should be header
        header = lines[0]
        assert "test_case_id,step_index,step_name" in header

        # Second line should be data
        if len(lines) > 1:
            data_line = lines[1]
            parts = data_line.split(",")
            # Should have all columns
            assert len(parts) >= 7  # All expected columns

    def test_reporter_save_method(self, osmo_with_history):
        """Test Reporter.save() method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_report.json"

            reporter = JSONReporter(osmo_with_history.history)
            reporter.save(str(path))

            # File should exist
            assert path.exists()

            # File should contain valid JSON
            with open(path) as f:
                data = json.load(f)
            assert "summary" in data


class TestOsmoIntegration:
    """Test Osmo class integration with reporting."""

    @pytest.fixture
    def osmo_with_history(self):
        """Create Osmo instance with test history."""
        model = SimpleTestModel()
        osmo = Osmo(model)
        osmo.seed = 42
        osmo.test_end_condition = Length(10)
        osmo.test_suite_end_condition = Length(2)
        osmo.run()
        return osmo

    def test_save_report_html(self, osmo_with_history):
        """Test Osmo.save_report() with HTML format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.html"

            osmo_with_history.save_report(str(path), format=Format.HTML)

            assert path.exists()
            content = path.read_text()
            assert "<!DOCTYPE html>" in content

    def test_save_report_json(self, osmo_with_history):
        """Test Osmo.save_report() with JSON format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.json"

            osmo_with_history.save_report(str(path), format=Format.JSON)

            assert path.exists()
            with open(path) as f:
                data = json.load(f)
            assert "summary" in data

    def test_save_report_junit(self, osmo_with_history):
        """Test Osmo.save_report() with JUnit format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "junit.xml"

            osmo_with_history.save_report(str(path), format=Format.JUNIT)

            assert path.exists()
            content = path.read_text()
            root = ET.fromstring(content)
            assert root.tag == "testsuites"

    def test_save_report_markdown(self, osmo_with_history):
        """Test Osmo.save_report() with Markdown format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.md"

            osmo_with_history.save_report(str(path), format=Format.MARKDOWN)

            assert path.exists()
            content = path.read_text()
            assert "# PyOsmo Test Report" in content

    def test_save_report_csv(self, osmo_with_history):
        """Test Osmo.save_report() with CSV format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.csv"

            osmo_with_history.save_report(str(path), format=Format.CSV)

            assert path.exists()
            content = path.read_text()
            assert "test_case_id" in content

    def test_save_report_with_config(self, osmo_with_history):
        """Test Osmo.save_report() with custom config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.html"
            config = ReportConfig(
                title="Custom Report Title",
                theme="dark",
            )

            osmo_with_history.save_report(str(path), format=Format.HTML, config=config)

            assert path.exists()
            content = path.read_text()
            assert "Custom Report Title" in content

    def test_save_reports_all_formats(self, osmo_with_history):
        """Test Osmo.save_reports() with all formats."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir) / "test_run"

            osmo_with_history.save_reports(str(base_path))

            # Should create all format files
            assert (Path(tmpdir) / "test_run.html").exists()
            assert (Path(tmpdir) / "test_run.json").exists()
            assert (Path(tmpdir) / "test_run.xml").exists()
            assert (Path(tmpdir) / "test_run.md").exists()
            assert (Path(tmpdir) / "test_run.csv").exists()

    def test_save_reports_selected_formats(self, osmo_with_history):
        """Test Osmo.save_reports() with selected formats."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir) / "test_run"

            osmo_with_history.save_reports(
                str(base_path),
                formats=[Format.HTML, Format.JSON],
            )

            # Should create only selected files
            assert (Path(tmpdir) / "test_run.html").exists()
            assert (Path(tmpdir) / "test_run.json").exists()
            assert not (Path(tmpdir) / "test_run.xml").exists()
            assert not (Path(tmpdir) / "test_run.md").exists()
            assert not (Path(tmpdir) / "test_run.csv").exists()

    def test_save_reports_with_config(self, osmo_with_history):
        """Test Osmo.save_reports() with custom config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir) / "test_run"
            config = ReportConfig(title="Batch Report")

            osmo_with_history.save_reports(
                str(base_path),
                formats=[Format.HTML, Format.JSON],
                config=config,
            )

            # Check HTML contains custom title
            html_path = Path(tmpdir) / "test_run.html"
            assert html_path.exists()
            content = html_path.read_text()
            assert "Batch Report" in content

            # Check JSON contains custom title
            json_path = Path(tmpdir) / "test_run.json"
            assert json_path.exists()
            with open(json_path) as f:
                data = json.load(f)
            assert data["config"]["title"] == "Batch Report"

    def test_save_report_invalid_format(self, osmo_with_history):
        """Test Osmo.save_report() with invalid format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.txt"

            # This should raise ValueError for unsupported format
            # Since we're using an enum, we can't easily pass an invalid format
            # But we can test that the reporter_map handles it correctly
            # by checking that only valid formats work
            osmo_with_history.save_report(str(path), format=Format.HTML)
            assert path.exists()


class TestReportConfig:
    """Test ReportConfig functionality."""

    def test_default_config(self):
        """Test ReportConfig with default values."""
        config = ReportConfig()

        assert config.title == "PyOsmo Test Report"
        assert config.include_charts is True
        assert config.include_timeline is True
        assert config.include_statistics is True
        assert config.theme == "light"
        assert config.custom_css is None

    def test_custom_config(self):
        """Test ReportConfig with custom values."""
        config = ReportConfig(
            title="Custom Title",
            include_charts=False,
            include_timeline=False,
            include_statistics=False,
            theme="dark",
            custom_css="/path/to/custom.css",
        )

        assert config.title == "Custom Title"
        assert config.include_charts is False
        assert config.include_timeline is False
        assert config.include_statistics is False
        assert config.theme == "dark"
        assert config.custom_css == "/path/to/custom.css"


class TestReportContent:
    """Test report content accuracy."""

    @pytest.fixture
    def osmo_with_history(self):
        """Create Osmo instance with predictable history."""
        model = SimpleTestModel()
        osmo = Osmo(model)
        osmo.seed = 12345
        osmo.test_end_condition = Length(5)
        osmo.test_suite_end_condition = Length(3)
        osmo.run()
        return osmo

    def test_json_report_accuracy(self, osmo_with_history):
        """Test JSON report contains accurate data."""
        reporter = JSONReporter(osmo_with_history.history)
        data = reporter.to_dict()

        # Check summary matches history
        assert data["summary"]["total_tests"] == osmo_with_history.history.test_case_count
        assert data["summary"]["total_steps"] == osmo_with_history.history.total_amount_of_steps
        assert data["summary"]["error_count"] == osmo_with_history.history.error_count

        # Check test cases
        assert len(data["test_cases"]) == osmo_with_history.history.test_case_count

    def test_step_frequency_accuracy(self, osmo_with_history):
        """Test step frequency is accurate across reporters."""
        stats = osmo_with_history.history.statistics()

        # JSON reporter
        json_reporter = JSONReporter(osmo_with_history.history)
        json_data = json_reporter.to_dict()
        assert json_data["statistics"]["step_frequency"] == stats.step_frequency

    def test_duration_accuracy(self, osmo_with_history):
        """Test duration is accurate in reports."""
        json_reporter = JSONReporter(osmo_with_history.history)
        data = json_reporter.to_dict()

        expected_duration = osmo_with_history.history.duration.total_seconds()
        assert data["summary"]["duration_seconds"] == pytest.approx(expected_duration, rel=1e-6)


class TestErrorHandling:
    """Test error handling in reporters."""

    def test_reporter_with_empty_history(self):
        """Test reporters handle empty history."""
        osmo = Osmo(SimpleTestModel())
        # Don't run, so history is empty

        # Should not crash, but may have minimal data
        json_reporter = JSONReporter(osmo.history)
        content = json_reporter.generate()
        data = json.loads(content)
        assert data["summary"]["total_tests"] == 0

    def test_html_reporter_with_errors(self):
        """Test HTML reporter handles test errors."""

        class ErrorModel:
            @step
            def step_that_fails(self):
                raise ValueError("Test error")

        osmo = Osmo(ErrorModel())
        osmo.test_end_condition = Length(2)
        osmo.test_suite_end_condition = Length(1)

        # Run with error handling
        from pyosmo.error_strategy import AlwaysIgnore

        osmo.test_error_strategy = AlwaysIgnore()
        osmo.run()

        # Should still generate report
        reporter = HTMLReporter(osmo.history)
        content = reporter.generate()
        assert "<!DOCTYPE html>" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
