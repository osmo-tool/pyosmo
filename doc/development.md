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
pip install -r requirements.txt
```

### Run osmo tests:

```bash
pytest pyosmo/tests/
```

### Run pylint

```bash
pylint *
```

### Run flake8

```bash
flake8 --max-line-length 120 --ignore=E722,F401,E402
```

### Run mutation testing
*Read more about the tool in https://github.com/boxed/mutmut*
```bash
mutmut run
```
