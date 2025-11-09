# Publishing Guide

This guide explains how to publish new versions of PyOsmo to PyPI.

## Quick Start

The easiest way to publish a new version is to use the automated scripts:

```bash
# Bump patch version (0.2.2 -> 0.2.3) and publish
make publish-patch

# Bump minor version (0.2.2 -> 0.3.0) and publish
make publish-minor

# Bump major version (0.2.2 -> 1.0.0) and publish
make publish-major
```

## What the Automated Script Does

The `scripts/publish.py` script automates the entire publishing workflow:

1. **Checks git status** - Ensures working directory is clean
2. **Checks PyPI** - Verifies the current and new versions don't already exist
3. **Bumps version** - Updates version in `pyproject.toml`
4. **Commits changes** - Creates a commit with the version bump
5. **Creates git tag** - Tags the commit with `v{version}`
6. **Pushes to GitHub** - Pushes both commit and tag
7. **Provides next steps** - Shows link to create GitHub release

## Manual Version Bumping

If you just want to bump the version without publishing:

```bash
# Using make
make version-patch   # 0.2.2 -> 0.2.3
make version-minor   # 0.2.2 -> 0.3.0
make version-major   # 0.2.2 -> 1.0.0

# Using the script directly
python scripts/bump_version.py patch
python scripts/bump_version.py minor
python scripts/bump_version.py major

# Set specific version
python scripts/bump_version.py --version 1.0.0

# Dry run (see what would change)
python scripts/bump_version.py --dry-run patch
```

## Manual Publishing Workflow

If you prefer to do things manually:

1. **Check current version on PyPI:**
   ```bash
   make check-pypi
   ```

2. **Bump version:**
   ```bash
   python scripts/bump_version.py patch
   ```

3. **Review changes:**
   ```bash
   git diff pyproject.toml
   ```

4. **Commit and tag:**
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 0.2.3"
   git tag v0.2.3
   ```

5. **Push to GitHub:**
   ```bash
   git push origin main  # or your branch
   git push origin v0.2.3
   ```

6. **Create GitHub Release:**
   - Go to https://github.com/osmo-tool/pyosmo/releases/new
   - Select the tag you just created (e.g., `v0.2.3`)
   - Click "Generate release notes"
   - Review and edit the release notes if needed
   - Click "Publish release"

7. **Automatic PyPI Upload:**
   - The GitHub Action workflow (`.github/workflows/python-publish.yml`) will automatically:
     - Check that the version doesn't exist on PyPI
     - Build the distribution packages
     - Upload to PyPI using the configured API token

## Troubleshooting

### Error: Version already exists on PyPI

If you see this error:
```
HTTPError: 400 Bad Request from https://upload.pypi.org/legacy/
File already exists ('pyosmo-0.2.2-py3-none-any.whl'...)
```

**Solution:** You need to bump the version before publishing:
```bash
make publish-patch  # This will automatically bump and publish
```

Or manually:
```bash
python scripts/bump_version.py patch
```

### Error: Working directory is not clean

The automated script requires a clean git working directory.

**Solution:** Commit or stash your changes first:
```bash
git status
git add .
git commit -m "Your commit message"
# Then try publishing again
make publish-patch
```

### Version Check Fails in GitHub Actions

If the GitHub Action fails with "Version already exists on PyPI", it means:
- You created a GitHub release without bumping the version first
- The version in `pyproject.toml` was already published

**Solution:**
1. Delete the GitHub release and tag
2. Bump the version using the scripts
3. Create a new release with the new version

### Skipping Pre-Publish Checks

If you need to skip the git status and PyPI checks (not recommended):
```bash
python scripts/publish.py patch --skip-checks
```

## Version Numbering Guidelines

Follow [Semantic Versioning (SemVer)](https://semver.org/):

- **MAJOR** version (1.0.0 -> 2.0.0): Breaking changes / incompatible API changes
- **MINOR** version (0.2.0 -> 0.3.0): New features, backward compatible
- **PATCH** version (0.2.2 -> 0.2.3): Bug fixes, backward compatible

### Examples

- Bug fix: `make publish-patch`
- New feature: `make publish-minor`
- Breaking change: `make publish-major`

## CI/CD Workflow

The publishing workflow uses GitHub Actions:

1. **Trigger**: Creating a GitHub release
2. **Actions performed**:
   - Checkout code
   - Set up Python 3.11
   - Install `uv` for fast builds
   - **Check version doesn't exist on PyPI** ⭐ (prevents duplicate uploads)
   - Build distribution packages (wheel + source)
   - Upload to PyPI using API token

**Required Secret**: `PYPI_API_TOKEN` must be configured in GitHub repository secrets.

## First-Time Setup

If you're setting up publishing for the first time:

1. **Create PyPI API token:**
   - Go to https://pypi.org/manage/account/token/
   - Create a new API token scoped to the `pyosmo` project
   - Copy the token (it starts with `pypi-`)

2. **Add token to GitHub:**
   - Go to repository Settings > Secrets and variables > Actions
   - Create new secret named `PYPI_API_TOKEN`
   - Paste the PyPI token

3. **Test publishing:**
   - Consider testing on TestPyPI first
   - Or publish a patch version bump as a test

## Best Practices

1. **Always bump version before creating a release** - Use the automated scripts
2. **Test thoroughly before publishing** - Run `make test` and `make lint`
3. **Use semantic versioning** - Follow the MAJOR.MINOR.PATCH convention
4. **Write good release notes** - Use GitHub's "Generate release notes" feature
5. **Check PyPI after publishing** - Verify the new version appears at https://pypi.org/project/pyosmo/

## Useful Commands

```bash
# Development
make test              # Run tests
make lint              # Check code quality
make format            # Format code

# Version management
make check-pypi        # Check if current version exists on PyPI
make version-patch     # Bump patch version only (no publish)

# Publishing
make publish-patch     # Complete automated workflow
```

## Additional Resources

- [PyPI Help](https://pypi.org/help/)
- [Semantic Versioning](https://semver.org/)
- [Python Packaging Guide](https://packaging.python.org/)
- [GitHub Actions for Python](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)
