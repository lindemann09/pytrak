import numpy as np
import pygame

from . import settings
from .plotter import PlotterThread, lock_expyriment


class PlotterXYZ(object):
    def __init__(self, attached_sensors, expyriment_screen_size, refresh_time):
        self.refresh_time = refresh_time
        self.attached_sensors = attached_sensors
        row_colours = []
        for sensor in attached_sensors:
            row_colours.append(settings.colours[sensor])

        self.plotter_array = []
        self._update_rects = []
        h = settings.plotter_height
        for position in [(0, h+5), (0, 0), (0, -(h+5))]:
            plotter_thread = PlotterThread(
                        n_data_rows=len(self.attached_sensors),
                        data_row_colours=row_colours,
                        y_range=(-h/2, h/2),
                        width=settings.plotter_width,
                        position=position,
                        background_colour=settings.plotter_background_colour,
                        axis_colour=settings.plotter_axis_colour)
            self.plotter_array.append(plotter_thread)
            self._update_rects.append(plotter_thread.get_plotter_rect(
                                    expyriment_screen_size))

        self._start_values = None
        self.scaling = settings.plotter_scaling

    @property
    def update_rects(self):
        return self._update_rects

    def reset_start_values(self):
        self._start_values = None

    def add_values(self, data, set_marker=False):
        mtx = []
        for x in self.attached_sensors:
            mtx.append(data[x][0:3])
        mtx = np.array(mtx, dtype=int) * self.scaling
        if self._start_values is None:
            self._start_values = mtx
        else:
            mtx = mtx - self._start_values
            for s in range(3):
                self.plotter_array[s].add_values(mtx[:, s],
                                    set_marker = set_marker)

    def start(self):
        """plotter threads"""
        for plotter in self.plotter_array:
            plotter.start()

    def stop(self):
        """stop plotter threads"""
        for plotter in self.plotter_array:
            plotter.stop()

    def update(self):
        lock_expyriment.acquire()
        pygame.display.update(self.update_rects)
        lock_expyriment.release()
