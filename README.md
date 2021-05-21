# pyosmo

A simple model-based testing tool for python

pyosmo is python version of OSMO tester

Original OSMO tester can be found here: https://github.com/mukatee/osmo

Idea of model based testing is described in [introduction](doc/introduction.md)

## Example model

```python
class ExampleModel:

    def __init__(self):
        print('starting')
        self._counter = 0

    def before_test(self):
        self._counter = 0

    def guard_decrease(self):
        return self._counter > 1

    def step_decrease(self):
        self._counter -= 1
        print("- {}".format(self._counter))

    def guard_increase(self):
        return self._counter < 100

    def step_increase(self):
        self._counter += 1
        print("+ {}".format(self._counter))


osmo = Osmo()
osmo.add_model(ExampleModel())
osmo.set_algorithm(RandomAlgorithm())
osmo.set_test_end_condition(Length(100))
osmo.set_suite_end_condition(Length(100))
osmo.generate(seed=333)
```

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
