"""Sensor History with moving average filtering and replacement methods"""

__author__ = 'Oliver Lindemann <oliver.lindemann@cognitive-psychology.eu>,\
Raphael Wallroth <>'
__version__ = 0.2

import math

def euclidian_distance(a, b):
    """calculates euclidian distance between a and b"""
    return math.sqrt(sum( map(lambda x:(x[1]-x[0])**2, zip(a, b)) ))

class SensorHistory():
    """The Sensory History keeps track of the last n recorded sample and
    calculates online the moving average (running mean).
    """

    def __init__(self, history_size, number_of_sensors):
        self.history = [[0] * number_of_sensors] * history_size
        self._moving_average = [0] * number_of_sensors
        self._correction_cnt = 0

    def __str__(self):
        return str(self.history)

    def update(self, values):
        """Update history and calculate moving average

        (correct for accumulated rounding errors ever 10000 samples)

        Parameter
        ---------
        values : list of values for all sensor parameters

        """

        pop = self.history.pop(0)
        self.history.append(values)
        # pop first element and calc moving average
        if self._correction_cnt > 10000:
            self._correction_cnt = 0
            self._moving_average = self.calc_history_average()
        else:
            self._correction_cnt += 1
            self._moving_average = map(
                lambda x:x[0] + (float(x[1]-x[2])/len(self.history)),
                        zip(self._moving_average, values, pop))


    def calc_history_average(self):
        """Calculate history averages for all sensor parameter.

        The method is more time consuming than calling the property
        `moving_average`. It is does however not suffer from accumulated
        rounding-errors such as moving average.

        """

        s = [float(0)] * self.number_of_sensors
        for t in self.history:
            s = map(lambda x:x[0]+x[1], zip(s, t))
        return map(lambda x:x/len(self.history), s)

    @property
    def history_size(self):
        return len(self.history)

    @property
    def number_of_sensors(self):
        return len(self.history[0])

    @property
    def moving_average(self):
        return self._moving_average

    @property
    def replacement(self):
        """returns the last replacement"""
        return map(lambda x:x[0]-x[1], zip(self.history[-1], self.history[-2]))

    @property
    def replacement_distance(self):
        """ returns the euclidian distance of the last replacement"""
        return euclidian_distance(self.history[-1], self.history[-2])

if __name__ == "__main__":
    import random

    sh = SensorHistory(history_size=5, number_of_sensors=3)
    for x in range(19908):
        x = [random.randint(0,100),random.randint(0,100), random.randint(0,100)]
        sh.update(x)

    print sh.moving_average, sh.calc_history_average()
