[![Test code](https://github.com/OPpuolitaival/pyosmo/actions/workflows/pr_check.yaml/badge.svg)](https://github.com/OPpuolitaival/pyosmo/actions/workflows/pr_check.yaml)

# pyosmo

A simple model-based testing (MBT) tool for python

Original OSMO tester can be found from: https://github.com/mukatee/osmo

## Motivation

Pyosmo is very useful tool when need to test system under testing logic very carefully or long time with automation.
This tool maximises the MBT tool flexibility and power by using the the pure python code as modelling language.

From traditional testing tools perspective pyosmo provides automated test case creation based on programmed model. In
practise parametrized test cases (for
example: [pytest parametrized fixtures](https://docs.pytest.org/en/6.2.x/parametrize.html))
are providing a bit similar functionality than simple test model can do. With true model it is able to plan a lot more
complex scenarions.

From traditional [Model-based testing](https://en.wikipedia.org/wiki/Model-based_testing) tools perspective pyosmo is
providing much more flexible modelling language and simple integration to the system under testing or test generator.
Traditionally MBT tools have been using graphical modelling language which leads the stat explosion when test data is
included to the model. In pyosmo the model is pure python. Then it is able to model anything that is able to code with
python. All python libraries are helping the modelling work.

## Install

using pip

```bash
pip install pyosmo
```

or using git clone

```bash
git clone git@github.com:OPpuolitaival/pyosmo.git
python -m pip install -e .
```

## Example model

```python
import pyosmo


class ExampleCalculatorModel:

    def __init__(self):
        print('starting')
        self._counter = 0

    def before_test(self):
        self._counter = 0

    def guard_decrease(self):
        return self._counter > 1

    def step_decrease(self):
        self._counter -= 1
        print(f"- {self._counter}")

    def guard_increase(self):
        return self._counter < 100

    def step_increase(self):
        self._counter += 1
        print(f"+ {self._counter}")


# Initialize Osmo with model
osmo = pyosmo.Osmo(ExampleCalculatorModel())
# Generate tests
osmo.run()
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
import pyosmo

# This ues same example model than defined above
osmo = pyosmo.Osmo(ExampleCalculatorModel())
# Make sure that osmo go trough whole model in every test case
osmo.test_end_condition = pyosmo.end_conditions.StepCoverage(100)
# Do some test cases, which test do not take too long
osmo.test_suite_end_condition = pyosmo.end_conditions.Length(3)
# Give seed to make sure that test is same every time
osmo.seed = 333
# Run osmo
osmo.generate()
```

## Long running test

```python
import datetime
import pyosmo

osmo = pyosmo.Osmo(ExampleCalculatorModel())
# Run model for ten hours
osmo.test_end_condition = pyosmo.end_conditions.Time(int(datetime.timedelta(hours=10).total_seconds()))
osmo.test_suite_end_condition = pyosmo.end_conditions.Length(1)
osmo.generate()
```

## Run with pytest

```python
import pyosmo
# You can use your existing fixtures normally
def test_smoke():
    osmo = pyosmo.Osmo(ExampleCalculatorModel())
    osmo.test_end_condition = pyosmo.end_conditions.Length(10)
    osmo.test_suite_end_condition = pyosmo.end_conditions.Length(1)
    osmo.algorithm = pyosmo.algorithm.RandomAlgorithm()
    osmo.generate()
```

## Performance testing

When system behaviour is modelled in online models you can use [https://locust.io/](https://locust.io/)
to run multiple models parallel for stress test purposes. It may need 
