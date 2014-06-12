from trakstar import init_trakStar, getSynchronousRecordDataDict, close_trakStar, data_dict2string
from expyriment import control, stimuli, design


control.defaults.initialize_delay = 1
control.defaults.window_mode = True
control.defaults.fast_quit = True
control.defaults.open_gl = False
exp = design.Experiment()
exp.set_log_level(0)
control.initialize(exp)
control.end()

stimuli.TextLine(text="Initialize TrakSTAR").present()
sys_conf, attached_sensors = init_trakStar()

stimuli.TextLine(text="Press key to start recording").present()
exp.keyboard.wait()

key = None
cnt = 0
exp.keyboard.clear()
exp.clock.reset_stopwatch()
while key is None:
    cnt += 1
    data = getSynchronousRecordDataDict(attached_sensors)
    
    sample_rate = 1000 * cnt / float(exp.clock.stopwatch_time)
    if cnt % 30==0:
        stimuli.TextBox(text = "{0}\n{1}\n".format(cnt, sample_rate) + data_dict2string(data),
                        size = (400, 300), text_size=20).present()
    key = exp.keyboard.check()
    
stimuli.TextLine(text="Closing trakSTAR").present()
close_trakStar()
control.end()

    
#def make_dots(
