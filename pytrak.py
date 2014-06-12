from trakstar import TrakSTARInterface
from expyriment import control, stimuli, design


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
exp.keyboard.clear()
exp.clock.reset_stopwatch()
while key is None:
    cnt += 1
    data = trakstar.getSynchronousRecordDataDict()
    
    sample_rate = 1000 * cnt / float(exp.clock.stopwatch_time)
    if cnt % 30==0:
        stimuli.TextBox(text = "{0}\n{1}\n".format(cnt, sample_rate) +
                        TrakSTARInterface.data2string(data),
                        size = (400, 300), text_size=20).present()
    key = exp.keyboard.check()
    
stimuli.TextLine(text="Closing trakSTAR").present()
trakstar.close()
control.end()

    
#def make_dots(
