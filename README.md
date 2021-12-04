# pyosmo

A simple model-based testing (MBT) tool for python

pyosmo is python version of OSMO tester

Original OSMO tester can be found here: https://github.com/mukatee/osmo

Idea of model based testing is described in [introduction](doc/introduction.md)

## Install

```bash
pip install pyosmo
```

## Example model

```python
from pyosmo.osmo import Osmo


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


# Initialize Osmo with model
osmo = Osmo(ExampleModel())
# Generate tests
osmo.generate()
```

# Select your approach

## Offline model-based testing (MBT)

This means that the model will generate test cases which can be executed later using your existing test infrastructure.
[Checkout the example](examples/offline_mbt/README.md)

Pros:

* Maximum reuse of existing test harness
* Osmo runs once and generated tests can be execute multiple times same way
* Osmo can generate short tests for smoke and long tests for regression testing

Cons:

* The model cannot evolve based on system under testing responses
* Cannot test non-deterministic systems
* Cannot run "infinite"

## Online model-based testing

Online MBT means that when model steps are executed also real command are sent to the system and responses returned to
the model.

Pros:

* Model can be really smart because it may evolve based on the system
* Enable non-deterministic systems testing
* Test can take as long as needed

Cons:

* Typically need more experiences of modelling
* Cannot reuse existing test harness so easily

# Use cases

## Regression testing

```python
from pyosmo.osmo import Osmo
from pyosmo.end_conditions import StepCoverage
from pyosmo.end_conditions import Length

# This ues same example model than defined above
osmo = Osmo(ExampleModel())
# Make sure that osmo go trough whole model in every test case
osmo.test_end_condition = StepCoverage(100)
# Do some test cases, which test do not take too long
osmo.test_suite_end_condition = Length(3)
# Give seed to make sure that test is same every time
osmo.seed = 333
# Run osmo
osmo.generate()
```

## Long running test

```python
import datetime
from pyosmo.osmo import Osmo
from pyosmo.end_conditions import Time

osmo = Osmo(ExampleModel())
# Run model for ten hours
osmo.test_end_condition = Time(int(datetime.timedelta(hours=10).total_seconds()))
osmo.test_suite_end_condition = Length(1)
osmo.generate()
```

## Run with pytest

```python
def test_smoke():
    osmo = Osmo(ExampleModel())
    osmo.test_end_condition = Length(10)
    osmo.test_suite_end_condition = Length(1)
    osmo.algorithm = RandomAlgorithm()
    osmo.generate()
```

## Performance testing 

When system behaviour is modelled in online models you can use [https://locust.io/](https://locust.io/) 
to run multiple models parallel for stress test purposes. It may need 
