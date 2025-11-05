"""Reporting module for PyOsmo test execution results.

This module provides various reporters to export test execution history
in different formats (HTML, JSON, JUnit XML, Markdown, CSV).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from pyosmo.history.history import OsmoHistory


class Format(Enum):
    """Supported report output formats."""

    HTML = "html"
    JSON = "json"
    JUNIT = "junit"
    MARKDOWN = "md"
    CSV = "csv"


@dataclass
class ReportConfig:
    """Configuration for report generation.

    Attributes:
        title: Report title
        include_charts: Whether to include visualizations (for HTML)
        include_timeline: Whether to include execution timeline
        include_statistics: Whether to include detailed statistics
        theme: Visual theme for HTML reports ("light" or "dark")
        custom_css: Optional path to custom CSS file for HTML reports
    """

    title: str = "PyOsmo Test Report"
    include_charts: bool = True
    include_timeline: bool = True
    include_statistics: bool = True
    theme: str = "light"
    custom_css: Optional[str] = None


class Reporter(ABC):
    """Base class for all report generators.

    Reporters convert test execution history into various output formats.
    """

    def __init__(self, history: "OsmoHistory", config: Optional[ReportConfig] = None) -> None:
        """Initialize reporter.

        Args:
            history: Test execution history to report on
            config: Optional configuration for report generation
        """
        self.history = history
        self.config = config or ReportConfig()

    @abstractmethod
    def generate(self) -> str:
        """Generate report content.

        Returns:
            Report content as a string
        """
        ...

    def save(self, path: str) -> None:
        """Save report to file.

        Args:
            path: File path where report should be saved
        """
        content = self.generate()
        Path(path).write_text(content, encoding="utf-8")


# Import specific reporters for easier access
from pyosmo.reporting.csv_reporter import CSVReporter
from pyosmo.reporting.html_reporter import HTMLReporter
from pyosmo.reporting.json_reporter import JSONReporter
from pyosmo.reporting.junit_reporter import JUnitReporter
from pyosmo.reporting.markdown_reporter import MarkdownReporter

__all__ = [
    "Format",
    "ReportConfig",
    "Reporter",
    "HTMLReporter",
    "JSONReporter",
    "JUnitReporter",
    "MarkdownReporter",
    "CSVReporter",
]
