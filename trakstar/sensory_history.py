"""Sensor History with moving average filtering and velocity"""

__author__ = 'Oliver Lindemann <oliver.lindemann@cognitive-psychology.eu>,\
Raphael Wallroth <>'
__version__ = 0.1

import numpy as np

class SensorHistory():
    """The Sensory History keeps track of the last n recorded sample and
    calculates online the moving average (running mean).
    """

    DataType = np.float64

    def __init__(self, history_size, number_of_sensors):
        self.history = np.zeros((history_size, number_of_sensors))
        self._moving_average = 0
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

        values = np.array(values, dtype=SensorHistory.DataType)
        pop = self.history[0,:]
        self.history = np.vstack([self.history, values])[1:, :]

        # pop first element and calc moving average
        if self._correction_cnt > 10000:
            self._correction_cnt = 0
            self._moving_average = self.calc_history_average()
        else:
            self._moving_average = self._moving_average + \
            values / self.history.shape[0] - pop / self.history.shape[0]
            self._correction_cnt += 1

    def calc_history_average(self):
        """Calculate history averages for all sensor parameter.

        The method is more time consuming than calling the property
        `moving_average`. It is does however not suffer from accumulated
        rounding-errors such as moving average.

        """

        return np.mean(self.history, axis=0, dtype=SensorHistory.DataType)

    @property
    def history_size(self):
        return self.history.shape[0]

    @property
    def number_of_sensors(self):
        return self.history.shape[1]

    @property
    def moving_average(self):
        return self._moving_average

    @property
    def velocity(self):
        """ returns the current velocity"""
        return self.history[-1,:] - self.history[-2,:]



if __name__ == "__main__":
    import random
    sh = SensorHistory(history_size=5, number_of_sensors=3)

    for x in range(19908):
        sh.update([random.random(),random.random(),random.random()])

    print sh
    print sh.moving_average, sh.calc_history_average()
