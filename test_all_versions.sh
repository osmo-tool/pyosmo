#!/bin/bash
set -e

VERSIONS=("3.11" "3.12" "3.13" "3.14")

for version in "${VERSIONS[@]}"; do
  echo "================================================"
  echo "Testing with Python $version"
  echo "================================================"

  # Use version-specific virtual environment directory
  venv_dir=".venv_${version//./}"  # e.g., .venv_311

  # Create/sync venv for this Python version if it doesn't exist
  if [ ! -d "$venv_dir" ]; then
    echo "Creating virtual environment for Python $version..."
    uv venv "$venv_dir" --python "$version"
  fi

  # Install dependencies in the specific venv
  uv pip install --python "$venv_dir" -e ".[dev]"

  # Activate and run checks using the specific venv
  source "$venv_dir/bin/activate"
  ruff check --fix
  ruff format
  ty check pyosmo/
  ty check examples/
  pytest pyosmo/tests/
  deactivate
done

echo "================================================"
echo "All Python versions tested successfully!"
echo "================================================"
