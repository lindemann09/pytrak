import numpy as np
import expyriment, pygame
from expyriment import control, stimuli, misc, io
from pygame_plotter import Plotter


control.set_develop_mode(True)
control.defaults.open_gl = False
exp = control.initialize()


c = stimuli.Canvas(size=(34,34))
pl = Plotter(n_data_rows = 2, data_row_colours =[ (255,0,0), (0, 255, 0)],
        width=500,
        background_colour=(0,0,0),
        axis_colour = (100,100,100))

x = 0
marker = False
while True:
    key = exp.keyboard.check()
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
    y2 = int(np.sin(x/10.0) * np.cos(x/40.0) * 90)

    t = stimuli.TextLine(str(x), position=(0, 150))
    exp.clock.reset_stopwatch()
    pl.update_values((y, y2), set_marker=marker)
    #print exp.clock.stopwatch_time
    #plot    t.present(update=False, clear=True)
    pl.present(update=False, clear=False)
    exp.screen.update_stimuli([t, pl])

    exp.clock.wait(5)

control.end()

