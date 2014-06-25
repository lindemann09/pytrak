from trakstar import TrakSTARInterface, SensorHistory
from expyriment import control, stimuli, design, io, misc

__author__ = 'Raphael Wallroth <>, \
Oliver Lindemann <oliver.lindemann@cognitive-psychology.eu>'
__version__ = '0.1.2'


trakstar = TrakSTARInterface()
print "Initialize TrakSTAR"
trakstar.initialize()
trakstar.set_system_configuration(measurement_rate=50,
                                    max_range=72,
                                    print_configuration = True)

#expyriment
control.defaults.initialize_delay = 0
control.defaults.window_mode = True
control.defaults.fast_quit = True
control.defaults.open_gl = False
control.defaults.event_logging = 0
exp = design.Experiment()
exp.set_log_level(0)
control.initialize(exp)
<<<<<<< HEAD


trakstar = TrakSTARInterface()
stimuli.TextLine(text="Initialize TrakSTAR").present()
trakstar.initialize()
trakstar.set_system_configuration(sampling_rate=50,
                                    max_range=72,
                                    print_configuration = True)
=======
>>>>>>> master
stimuli.TextLine(text="Press key to start recording").present()
exp.keyboard.wait()

# make circles and history
colours = { 0: misc.constants.C_RED,
            1: misc.constants.C_GREEN,
            2: misc.constants.C_YELLOW,
            3: misc.constants.C_BLUE }
circle_diameter = 40
circles = {}
history = {}
for sensor in trakstar.attached_sensors:
    circles[sensor] = stimuli.Circle(circle_diameter, colour=colours[sensor])
    stimuli.TextLine(str(sensor+1), text_size=circle_diameter/2, text_bold=True,
                     text_colour=misc.constants.C_WHITE).plot(circles[sensor])
    history[sensor] = SensorHistory(history_size=5, number_of_parameter=3)


def update_screen(trakstar, circles, history):
    for sensor in trakstar.attached_sensors:
        if not trakstar.system_configuration.metric:
            circles[sensor].position = (
                    int(round(history[sensor].moving_average[1]*10)),
                    int(round(history[sensor].moving_average[0]*10)))
        else:
            circles[sensor].position = (history[sensor].moving_average[1]/2,
                                        history[sensor].moving_average[0]/2)

    canvas = stimuli.BlankScreen()
    sample_rate = 1000 * cnt / float(exp.clock.stopwatch_time)
    txt_box = stimuli.TextBox(text = "{1}\n".format(cnt, sample_rate) +
                    TrakSTARInterface.data2string(data, times=False),
                    text_justification = 0,
                    size = (400, 300), text_size=20)
    for circle in circles.values():
        circle.plot(canvas)
    txt_box.plot(canvas)
    canvas.present()


trakstar.open_data_file(filename="test_recording", directory="data",
                      suffix = ".csv", time_stamp_filename=True,
                       write_angles=False, write_quality=True)

#wait for connection
while not trakstar.udp.is_connected:
    trakstar.udp.poll()

key = None
cnt = 0
exp.keyboard.clear()
exp.clock.reset_stopwatch()

udp.clear_input_buffer()
while key is None:
    cnt += 1
    data = trakstar.get_synchronous_data_dict()

    for sensor in trakstar.attached_sensors:
        history[sensor].update(data[sensor][:3])

    if cnt % 30 == 1:
        update_screen(trakstar, circles, history)
    key = exp.keyboard.check()

trakstar.close_data_file()
trakstar.close()
stimuli.TextLine(text="Closing trakSTAR").present()
control.end()
