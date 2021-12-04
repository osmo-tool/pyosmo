import random
import time


class RandomDelayModel:
    """
    This model cause random delay after each test step between min and max value
    """

    def __init__(self, min_delay, max_delay):
        """
        :param min_delay: minimum delay in seconds
        :param max_delay: maximum delay in seconds
        """
        self.min = min_delay
        self.max = max_delay

    def after(self):
        delay = random.uniform(self.min, self.max)
        print(f'Sleeping {delay}')
        time.sleep(delay)
