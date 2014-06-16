from trakstar import TrakSTARInterface, SensorHistory
from expyriment import control, stimuli, design, io, misc

__author__ = 'Raphael Wallroth <>, \
Oliver Lindemann <oliver.lindemann@cognitive-psychology.eu>'
__version__ = '0.1.2'



control.defaults.initialize_delay = 0
control.defaults.window_mode = True
control.defaults.fast_quit = True
control.defaults.open_gl = False
control.defaults.event_logging = 0
exp = design.Experiment()
exp.set_log_level(0)
control.initialize(exp)

trakstar = TrakSTARInterface()
stimuli.TextLine(text="Initialize TrakSTAR").present()
trakstar.initialize()
stimuli.TextLine(text="Press key to start recording").present()
exp.keyboard.wait()

key = None
cnt = 0

sensors = trakstar.attached_sensors
write_angle = False
write_quality = False

colours = { 0: misc.constants.C_RED,
            1: misc.constants.C_GREEN,
            2: misc.constants.C_YELLOW,
            3: misc.constants.C_BLUE }
circle_diameter = 40
circles = {}
canvas = stimuli.BlankScreen()
for sensor in sensors:
    circles[sensor] = stimuli.Circle(circle_diameter, colour=colours[sensor])
    stimuli.TextLine(str(sensor+1), text_size=circle_diameter/2, text_bold=True,
                     text_colour=misc.constants.C_WHITE).plot(circles[sensor])

history = {}
for sensor in sensors:
    history[sensor] = SensorHistory(history_size=5, number_of_parameter=3)

trakstar.open_data_file(filename="test_recording", directory="data",
                      suffix = ".csv", time_stamp_filename=True,
                       write_angles=False, write_quality=True)
exp.keyboard.clear()
exp.clock.reset_stopwatch()
while key is None:
    cnt += 1
    data = trakstar.getSynchronousRecordDataDict()
    for sensor in sensors:
        history[sensor].update(data[sensor][:3])

    if cnt % 30 == 1:
        for sensor in sensors:
            circles[sensor].position = (int(round(history[sensor].moving_average[1]*10)),
                                        int(round(history[sensor].moving_average[0]*10)))
        canvas.clear_surface()
        sample_rate = 1000 * cnt / float(exp.clock.stopwatch_time)
        txt_box = stimuli.TextBox(text = "{1}\n".format(cnt, sample_rate) +
                        TrakSTARInterface.data2string(data, times=False),
                        text_justification = 0,
                        size = (400, 300), text_size=20)
        for circle in circles.values():
            circle.plot(canvas)
        txt_box.plot(canvas)
        canvas.present()
        
    key = exp.keyboard.check()
    
trakstar.close_data_file()
trakstar.close()
stimuli.TextLine(text="Closing trakSTAR").present()
control.end()


