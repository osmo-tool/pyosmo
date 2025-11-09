#!/usr/bin/env python3
"""Check if the current version exists on PyPI."""

import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


def main() -> int:
    # Read version from pyproject.toml
    pyproject = Path(__file__).parent.parent / 'pyproject.toml'
    content = pyproject.read_text()

    match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        print('Error: Could not find version in pyproject.toml', file=sys.stderr)
        return 1

    version = match.group(1)
    print(f'Current version: {version}')

    # Check if version exists on PyPI
    url = f'https://pypi.org/pypi/pyosmo/{version}/json'
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                print(f'❌ Version {version} already exists on PyPI')
                print(f'   URL: https://pypi.org/project/pyosmo/{version}/')
                return 1
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f'✓ Version {version} is available on PyPI')
            return 0
        else:
            print(f'Error checking PyPI: {e}', file=sys.stderr)
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
