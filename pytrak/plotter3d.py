import numpy as np

import settings
from pygame_plotter import Plotter


class Plotter3d(object):
    def __init__(self, attached_sensors):
        self.n_sensors = len(attached_sensors)
        row_colours = []
        for sensor in attached_sensors:
            row_colours.append(settings.colours[sensor])

        self.plotter_array = []
        self.plotter_array.append(Plotter(n_data_rows=self.n_sensors,
                                          data_row_colours=row_colours,
                                          width=settings.plotter_width,
                                          position=(0, 150),
                                          background_colour=settings.plotter_background_colour,
                                          axis_colour=settings.plotter_axis_colour))
        self.plotter_array.append(Plotter(n_data_rows=self.n_sensors,
                                          data_row_colours=row_colours,
                                          width=settings.plotter_width,
                                          position=(0, 0),
                                          background_colour=settings.plotter_background_colour,
                                          axis_colour=settings.plotter_axis_colour))
        self.plotter_array.append(Plotter(n_data_rows=self.n_sensors,
                                          data_row_colours=row_colours,
                                          width=settings.plotter_width,
                                          position=(0, -150),
                                          background_colour=settings.plotter_background_colour,
                                          axis_colour=settings.plotter_axis_colour))
        self._start_values = None
        self.scale = 1

    def update_values(self, data):
        mtx = np.array([data[1][0:3], data[2][0:3], data[3][0:3]]) * self.scale
        mtx = mtx.astype(int)
        if self._start_values is None:
            self._start_values = mtx
        else:
            mtx = mtx - self._start_values
            for s in range(self.n_sensors):
                self.plotter_array[s].update_values(mtx[:, s])
                self.plotter_array[s].present(update=False, clear=False)

            
