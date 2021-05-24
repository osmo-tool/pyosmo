## Pyosmo development

Enable debug logging

```python
import logging, sys

# initalize osmo with model

logger = logging.getLogger('osmo')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))
osmo.generate()
```

Install tools needed for development

```bash
pip install -r requirements.txt
```

Run osmo tests:

```bash
pytest pyosmo/tests/
```

Run pylint

```bash
pylint *
```
