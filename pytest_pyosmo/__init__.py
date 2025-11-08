"""
pytest-pyosmo: Model-based testing discovery for pytest

This plugin enables pytest to automatically discover @pytest.model classes
and generate tests from them using pyosmo.

Installation:
    pip install pytest pyosmo

Usage:
    pytest tests/ -v
    pytest tests/ -m quick
    pytest tests/ --collect-only

For more information, see the README.md file.
"""

__version__ = '0.1.0'
__all__ = []
