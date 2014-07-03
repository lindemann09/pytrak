from time import strftime
import numpy as np
from expyriment import control, stimuli, design, io, misc

import settings
from trakstar import TrakSTARInterface
from sensor_history import SensorHistory
from plotter3d import Plotter3d


__author__ = 'Raphael Wallroth <>, \
Oliver Lindemann <oliver.lindemann@cognitive-psychology.eu>'
__version__ = '0.2'


trakstar = TrakSTARInterface()
print "Initialize TrakSTAR"
trakstar.initialize()

def get_monitor_resolution():
    """Returns the monitor resolution

    Returns n
    -------
    resolution: (int, int)
        monitor resolution, screen resolution

    """

    import pygame
    pygame.display.init()
    return (pygame.display.Info().current_w,
                pygame.display.Info().current_h)

screen_size = get_monitor_resolution()
sz = [screen_size[0]-screen_size[0]/10,
    screen_size[1]-screen_size[1]/10]

#expyriment
control.defaults.initialize_delay = 0
control.defaults.pause_key = None
control.defaults.window_mode = True
control.defaults.window_size = sz
control.defaults.fast_quit = True
control.defaults.open_gl = False
control.defaults.event_logging = 0
exp = design.Experiment()
exp.set_log_level(0)
control.initialize(exp)


stimuli.TextLine(text="Use remote control? (Y/N)").present()
key = exp.keyboard.wait([ord("z"), ord("y"), ord("n")])[0]

#remote control
if key == ord("y") or key == ord("z"):
    remote = True
    filename = ""
    trakstar.udp.poll_last_data() # clear buffer
    while not trakstar.udp.is_connected: # wait for connection
        stimuli.TextLine(text="Waiting for connection...").present()
        exp.clock.wait(100)
        trakstar.udp.poll()
        exp.keyboard.check()
    #get settings from remote
    s = trakstar.udp.poll()
    while s is None or s.lower() != 'done':
        stimuli.TextLine(text="Waiting for settings...").present()
        exp.clock.wait(50)
        if s is not None:
            settings.get_udp_input(s)
        s = trakstar.udp.poll()
    trakstar.udp.send('confirm')
#manual control
else:
    remote = False
    filename = io.TextInput("filename:").get()
    stimuli.TextLine(text="Change TrakSTAR settings? (Y/N)").present()
    key = exp.keyboard.wait([ord("z"), ord("y"), ord("n")])[0]
    if key == ord("y") or key == ord("z"):
        menu = settings.get_menu()
        menu.present()
        key = exp.keyboard.wait(range(ord("1"),ord("5")+1)+[ord("q")])[0]
        while key != ord("q"):
            settings.get_input(int(chr(int(key))))
            menu.present()
            key = exp.keyboard.wait(range(ord("1"),ord("5")+1)+[ord("q")])[0]


#set system settings
trakstar.set_system_configuration(measurement_rate=settings.measurement_rate,
                                  max_range=settings.max_range,
                                  power_line=settings.power_line,
                                  metric=settings.metric,
                                  report_rate=settings.report_rate,
                                  print_configuration=True)

trakstar.open_data_file(filename=filename, directory="data",
                        suffix = ".csv", time_stamp_filename=True,
                        write_angles=False, write_quality=True,
                        write_udp=remote, write_cpu_times=False) #todo: in settings

# make circles and history
show_circles = False
circles = {}
history = {}
for sensor in trakstar.attached_sensors:
    circles[sensor] = stimuli.Circle(settings.circle_diameter, colour=settings.colours[sensor])
    stimuli.TextLine(str(sensor), text_size=settings.circle_diameter/2, text_bold=True,
                     text_colour=misc.constants.C_WHITE).plot(circles[sensor])
    history[sensor] = SensorHistory(history_size=5, number_of_parameter=3)

# make text lines
def text_line(text, position, text_size=15, text_colour = (255, 150, 50)):
    return stimuli.TextLine(text, position = position,
                    text_size = text_size, text_colour=text_colour)
sz = control.defaults.window_size
txt_v = text_line("v: visualize sensors", [-sz[0]/2+100, -sz[1]/2+50])
txt_p = text_line("p: pause/unpause", [0, -sz[1]/2+50])
txt_q = text_line("q: quit recording", [sz[0]/2-100, -sz[1]/2+50])
txt_fn = text_line("filename: " + filename,
                        position=[-sz[0]/2+100, sz[1]/2-50])
txt_date = text_line("date: {0}".format(strftime("%d/%m/%Y")),
                            position=[sz[0]/2-100, sz[1]/2-50])
info_txts = [txt_v, txt_p, txt_q, txt_fn, txt_date]
txt_pause = text_line("PAUSED", position=[0,-50], text_size=50)


def update_circles(trakstar,circles, history):
    for sensor in trakstar.attached_sensors:
        if not trakstar.system_configuration.metric:
            circles[sensor].position = (
                int(round(history[sensor].moving_average[1]*10)),
                int(round(history[sensor].moving_average[0]*10)))
        else:
            circles[sensor].position = (history[sensor].moving_average[1]/2,
                                        history[sensor].moving_average[0]/2)
    for circle in circles.values(): #todo
        circle.plot(canvas)

def show_info_screen(pause = False):
    canvas = stimuli.BlankScreen()
    for txt in info_txts:
        txt.plot(canvas)
    if pause:
        txt_pause.plot(canvas)
    canvas.present()


pause = False
cnt = -1
exp.keyboard.clear()

if remote:
    trakstar.udp.poll_last_data() #clear buffer
    stimuli.TextLine(text="Waiting to start recording...").present()
    while s is None or not s.lower().startswith('start'):
        exp.keyboard.check()
        s = trakstar.udp.poll()
    trakstar.udp.send('confirm')
else:
    stimuli.TextLine(text="Press key to start recording").present()
    exp.keyboard.wait()

trakstar.reset_timer()

plotter = Plotter3d(attached_sensors=trakstar.attached_sensors)
show_info_screen()
scale = 1
while True:
    if not pause:
        cnt += 1
        data = trakstar.get_synchronous_data_dict() #polls udp while unpaused
        udp_input = data['udp'] #temporary variable to check for udp input read in by trakstar.get_synchronous_data_dict()

        exp.clock.reset_stopwatch()
        #for sensor in trakstar.attached_sensors:
        #    history[sensor].update(data[sensor][:3])
        plotter.update_values(data)
        exp.screen.update_stimuli(plotter.plotter_array)
        print exp.clock.stopwatch_time

        #if cnt % (40) == 0 and show_circles:
        #    update_circles(trakstar, circles, history)
    else:
        if remote:
            if udp_input.lower() == 'pause':
                pause = True
                show_info_screen(pause = pause)
                udp_input = '0' #reset the pause command to None
            s = trakstar.udp.poll() #polls udp while paused
            if s is not None and s.lower() == 'unpause':
                pause = False
                show_info_screen(pause = False)
                trakstar.udp.send('confirm')
                #if you wish to have the 'unpause' command in your data output, you'll have to send it twice!

    key = exp.keyboard.check()
    if key == ord("v"):
        show_circles = not show_circles
    elif key == ord("p"):
        pause = not pause
        show_info_screen(pause = pause)
    elif key == ord("q"):
        break
    elif key == misc.constants.K_UP:
        plotter.scale += 0.01
    elif key == misc.constants.K_DOWN:
        plotter.scale -= 0.01

    if remote:
        if udp_input != '0':
            if udp_input.lower() == 'pause':
                pause = True
                trakstar.udp.send('confirm')
                show_info_screen(pause = pause)
            elif udp_input.lower() == 'quit':
                trakstar.udp.send('confirm')
                break


trakstar.close_data_file()
trakstar.close()
stimuli.TextLine(text="Closing trakSTAR").present()
control.end()
