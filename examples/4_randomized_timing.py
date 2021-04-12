from pyosmo.osmo import Osmo
import random
import time


class PositiveCalculator:
    @staticmethod
    def guard_something():
        return True

    @staticmethod
    def step_something():
        print("1. inside step")

        # Random wait can be added inside test step
        wait_ms = random.randint(200, 1000)
        print("{} sleep inside step".format(wait_ms))
        time.sleep(wait_ms / 1000)

        print("2. inside step")

    @staticmethod
    def after():
        # Random wait can be added also between test steps
        wait_ms = random.randint(200, 3000)
        print('Waiting for: {}ms between steps'.format(wait_ms))
        time.sleep(wait_ms / 1000)


osmo = Osmo(PositiveCalculator())
osmo.generate()
