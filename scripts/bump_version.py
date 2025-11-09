#!/usr/bin/env python3
"""
Version bumping script for PyOsmo.

Usage:
    python scripts/bump_version.py patch   # 0.2.2 -> 0.2.3
    python scripts/bump_version.py minor   # 0.2.2 -> 0.3.0
    python scripts/bump_version.py major   # 0.2.2 -> 1.0.0
    python scripts/bump_version.py 0.3.0   # Set specific version
"""

import argparse
import re
import sys
from pathlib import Path


def get_current_version(pyproject_path: Path) -> str:
    """Extract current version from pyproject.toml."""
    content = pyproject_path.read_text()
    match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    if not match:
        raise ValueError('Could not find version in pyproject.toml')
    return match.group(1)


def parse_version(version: str) -> tuple[int, int, int]:
    """Parse version string into (major, minor, patch) tuple."""
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version)
    if not match:
        raise ValueError(f'Invalid version format: {version}')
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def bump_version(current: str, bump_type: str) -> str:
    """Bump version according to bump_type (patch/minor/major)."""
    major, minor, patch = parse_version(current)

    if bump_type == 'patch':
        patch += 1
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    else:
        # Assume it's a specific version string
        parse_version(bump_type)  # Validate format
        return bump_type

    return f'{major}.{minor}.{patch}'


def update_pyproject(pyproject_path: Path, old_version: str, new_version: str) -> None:
    """Update version in pyproject.toml."""
    content = pyproject_path.read_text()

    # Replace version line
    old_line = f'version = "{old_version}"'
    new_line = f'version = "{new_version}"'

    if old_line not in content:
        # Try single quotes
        old_line = f"version = '{old_version}'"
        new_line = f"version = '{new_version}'"

    if old_line not in content:
        raise ValueError(f'Could not find version line in pyproject.toml: {old_line}')

    new_content = content.replace(old_line, new_line)
    pyproject_path.write_text(new_content)


def main() -> int:
    parser = argparse.ArgumentParser(description='Bump version in pyproject.toml')
    parser.add_argument(
        'bump_type',
        choices=['patch', 'minor', 'major'],
        nargs='?',
        help='Version component to bump, or specific version number',
    )
    parser.add_argument(
        '--version',
        help='Set specific version number (e.g., 0.3.0)',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making changes',
    )

    args = parser.parse_args()

    # Determine what version change to make
    if args.version:
        bump_type = args.version
    elif args.bump_type:
        bump_type = args.bump_type
    else:
        parser.print_help()
        return 1

    # Find pyproject.toml
    repo_root = Path(__file__).parent.parent
    pyproject_path = repo_root / 'pyproject.toml'

    if not pyproject_path.exists():
        print(f'Error: pyproject.toml not found at {pyproject_path}', file=sys.stderr)
        return 1

    try:
        current_version = get_current_version(pyproject_path)
        new_version = bump_version(current_version, bump_type)

        print(f'Current version: {current_version}')
        print(f'New version: {new_version}')

        if args.dry_run:
            print('\n[DRY RUN] No changes made.')
            return 0

        update_pyproject(pyproject_path, current_version, new_version)
        print(f'\n✓ Successfully updated pyproject.toml to version {new_version}')
        print('\nNext steps:')
        print(f'  1. Review changes: git diff pyproject.toml')
        print(f'  2. Commit: git add pyproject.toml && git commit -m "Bump version to {new_version}"')
        print(f'  3. Tag: git tag v{new_version} && git push origin v{new_version}')
        print(f'  4. Create GitHub release from tag v{new_version}')

        return 0

    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
