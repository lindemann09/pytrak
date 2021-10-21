""" Settings module for pytrak

    reads and save settings automatically
"""

import atexit
import configparser
from expyriment import stimuli, misc, io

#####
#  overwritten by existing config file
measurement_rate = 80
max_range = 36
report_rate = 1
power_line = 60
metric = True
#####

cfg_filename = "pytrak.cfg"
cfg_section = 'TrakStar'

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
    set_marker, set_reference_position = list(range(7))

colours = {1: misc.constants.C_RED,
           2: misc.constants.C_GREEN,
           3: misc.constants.C_YELLOW,
           4: misc.constants.C_BLUE}

t_wait = 1500

def save():
    config = configparser.RawConfigParser()
    config.add_section(cfg_section)
    config.set(cfg_section, "measurement_rate", measurement_rate)
    config.set(cfg_section, "max_range", max_range)
    config.set(cfg_section, "report_rate", report_rate)
    config.set(cfg_section, "power_line", power_line)
    config.set(cfg_section, "metric", metric)
    with open(cfg_filename, 'wb') as configfile:
        config.write(configfile)


def read():
    global measurement_rate, max_range
    global report_rate, power_line, metric, circle_diameter

    config = configparser.ConfigParser()
    try:
        config.read(cfg_filename)
        measurement_rate = config.getint(cfg_section, 'measurement_rate')
        max_range = config.getint(cfg_section, 'max_range')
        report_rate = config.getint(cfg_section, 'report_rate')
        power_line = config.getint(cfg_section, 'power_line')
        metric = config.getboolean(cfg_section, 'metric')
    except:
        print("Creating settings file: ", cfg_filename)
        save()
        return False
    return True

def reording_settings_info_screen():

    stimuli.TextBox()

def get_menu(exp):
    return stimuli.TextScreen("Settings:",
                              "1: Measurement rate\n" +
                              "2: Maximum range of transmitter\n" +
                              "3: Report rate of data\n" +
                              "4: Power line frequency\n" +
                              "5: Metric data reporting\n\n" +
                              "q: Quit settings",
                              text_justification=0,
                              size=[exp.screen.size[0] / 4,
                                    exp.screen.size[1] / 2])

def invalid_value(exp):
    stimuli.TextLine(text="Invalid value!").present()
    exp.clock.wait(t_wait)

def get_input(exp, i):
    global measurement_rate, max_range, report_rate, power_line, metric
    if i == 1:
        measurement_rate = int(io.TextInput("Measurement rate (20 Hz < rate < 255 Hz):", length=3,
                                            ascii_filter=list(range(ord("0"), ord("9") + 1))).get())
        if measurement_rate < 20 or measurement_rate > 255:
            measurement_rate = 80
            invalid_value()
        else:
            stimuli.TextLine(text="Measurement rate set to {0} Hz.".format(measurement_rate)).present()
            exp.clock.wait(t_wait)
        return
    elif i == 2:
        max_range = int(io.TextInput("Maximum range of transmitter (36, 72, 144 inches):", length=3,
                                     ascii_filter=list(range(ord("1"), ord("5"))) + [ord("6"), ord("7")]).get())
        if max_range not in [36, 72, 144]:
            max_range = 36
            invalid_value()
        else:
            stimuli.TextLine(text="Maximum range of transmitter set to {0} inches.".format(max_range)).present()
            exp.clock.wait(t_wait)
        return
    elif i == 3:
        report_rate = int(io.TextInput("Report rate of the data (1 <= rate <= 127):", length=3,
                                       ascii_filter=list(range(ord("0"), ord("9") + 1))).get())
        if report_rate < 1 or report_rate > 127:
            report_rate = 1
            invalid_value()
        else:
            stimuli.TextLine(text="Report rate of incoming data set to {0}.".format(report_rate)).present()
            exp.clock.wait(t_wait)
        return
    elif i == 4:
        power_line = int(io.TextInput("Power line frequency of the AC power source (50 or 60 Hz):",
                                      length=2, ascii_filter=[ord("0"), ord("5"), ord("6")]).get())
        if power_line not in [50, 60]:
            power_line = 60
            invalid_value()
        else:
            stimuli.TextLine(
                text="Power line frequency of the AC power source set to {0} Hz.".format(power_line)).present()
            exp.clock.wait(t_wait)
        return
    elif i == 5:
        metric = int(io.TextInput("Switch metric data reporting on/off (1/0):",
                                  length=1, ascii_filter=[ord("0"), ord("1")]).get())
        if metric not in [0, 1]:
            metric = True
            invalid_value()
        else:
            stimuli.TextLine(text="Metric data reporting set to {0}.".format(metric)).present()
            exp.clock.wait(t_wait)
        return


def process_udp_input(s):
    """
    Input received via udp to change TrakSTAR system settings.
    Every string begins with a description of the value to be changed,
    followed by a colon, and the value to be set.

    e.g.: "measurement: 50", "metric: 0"
    """
    global filename, measurement_rate, max_range, report_rate, power_line, metric
    if s.lower().startswith("filename"):
        _, filename = s.split(":")
        filename = filename.strip()
        return
    elif s.lower().startswith("measurement"):
        _, measurement_rate = s.split(":")
        measurement_rate = int(measurement_rate.strip())
        if measurement_rate < 20 or measurement_rate > 255:
            measurement_rate = 80
        return
    elif s.lower().startswith("maximum"):
        _, max_range = s.split(":")
        max_range = int(max_range.strip())
        if max_range not in [36, 72, 144]:
            max_range = 36
        return
    elif s.lower().startswith("report"):
        _, report_rate = s.split(":")
        report_rate = int(report_rate.strip())
        if report_rate < 1 or report_rate > 127:
            report_rate = 1
        return
    elif s.lower().startswith("power"):
        _, power_line = s.split(":")
        power_line = int(power_line.strip())
        if power_line not in [50, 60]:
            power_line = 60
        return
    elif s.lower().startswith("metric"):
        _, metric = s.split(":")
        metric = int(metric.strip())
        if metric not in [0, 1]:
            metric = True
        return

###
atexit.register(save)
read()
###
