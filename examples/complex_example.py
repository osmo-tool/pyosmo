"""
Complex model with two actors.
"""

import random
from dataclasses import dataclass

from pyosmo.osmo import Osmo


@dataclass
class Person:
    name: str
    money: int = 10

    def give_money(self, preferred_amount, to_whom):
        n = min(self.money, preferred_amount)
        self.money -= n
        to_whom.receive_money(n)
        return n

    def receive_money(self, amount):
        self.money += amount


def give(giver, receiver):
    amount = giver.give_money(random.randint(1, 5), receiver)
    print(f'- {giver} gave {amount} to {receiver}')


class ExampleModel:
    def __init__(self):
        print('Starting')

    def before_test(self):
        self.person1 = Person('Jack')
        self.person2 = Person('Jill')

    def guard_person1_gives_to_person2(self):
        return self.person1.money > 0

    def step_person1_gives_to_person2(self):
        give(self.person1, self.person2)

    def guard_person2_gives_to_person1(self):
        return self.person2.money > 0

    def step_person2_gives_to_person1(self):
        give(self.person2, self.person1)

    def after_test(self):
        print(f'Situation in the end:\n  {self.person1}\n  {self.person2}')


if __name__ == '__main__':
    # Initialize Osmo with model
    osmo = Osmo(ExampleModel())
    # Generate tests
    osmo.generate()
