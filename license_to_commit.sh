#/bin/bash
uv sync --all-extras
uv run pytest pyosmo/tests/
uv run pylint *
uv run flake8 --max-line-length 120 --ignore=E722,F401,E402
uv run mypy pyosmo/