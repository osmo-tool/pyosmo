"""Plugin registry system for PyOsmo.

This module provides a centralized registry for algorithms, end conditions,
and error strategies, enabling easy discovery and extension.
"""

from pyosmo.plugins.registry import PluginRegistry, get_registry, register_algorithm

__all__ = [
    'PluginRegistry',
    'get_registry',
    'register_algorithm',
]
