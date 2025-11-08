#!/bin/bash
set -e

uv sync --all-extras
uv run ruff check --fix pyosmo/
uv run ruff format --check pyosmo/
uv run mypy pyosmo/
uv run pytest pyosmo/tests/
