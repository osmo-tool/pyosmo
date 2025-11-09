#!/usr/bin/env python3
"""
Automated publishing script for PyOsmo.

This script automates the entire publishing workflow:
1. Checks if version already exists on PyPI
2. Bumps version if needed
3. Commits and tags the new version
4. Pushes to GitHub
5. Creates a GitHub release (which triggers automatic PyPI upload)

Usage:
    python scripts/publish.py patch   # Bump patch version and publish
    python scripts/publish.py minor   # Bump minor version and publish
    python scripts/publish.py major   # Bump major version and publish
"""

import argparse
import json
import subprocess
import sys
import urllib.request
from pathlib import Path


def run_command(cmd: list[str], check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    """Run a shell command."""
    print(f'Running: {" ".join(cmd)}')
    if capture:
        return subprocess.run(cmd, check=check, capture_output=True, text=True)
    return subprocess.run(cmd, check=check)


def get_current_version() -> str:
    """Get current version from pyproject.toml."""
    result = subprocess.run(
        ['python', 'scripts/bump_version.py', '--dry-run', 'patch'],
        capture_output=True,
        text=True,
        check=True,
    )
    # Parse output to get current version
    for line in result.stdout.split('\n'):
        if line.startswith('Current version:'):
            return line.split(':')[1].strip()
    raise ValueError('Could not determine current version')


def check_version_on_pypi(package_name: str, version: str) -> bool:
    """Check if version exists on PyPI."""
    url = f'https://pypi.org/pypi/{package_name}/json'
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())
            versions = data.get('releases', {}).keys()
            return version in versions
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # Package doesn't exist yet
            return False
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description='Automated PyOsmo publishing')
    parser.add_argument(
        'bump_type',
        choices=['patch', 'minor', 'major'],
        help='Version component to bump',
    )
    parser.add_argument(
        '--skip-checks',
        action='store_true',
        help='Skip git status and PyPI version checks',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would happen without making changes',
    )

    args = parser.parse_args()

    try:
        # Check git status
        if not args.skip_checks:
            result = run_command(['git', 'status', '--porcelain'], capture=True)
            if result.stdout.strip() and not args.dry_run:
                print('\nError: Working directory is not clean. Please commit or stash changes first.')
                print(result.stdout)
                return 1

        # Get current version
        current_version = get_current_version()
        print(f'\nCurrent version: {current_version}')

        # Check if current version exists on PyPI
        if not args.skip_checks:
            print('Checking PyPI for existing version...')
            if check_version_on_pypi('pyosmo', current_version):
                print(f'⚠ Version {current_version} already exists on PyPI')
            else:
                print(f'✓ Version {current_version} not found on PyPI')

        # Bump version
        print(f'\nBumping {args.bump_type} version...')
        bump_cmd = ['python', 'scripts/bump_version.py', args.bump_type]
        if args.dry_run:
            bump_cmd.append('--dry-run')

        result = run_command(bump_cmd, capture=True)
        print(result.stdout)

        # Extract new version from output
        new_version = None
        for line in result.stdout.split('\n'):
            if line.startswith('New version:'):
                new_version = line.split(':')[1].strip()
                break

        if not new_version:
            print('Error: Could not determine new version')
            return 1

        if args.dry_run:
            print('\n[DRY RUN] Stopping here. No changes made.')
            return 0

        # Check if new version already exists on PyPI
        if not args.skip_checks:
            print(f'\nChecking if version {new_version} exists on PyPI...')
            if check_version_on_pypi('pyosmo', new_version):
                print(f'Error: Version {new_version} already exists on PyPI!')
                print('You may need to bump a higher version component (minor or major).')
                return 1
            else:
                print(f'✓ Version {new_version} is available on PyPI')

        # Git operations
        print('\nCommitting version bump...')
        run_command(['git', 'add', 'pyproject.toml'])
        run_command(['git', 'commit', '-m', f'Bump version to {new_version}'])

        print(f'\nCreating git tag v{new_version}...')
        run_command(['git', 'tag', '-a', f'v{new_version}', '-m', f'Release version {new_version}'])

        print('\nPushing to GitHub...')
        run_command(['git', 'push', 'origin', 'HEAD'])
        run_command(['git', 'push', 'origin', f'v{new_version}'])

        print(f'\n✓ Successfully prepared release {new_version}!')
        print('\nNext steps:')
        print(f'  1. Go to GitHub: https://github.com/osmo-tool/pyosmo/releases/new')
        print(f'  2. Select tag: v{new_version}')
        print(f'  3. Click "Generate release notes"')
        print(f'  4. Click "Publish release"')
        print('\nThe GitHub Action will automatically publish to PyPI when the release is created.')

        return 0

    except subprocess.CalledProcessError as e:
        print(f'\nError: Command failed: {e}', file=sys.stderr)
        return 1
    except Exception as e:
        print(f'\nError: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
