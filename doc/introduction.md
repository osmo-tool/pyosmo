
# Towards randomized tests

## 1. Start from simple example static test case
```
# Send and receive data
output = system_under_testing(2)
assert output == 4
```


## 2. Randomize input

Instead of sending static number send random value between 1 and 1000. This improve test coverage a lot:
```
input = random.randint(1, 10000)
output = system_under_testing(input)
```
But how to assert output value because there is no simple input output pair?

1. Check that output is right format
```
    # Check that output is integer
    try:
        int(output)
    except:
        raise Exception("Data is not integer: {}".format(output))
```

2. If logic is known we can write algorithm to check it. For example here we know that response is two times bigger
than input

```
assert output == (2 * input)
```

3. Sometimes logic is so complex that it is good if system responses something in time limit.
This approach is used much in fuzz testing

## 3. Randomize logic

The core of model-based testing is to randomize order and amount of test steps. 

Example of normal test case:
```
c = Calculator()
c.add(10)
c.minus(1)
c.minus(1)
assert c.result() == 8
```
To make able to cover significant part of that Calculator means a painful amount of test cases to be implemented
manually. In case of model-based testing the logic is replaced with model:

```
class PositiveCalculator:
    def __init__(calculatorInterface):
        // Reference number
        count = 0
        // Calculator interface instance
        calculator = calculatorInterface

    def guard_add(self):
        // add is always possible step
        return True

    def step_add(self):
        // Take random number
        add_num = random.randint(1, 1000)

        // Update referance number
        self.count += add_num

        // Add number to calculator 
        calculator.add(add_num)
        
        // Check that calculator output and reference number match
        assert calculator.output() == self.count

    def guard_minus(self):
        return True

    def step_minus(self):
        minus_num = random.randint(1, self.__count)
        self.count -= minus_num
        calculator.minus(minus_num)
        assert calculator.output() == self.count
```

With that model osmo can generate infinite long test cases. Running that for couple of hours can get coverage
that cannot be reach with days of manual writing. And additional that is easy to rerun after some changes in the model.


## 4. Randomize timing

In real world things doesn't normally happen with same timing. With randomized timing the model can be much more 
real life use case.

```
class PositiveCalculator:
    def guard_something(self):
        return True

    def step_something(self):
        print("1. inside step")

        # Random wait can be added inside test step
        wait_ms = random.randint(200, 1000)
        print("{} sleep inside step".format(wait_ms))
        time.sleep(wait_ms / 1000)

        print("2. inside step")

    def after(self):
        # Random wait can be added also between test steps
        wait_ms = random.randint(200, 3000)
        print('Waiting for: {}ms between steps'.format(wait_ms))
        time.sleep(wait_ms / 1000)
        print('')
```
See whole example in [4_randomized_timing.py](../examples/4_randomized_timing.py)

## Summary

When randomizing input, logic and timing the test case coverage is going better during the time.

Optimal is that randomization is close to real life randomization range. Then testing can catch similar problems thatn real life usage.
