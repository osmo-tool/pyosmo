#!/bin/bash
set -e

uv sync --all-extras
uv run ruff check --fix
uv run ruff format
uv run mypy pyosmo/
uv run mypy examples/
uv run pytest pyosmo/tests/
pytest pytest_pyosmo/test_models_example.py