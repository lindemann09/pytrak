from trakstar import TrakSTARInterface
from expyriment import control, stimuli, design, io
import time


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

init_time = time.time()

exp.keyboard.clear()
exp.clock.reset_stopwatch()
while key is None:
    cnt += 1
    data = trakstar.getSynchronousRecordDataDict(init_time)
    for sensor in sensors:
        output.add([data["time"], sensor, data[sensor][0],
                    data[sensor][1], data[sensor][2]])
    
    sample_rate = 1000 * cnt / float(exp.clock.stopwatch_time)
    if cnt % 30==0:
        stimuli.TextBox(text = "{0}\n{1}\n".format(cnt, sample_rate) +
                        TrakSTARInterface.data2string(data),
                        size = (400, 300), text_size=20).present()

    
    output.save()        
    key = exp.keyboard.check()
    
stimuli.TextLine(text="Closing trakSTAR").present()
trakstar.close()
control.end()


