import random
import time

from pyosmo.osmo import Osmo


class PositiveCalculator:
    @staticmethod
    def guard_something():
        return True

    @staticmethod
    def step_something():
        print('1. inside step')

        # Random wait can be added inside test step
        wait_ms = random.randint(200, 1000)
        print(f'{wait_ms} sleep inside step')
        time.sleep(wait_ms / 1000)

        print('2. inside step')

    @staticmethod
    def after():
        # Random wait can be added also between test steps
        wait_ms = random.randint(200, 3000)
        print(f'Waiting for: {wait_ms}ms between steps')
        time.sleep(wait_ms / 1000)


if __name__ == '__main__':
    osmo = Osmo(PositiveCalculator())
    osmo.generate()
