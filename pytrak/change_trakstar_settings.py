"""helper functions for changing Trakstar settings"""

from expyriment import stimuli, io

T_WAIT = 1500

def menu(exp):
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

def _invalid_value(exp):
    stimuli.TextLine(text="Invalid value!").present()
    exp.clock.wait(T_WAIT)

def manual(exp, i, trakstar_seetings):

    if i == 1:
        trakstar_seetings.measurement_rate = int(io.TextInput("Measurement rate (20 Hz < rate < 255 Hz):", length=3,
                                            ascii_filter=range(ord("0"), ord("9") + 1)).get())
        if trakstar_seetings.measurement_rate < 20 or trakstar_seetings.measurement_rate > 255:
            trakstar_seetings.measurement_rate = 80
            _invalid_value()
        else:
            stimuli.TextLine(text="Measurement rate set to {0} Hz.".format(trakstar_seetings.measurement_rate)).present()
            exp.clock.wait(T_WAIT)

    elif i == 2:
        trakstar_seetings.max_range = int(io.TextInput("Maximum range of transmitter (36, 72, 144 inches):", length=3,
                                     ascii_filter=range(ord("1"), ord("5")) + [ord("6"), ord("7")]).get())
        if trakstar_seetings.max_range not in [36, 72, 144]:
            trakstar_seetings.max_range = 36
            _invalid_value()
        else:
            stimuli.TextLine(text="Maximum range of transmitter set to {0} inches.".format(trakstar_seetings.max_range)).present()
            exp.clock.wait(T_WAIT)

    elif i == 3:
        trakstar_seetings.report_rate = int(io.TextInput("Report rate of the data (1 <= rate <= 127):", length=3,
                                       ascii_filter=range(ord("0"), ord("9") + 1)).get())
        if trakstar_seetings.report_rate < 1 or trakstar_seetings.report_rate > 127:
            trakstar_seetings.report_rate = 1
            _invalid_value()
        else:
            stimuli.TextLine(text="Report rate of incoming data set to {0}.".format(trakstar_seetings.report_rate)).present()
            exp.clock.wait(T_WAIT)

    elif i == 4:
        trakstar_seetings.power_line = int(io.TextInput("Power line frequency of the AC power source (50 or 60 Hz):",
                                      length=2, ascii_filter=[ord("0"), ord("5"), ord("6")]).get())
        if trakstar_seetings.power_line not in [50, 60]:
            trakstar_seetings.power_line = 60
            _invalid_value()
        else:
            stimuli.TextLine(
                text="Power line frequency of the AC power source set to {0} Hz.".format(trakstar_seetings.power_line)).present()
            exp.clock.wait(T_WAIT)

    elif i == 5:
        trakstar_seetings.metric = int(io.TextInput("Switch metric data reporting on/off (1/0):",
                                  length=1, ascii_filter=[ord("0"), ord("1")]).get())
        if trakstar_seetings.metric not in [0, 1]:
            trakstar_seetings.metric = True
            _invalid_value()
        else:
            stimuli.TextLine(text="Metric data reporting set to {0}.".format(trakstar_seetings.metric)).present()
            exp.clock.wait(T_WAIT)

    return trakstar_seetings


def remote(s, trakstar_seetings):
    """
    Input received via udp to change TrakSTAR system settings.
    Every string begins with a description of the value to be changed,
    followed by a colon, and the value to be set.

    e.g.: "measurement: 50", "metric: 0"
    """
    if s.lower().startswith("measurement"):
        _, measurement_rate = s.split(":")
        measurement_rate = int(measurement_rate.strip())
        if measurement_rate < 20 or measurement_rate > 255:
            measurement_rate = 80
        trakstar_seetings.measurement_rate = measurement_rate

    elif s.lower().startswith("maximum"):
        _, max_range = s.split(":")
        max_range = int(max_range.strip())
        if max_range not in [36, 72, 144]:
            max_range = 36
        trakstar_seetings.max_range = max_range

    elif s.lower().startswith("report"):
        _, report_rate = s.split(":")
        report_rate = int(report_rate.strip())
        if report_rate < 1 or report_rate > 127:
            report_rate = 1
        trakstar_seetings.report_rate = report_rate

    elif s.lower().startswith("power"):
        _, power_line = s.split(":")
        power_line = int(power_line.strip())
        if power_line not in [50, 60]:
            power_line = 60
        trakstar_seetings.power_line = power_line

    elif s.lower().startswith("metric"):
        _, metric = s.split(":")
        metric = int(metric.strip())
        if metric not in [0, 1]:
            metric = True
        trakstar_seetings.metric = metric

    return trakstar_seetings
