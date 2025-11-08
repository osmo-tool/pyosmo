"""
setup.py for pytest-pyosmo

Packages the plugin for installation via pip.

Usage:
    pip install -e .
    
Then pytest will automatically discover and load the plugin.
"""

from setuptools import setup, find_packages

setup(
    name="pytest-pyosmo",
    version="1.0.0",
    description="Model-based testing discovery plugin for pytest",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Pyosmo Team",
    author_email="hello@pyosmo.dev",
    url="https://github.com/osmo-tool/pytest-pyosmo",
    license="MIT",
    
    packages=find_packages(),
    
    # Plugin dependencies
    install_requires=[
        "pytest>=7.0",
        "pyosmo>=1.0.0",
    ],
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest-cov>=3.0",
            "black>=22.0",
            "mypy>=0.900",
            "flake8>=4.0",
        ],
    },
    
    # Make pytest automatically discover our plugin
    entry_points={
        "pytest11": [
            "pytest_pyosmo = pytest_pyosmo_plugin",
        ],
    },
    
    python_requires=">=3.9",
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Testing",
    ],
    
    keywords=[
        "pytest",
        "model-based-testing",
        "testing",
        "state-machine",
        "pyosmo",
    ],
)
