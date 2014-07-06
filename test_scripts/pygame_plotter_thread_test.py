import numpy as np
from expyriment import control, stimuli, misc
from pygame_plotter import PlotterThread


control.set_develop_mode(True)
control.defaults.open_gl = False
exp = control.initialize()


#self._plot_request.set() # plot not set

c = stimuli.Canvas(size=(34,34))
#pl = Plotter(n_data_rows = 2, data_row_colours =[ (255,0,0), (0, 255, 0)],
#        width=500,
#        background_colour=(0,0,0),
#        axis_colour = (100,100,100))

pl_thread = PlotterThread(exp, refesh_time = 0.02)
#pl = Plotter(n_data_rows = 1, data_row_colours =[ (0, 255, 0)])
x = 0
marker = False
pl_thread.start()

while True:
    key = exp.keyboard.check(check_for_control_keys=False)
    if key == misc.constants.K_UP:
        x += 10
    elif key == misc.constants.K_DOWN:
        x -=10
    if key == ord("m"):
        marker = True
    else:
        marker = False
    if key == misc.constants.K_q:
        break

    x += 1
    y = int(np.sin(x/15.0) * 90)
    y2 = int(np.sin(x/1000.0) * np.cos(x/40.0) * 90)

    #t = stimuli.TextLine(str(x), position=(0, 150))
    exp.clock.reset_stopwatch()
    pl_thread.new_values((y,y2), marker)
    if exp.clock.stopwatch_time >= 1:
        pass
#print exp.clock.stopwatch_time
    exp.clock.wait(1)

print "end"
pl_thread.stop()
control.end()

