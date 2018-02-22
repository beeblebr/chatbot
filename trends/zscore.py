import time
import random
from math import sqrt


class zscore:
    """
        Just pass the history count list and the current count for a topic (per hour) and 
        get a z score. You can choose to use additional functions like update and stuff,
        if you dont want to redo some operations that span the entire history list
        """

    def __init__(self, history=[]):
        self.history = history
        self.history_count = float(len(history))
        self.total = sum(history)
        self.sqrTotal = sum(x ** 2 for x in history)

    def update(self, value):
        self.history_count += 1.0
        self.total += value
        self.sqrTotal += value ** 2

    def avg(self):
        return self.total / self.history_count

    def std(self):
        return sqrt((self.sqrTotal / self.history_count) - self.avg() ** 2)

    def score(self, obs):
        return (obs - self.avg()) / self.std()
