.PHONY: help test lint format version-patch version-minor version-major publish-patch publish-minor publish-major build check-pypi

help:
	@echo "PyOsmo Development Commands"
	@echo ""
	@echo "Testing:"
	@echo "  make test                Run all tests"
	@echo "  make test-cov            Run tests with coverage"
	@echo ""
	@echo "Linting & Formatting:"
	@echo "  make lint                Run ruff linter"
	@echo "  make format              Format code with ruff"
	@echo "  make typecheck           Run mypy type checker"
	@echo ""
	@echo "Version Management:"
	@echo "  make version-patch       Bump patch version (0.2.2 -> 0.2.3)"
	@echo "  make version-minor       Bump minor version (0.2.2 -> 0.3.0)"
	@echo "  make version-major       Bump major version (0.2.2 -> 1.0.0)"
	@echo "  make check-pypi          Check if current version exists on PyPI"
	@echo ""
	@echo "Publishing:"
	@echo "  make publish-patch       Bump patch version and publish"
	@echo "  make publish-minor       Bump minor version and publish"
	@echo "  make publish-major       Bump major version and publish"
	@echo ""
	@echo "Building:"
	@echo "  make build               Build distribution packages"
	@echo "  make clean               Clean build artifacts"

# Testing
test:
	pytest pyosmo/tests/

test-cov:
	pytest pyosmo/tests/ --cov=pyosmo

# Linting & Formatting
lint:
	ruff check pyosmo/

lint-fix:
	ruff check pyosmo/ --fix

format:
	ruff format pyosmo/

format-check:
	ruff format --check pyosmo/

typecheck:
	mypy pyosmo/

# Version Management
version-patch:
	python scripts/bump_version.py patch

version-minor:
	python scripts/bump_version.py minor

version-major:
	python scripts/bump_version.py major

check-pypi:
	@python scripts/check_pypi.py

# Publishing (automated workflow)
publish-patch:
	python scripts/publish.py patch

publish-minor:
	python scripts/publish.py minor

publish-major:
	python scripts/publish.py major

# Building
build:
	python -m build

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
