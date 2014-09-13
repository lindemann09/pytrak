""" Settings module for pytrak
"""

from expyriment import misc

plotter_width = 1000
plotter_background_colour = (10, 10, 10)
plotter_axis_colour = (100, 100, 100)
plotter_height = 180
plotter_scaling = 0.3

data_dir = "data"
data_suffix = ".csv"
data_time_stamps = False
data_write_angles = False
data_write_cpu_time = False
data_write_quality = True
####

class Command:
    quit, toggle_pause, increase_scaling, decrease_scaling, normalize_plotting,\
    set_marker = range(6)

colours = {1: misc.constants.C_RED,
           2: misc.constants.C_GREEN,
           3: misc.constants.C_YELLOW,
           4: misc.constants.C_BLUE}

