"""
PyOsmo Model Creator - Autonomous website model generation tool.

This package provides tools to automatically generate PyOsmo models from websites
by crawling and analyzing their structure and behavior.
"""

__version__ = "0.1.0"

from .crawler import WebsiteCrawler
from .generator import ModelGenerator
from .updater import ModelUpdater

__all__ = ["WebsiteCrawler", "ModelGenerator", "ModelUpdater"]
