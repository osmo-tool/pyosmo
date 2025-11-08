class CalculatorSUT:
    def __init__(self):
        self.display = 0

    def plus(self, number):
        self.display += number

    def minus(self, number):
        self.display -= number
