"""Sensor History with moving average filtering and distance, velocity"""

import numpy as np

class SensorHistory():
    """The Sensory History keeps track of the last n recorded sample and
    calculates online the moving average (running mean).

    SensorHistory.moving_average

    """

    def __init__(self, history_size, number_of_parameter):

        self.history = np.zeros((history_size, number_of_parameter),
                                dtype=np.float32)
        self.moving_average = np.zeros(number_of_parameter, dtype=np.float32)

        self._correction_cnt = 0
        self._previous_moving_average = self.moving_average

    def __str__(self):
        return str(self.history)

    def update(self, values):
        """Update history and calculate moving average

        (correct for accumulated rounding errors ever 10000 samples)

        Parameter
        ---------
        values : list of values for all sensor parameters

        """

        self._previous_moving_average = self.moving_average
        pop = self.history[0,:]
        sample = np.array(values)
        self.history = np.vstack([self.history, sample])[1:,:] # append and remove first
        # pop first element and calc moving average
        if self._correction_cnt > 10000:
            self._correction_cnt = 0
            self.moving_average = self.calc_history_average()
        else:
            self._correction_cnt += 1
            self.moving_average = self.moving_average + \
                            ( (sample - pop) / len(self.history) )


    def calc_history_average(self):
        """Calculate history averages for all sensor parameter.

        The method is more time consuming than calling the property
        `moving_average`. It is does however not suffer from accumulated
        rounding-errors such as moving average.

        """

        return np.mean(self.history, axis=0)

    def distance_to_point(self, point):
        """returns current Euclidean distance to a point in space, based on
        filtered data (moving average)

        Note
        ----
        point has to match in the number of dimensions
        """

        return np.sqrt(np.sum( (self.moving_average - np.array(point)) ** 2))

    @property
    def history_size(self):
        return len(self.history)

    @property
    def number_of_parameter(self):
        return len(self.history[0])

    @property
    def replacement(self):
        """returns the current replacement based on filtered data"""
        return self.moving_average - self._previous_moving_average

    def velocity(self, sampling_rate):
        """returns the current velocity based on filtered data"""
        return self.distance_to_point(self._previous_moving_average) * sampling_rate


if __name__ == "__main__":
    import random
    print "go"
    sh = SensorHistory(history_size=5, number_of_parameter=3)
    for x in range(19908):
        x = [random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)]
        sh.update(x)

    print sh.moving_average, sh.calc_history_average()
    print sh.velocity(100)
