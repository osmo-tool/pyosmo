#!/bin/bash
set -e

uv sync --all-extras
uv run ruff check --fix
uv run ruff format
uv run ty check pyosmo/
uv run ty check examples/
uv run pytest pyosmo/tests/
uv run pytest pytest_pyosmo/test_models_example.py