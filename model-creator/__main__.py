"""
Main entry point for running the model-creator as a module.

Usage:
    python -m model-creator create <url> -o <output>
    python -m model-creator update <model> <url>
"""

from .cli import main

if __name__ == '__main__':
    main()
