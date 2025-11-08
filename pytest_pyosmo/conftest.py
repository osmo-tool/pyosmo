"""
conftest.py - How to integrate pytest-pyosmo into your project

There are two ways to add this plugin:

OPTION 1: Import from pytest_pyosmo package (once installed)
---

    # In your conftest.py
    pytest_plugins = ["pytest_pyosmo.plugin"]

OPTION 2: Copy plugin code directly
---

    # Copy pytest_pyosmo_plugin.py into your project
    # Then in conftest.py:
    pytest_plugins = ["pytest_pyosmo_plugin"]

OPTION 3: Paste plugin code directly here
---

    # Just copy the entire plugin code into conftest.py
    # (See pytest_pyosmo_plugin.py)

For this example, we'll do OPTION 2 (most common):
"""

import sys
from pathlib import Path

# Make the plugin available
# (In real project, this would be: pytest_plugins = ["pytest_pyosmo.plugin"])
pytest_plugins = ["pytest_pyosmo_plugin"]  # We copied pytest_pyosmo_plugin.py to this dir


# ============================================================================
# Optional: Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """
    Optional pytest configuration for model-based testing.
    
    You can set defaults here that apply to all models.
    """
    print("\n" + "="*70)
    print("Pytest-Pyosmo Integration Example")
    print("="*70)
    print("\nHow to run:")
    print("  pytest -v                    # All tests")
    print("  pytest -m quick              # Quick smoke tests only")
    print("  pytest -m comprehensive      # Full coverage tests")
    print("  pytest --collect-only -q     # Show what will run")
    print("  pytest -k CounterModel       # Run specific model")
    print("  pytest -v -s                 # Verbose with print statements")
    print("="*70 + "\n")


# ============================================================================
# Optional: Pytest Hooks for Model Testing
# ============================================================================

def pytest_collection_modifyitems(items):
    """
    Optional: Modify collected items.
    
    This is called after pytest discovers all tests (including generated ones).
    You can use this to:
    - Add markers dynamically
    - Skip certain tests
    - Modify test configuration
    """
    for item in items:
        if "ModelTestItem" in item.__class__.__name__:
            # This is a generated model test
            # You could add markers, modify timeouts, etc.
            pass
