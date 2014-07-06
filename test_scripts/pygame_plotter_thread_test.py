import threading
import numpy as np
from expyriment import control, stimuli, misc
from pygame_plotter import PlotterThread
from lock_expyriment import lock_expyriment
import time

control.set_develop_mode(True)
control.defaults.open_gl = False # Does not work in opengl mode
control.defaults.event_logging = 0
exp = control.initialize()

class DisplayThread(threading.Thread):
    def __init__(self, exp):
        super(DisplayThread, self).__init__()
        self._exp = exp
        self._stop_request = threading.Event()
        self._update_request = threading.Event()
        self._present_stimuli = []
        self._update_stimuli = []
        self._lock = threading.Lock()
        self._background= stimuli.BlankScreen() #TODO: make backgrund property
        self.clear()

    def add_present_stimuli(self, stimulus_array):
        """Set stimuli presented with next update"""
        if type(stimulus_array) is not list:
            stimulus_array = [stimulus_array]
        self._lock.acquire()
        for stim in stimulus_array:
            self._present_stimuli.append(stim.copy())
        self._lock.release()

    def add_update_stimuli(self, stimulus_array):
        """Set stimuli updated with next update"""
        if type(stimulus_array) is not list:
            stimulus_array = [stimulus_array]
        self._lock.acquire()
        for stim in stimulus_array:
            self._update_stimuli.append(stim.copy())
        self._lock.release()

    def stop(self):
        self.join(timeout=1000)

    def join(self, timeout=None):
        self._stop_request.set()
        super(DisplayThread, self).join(timeout)

    def update_request(self, wait_till_updated=False):
        self._update_request.set()
        if wait_till_updated:
            while not self.is_updated():
                self._update_request.set()

    def is_updated(self):
        self._lock.acquire()
        if len(self._update_stimuli) >0 or \
            len(self._present_stimuli) >0:
            rtn = False
        else:
            rtn = True
        self._lock.release()
        return rtn

    def clear(self):
        self._lock.acquire()
        self._present_stimuli = []
        self._update_stimuli = []
        self._lock.release()
        self.add_present_stimuli([self._background])

    def run(self):
        self._update_request.set()
        while not self._stop_request.is_set():
            if self._update_request.wait(timeout=0.1):
                self._lock.acquire()
                present_stimuli = self._present_stimuli
                update_stimuli = self._update_stimuli
                self._present_stimuli = []
                self._update_stimul = []
                self._lock.release()

                #expyriment plotting
                lock_expyriment.acquire()
                if len(present_stimuli) > 0:
                    for elem in present_stimuli:
                        elem.preload()
                        stimuli.Canvas(size = elem.surface_size,
                            position=elem.position, colour = \
                            self._background.colour).present(
                            clear=False, update=False)
                        elem.present(clear=False, update=False)
                        elem.unload()
                    update_stimuli = present_stimuli + update_stimuli
                if  len(update_stimuli) > 0:
                    self._exp.screen.update_stimuli(update_stimuli)

                self._update_request.clear()
                lock_expyriment.release()

#self._plot_request.set() # plot not set

c = stimuli.Canvas(size=(34,34))
#pl = Plotter(n_data_rows = 2, data_row_colours =[ (255,0,0), (0, 255, 0)],
#        width=500,
#        background_colour=(0,0,0),
#        axis_colour = (100,100,100))

def text_line(text, position, text_size=15, text_colour=(255, 150, 50)):
    """helper function"""
    return stimuli.TextLine(text, position=position,
                            text_size=text_size, text_colour=text_colour)

sz = control.defaults.window_size
el = []

el.append(text_line("v: visualize sensors", [-sz[0] / 2 + 100, -sz[1] / 2 + 50]))
el.append(text_line("p: pause/unpause", [0, -sz[1] / 2 + 50]))
el.append(text_line("q: quit recording", [sz[0] / 2 - 100, -sz[1] / 2 + 50]))
el.append(text_line("filename: " + "testfilename.py",
                       position=[-sz[0] / 2 + 100, sz[1] / 2 - 50]))
el.append(text_line("date: {0}".format(time.strftime("%d/%m/%Y")),
                         position=[sz[0] / 2 - 100, sz[1] / 2 - 50]))

txt_pause = text_line("PAUSED", position=[0, 0], text_size=50)


pl_thread = PlotterThread(exp, refesh_time = 0.01)
display = DisplayThread(exp)

#pl = Plotter(n_data_rows = 1, data_row_colours =[ (0, 255, 0)])
marker = False
pause = False
pl_thread.start()
display.start()

display.add_present_stimuli(el)
display.update_request(wait_till_updated=True)
x = 0
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
    if key == ord("p"):
        pause = not pause
        if pause:
            exp.clock.wait(30) # wait plotting finished
            display.add_present_stimuli([txt_pause])
            display.update_request()
    if key == misc.constants.K_q:
        break

    if not pause:
        x += 1
        y = int(np.sin(x/15.0) * 90)
        y2 = int(np.sin(x/1000.0) * np.cos(x/40.0) * 90)

        exp.clock.reset_stopwatch()
        pl_thread.new_values((y,y2), marker)

        if x % 100==0:
            t = stimuli.TextLine(str(x), position=(0, 200))
            display.add_present_stimuli([t])
            display.update_request()
        if exp.clock.stopwatch_time >= 3: print exp.clock.stopwatch_time

        exp.clock.wait(10)

print "end"
display.stop()
pl_thread.stop()
control.end()

