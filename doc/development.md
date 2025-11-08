# Pyosmo development

### Enable debug logging

```python
import logging, sys

# initalize osmo with model

logger = logging.getLogger('osmo')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))
osmo.generate()
```

### Install tools needed for development

```bash
uv pip install -e ".[dev]"
# or
uv sync --all-extras
```

### Run osmo tests:

```bash
pytest pyosmo/tests/
```

### Run ruff linting

```bash
ruff check pyosmo/
```

### Auto-fix linting issues

```bash
ruff check pyosmo/ --fix
```

### Run ruff formatting

```bash
ruff format pyosmo/
```

### Check formatting without changes

```bash
ruff format --check pyosmo/
```

### Run type checking

```bash
mypy pyosmo/
```

### Run mutation testing
*Read more about the tool in https://github.com/boxed/mutmut*
```bash
mutmut run
```
