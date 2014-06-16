from trakstar import TrakSTARInterface, SensorHistory
from expyriment import control, stimuli, design, io, misc


control.defaults.initialize_delay = 0
control.defaults.window_mode = True
control.defaults.fast_quit = True
control.defaults.open_gl = False
control.defaults.log_level = 0
exp = design.Experiment()
control.initialize(exp)

trakstar = TrakSTARInterface()
stimuli.TextLine(text="Initialize TrakSTAR").present()
trakstar.initialize()
stimuli.TextLine(text="Press key to start recording").present()
exp.keyboard.wait()

key = None
cnt = 0

sensors = trakstar.attached_sensors
output = io.DataFile("trakStar_data")
write_angle = False
write_quality = False
if not write_angle and not write_quality:
    output.add_variable_names(["time", "sensor", "x", "y", "z"])
#elif ... 

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

exp.keyboard.clear()
exp.clock.reset_stopwatch()
while key is None:
    cnt += 1
    data = trakstar.getSynchronousRecordDataDict()
    output.add(TrakSTARInterface.data2string(data))
    for sensor in sensors:
        history[sensor].update(data[sensor])
        circles[sensor].position = (int(round(data[sensor][1]*10)),
                                    int(round(data[sensor][0]*10)))
    canvas.clear_surface()
    sample_rate = 1000 * cnt / float(exp.clock.stopwatch_time)
    if cnt % 30==1:
        txt_box = stimuli.TextBox(text = "{0}\n{1}\n".format(cnt, sample_rate) +
                        TrakSTARInterface.data2string(data),
                        size = (400, 300), text_size=20)
    for circle in circles.values():
        circle.plot(canvas)
    txt_box.plot(canvas)
    canvas.present()
                
    output.save()        
    key = exp.keyboard.check()
    
stimuli.TextLine(text="Closing trakSTAR").present()
trakstar.close()
control.end()


