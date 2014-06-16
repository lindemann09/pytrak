"""Sensor History with moving average filtering"""

__author__ = 'Oliver Lindemann <oliver.lindemann@cognitive-psychology.eu>,\
Raphael Wallroth <>'
__version__ = 0.1

class SensorHistory():
    """The Sensory History keeps track of the last n recorded sample and
    calculates online the moving average (running mean).
    """

    def __init__(self, history_size):
        self.history = [0] * history_size
        self._history_size = history_size
        self._moving_average = 0
        self._correction_cnt = 0

    def update(self, value):
        """Update history and calculate moving average

        (correct for accumulated rounding errors ever 10000 samples)
        """

        self.history.append(value)
        # pop first element and calc moving average
        if self._correction_cnt > 10000:
            self._correction_cnt = 0
        else:
            self._moving_average = self._moving_average + \
            (float(value) / self._history_size) - \
            (float(self.history.pop(0)) / self.history_size)
            self._correction_cnt += 1


    def calc_history_average(self):
        """Calculate history average.

        The method is more time consuming than calling the property
        `history_average`. It is does however not suffer from accumulated
        rounding-errors such as moving average.

        """

        return sum(self.history) / float(len(self.history))

    @property
    def history_size(self):
        return self._history_size

    @property
    def moving_average(self):
        return self._moving_average

if __name__ == "__main__":
    import random
    sh = SensorHistory(5)

    for x in range(9999):
        r = random.random()
        sh.update(r)

print sh.moving_average, sh.calc_history_average()
