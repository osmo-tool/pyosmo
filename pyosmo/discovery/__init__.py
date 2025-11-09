"""Model discovery strategies for PyOsmo.

This module provides extensible discovery mechanisms for finding test steps,
guards, and weights in model classes.
"""

from pyosmo.discovery.base import DiscoveryStrategy, ModelMetadata
from pyosmo.discovery.decorator import DecoratorBasedDiscovery
from pyosmo.discovery.naming import NamingConventionDiscovery
from pyosmo.discovery.orchestrator import ModelDiscovery

__all__ = [
    'DiscoveryStrategy',
    'ModelMetadata',
    'DecoratorBasedDiscovery',
    'NamingConventionDiscovery',
    'ModelDiscovery',
]
