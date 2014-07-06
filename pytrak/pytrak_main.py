from time import strftime

from expyriment import control, stimuli, design, io, misc

from pytrak import settings
from sensor_history import SensorHistory
from plotter3d import Plotter3d
from trakstar import TrakSTARInterface


__author__ = 'Raphael Wallroth <>, \
Oliver Lindemann <oliver.lindemann@cognitive-psychology.eu>'
__version__ = '0.2'


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


def initialize():
    """return: trakstar, expyriment experiment, remote_control"""
    trakstar = TrakSTARInterface()
    print "Initialize TrakSTAR"
    trakstar.initialize() #TODO as thread

    screen_size = get_monitor_resolution()

    # expyriment
    control.defaults.initialize_delay = 0
    control.defaults.pause_key = None
    control.defaults.window_mode = True
    control.defaults.window_size = [screen_size[0] - screen_size[0] / 10,
                                    screen_size[1] - screen_size[1] / 10]
    control.defaults.fast_quit = True
    control.defaults.open_gl = False
    control.defaults.event_logging = 0
    exp = design.Experiment()
    exp.set_log_level(0)
    control.initialize(exp)

    stimuli.TextLine(text="Use remote control? (Y/N)").present()
    key = exp.keyboard.wait([ord("z"), ord("y"), ord("n")])[0]
    if key == ord("y") or key == ord("z"):
        remote_control = True
    else
        remote_control = False
    return trakstar, exp, remote_control


def prepare_recoding(trakstar, exp, remote_control, udp):
    """get filename, allow changing of settings
    and make connection in remote control mode

    returns the filename
    """
    # remote control
    if remote_control:
        filename = ""
        udp.poll_last_data()  # clear buffer
        while not udp.is_connected:  # wait for connection
            stimuli.TextLine(text="Waiting for connection...").present()
            exp.clock.wait(100)
            udp.poll()
            exp.keyboard.check()
        #get settings from remote
        s = udp.poll()
        while s is None or s.lower() != 'done':
            stimuli.TextLine(text="Waiting for settings...").present()
            exp.clock.wait(50)
            if s is not None:
                settings.get_udp_input(s)
            s = udp.poll()
        udp.send('confirm')
    #manual control
    else:
        filename = io.TextInput("filename:").get()
        stimuli.TextLine(text="Change TrakSTAR settings? (Y/N)").present()
        key = exp.keyboard.wait([ord("z"), ord("y"), ord("n")])[0]
        if key == ord("y") or key == ord("z"):
            menu = settings.get_menu()
            menu.present()
            key = exp.keyboard.wait(range(ord("1"), ord("5") + 1) + [ord("q")])[0]
            while key != ord("q"):
                settings.get_input(int(chr(int(key))))
                menu.present()
                key = exp.keyboard.wait(range(ord("1"), ord("5") + 1) +
                            [ord("q")])[0]

    #set system settings
    trakstar.set_system_configuration(measurement_rate=settings.measurement_rate,
                                      max_range=settings.max_range,
                                      power_line=settings.power_line,
                                      metric=settings.metric,
                                      report_rate=settings.report_rate,
                                      print_configuration=True)

    trakstar.open_data_file(filename=filename, directory="data",
                            suffix=".csv", time_stamp_filename=True,
                            write_angles=False, write_quality=True,
                            write_udp=remote_control,
                            write_cpu_times=False) #TODO: in settings
    return filename


def text_line(text, position, text_size=15, text_colour=(255, 150, 50)):
    "helper function"""
    return stimuli.TextLine(text, position=position,
                            text_size=text_size, text_colour=text_colour)

def wait_for_start_recording_event(udp, exp, remote_control):
    if remote_control:
        udp.poll_last_data()  #clear buffer
        stimuli.TextLine(text="Waiting to start recording...").present()
        while s is None or not s.lower().startswith('start'):
            exp.keyboard.check()
            s = udp.poll()
        udp.send('confirm')
    else:
        stimuli.TextLine(text="Press key to start recording").present()
        exp.keyboard.wait()

def present_recording_screen(pause=False):
    sz = control.defaults.window_size
    txt_v = text_line("v: visualize sensors", [-sz[0] / 2 + 100, -sz[1] / 2 + 50])
    txt_p = text_line("p: pause/unpause", [0, -sz[1] / 2 + 50])
    txt_q = text_line("q: quit recording", [sz[0] / 2 - 100, -sz[1] / 2 + 50])
    txt_fn = text_line("filename: " + filename,
                       position=[-sz[0] / 2 + 100, sz[1] / 2 - 50])
    txt_date = text_line("date: {0}".format(strftime("%d/%m/%Y")),
                         position=[sz[0] / 2 - 100, sz[1] / 2 - 50])
    info_txts = [txt_v, txt_p, txt_q, txt_fn, txt_date]
    txt_pause = text_line("PAUSED", position=[0, -50], text_size=50)

    canvas = stimuli.BlankScreen()
    for txt in info_txts:
        txt.plot(canvas)
    if pause:
        txt_pause.plot(canvas)
    canvas.present()

def end():
    trakstar.close_data_file()
    trakstar.close()
    stimuli.TextLine(text="Closing trakSTAR").present()
    control.end()

def record_data(trakstar, exp, remote_control, udp):
    scale = 1
    pause = False
    plotter = Plotter3d(attached_sensors=trakstar.attached_sensors)
    history = {} # make history
    for sensor in trakstar.attached_sensors:
        history[sensor] = SensorHistory(history_size=5, number_of_parameter=3)

    present_recording_screen()
    trakstar.reset_timer()
    exp.keyboard.clear()

    while True:
        if not pause:
            data = trakstar.get_synchronous_data_dict()  #polls udp while unpaused
            udp_input = data['udp'] # temporary variable to check for udp input
                                    # read in by trakstar.get_synchronous_data_dict()
            exp.clock.reset_stopwatch()
            #for sensor in trakstar.attached_sensors:
            #    history[sensor].update(data[sensor][:3])
            plotter.update_values(data)
            exp.screen.update_stimuli(plotter.plotter_array)
            print exp.clock.stopwatch_time
        else:
            if remote_control:
                if udp_input.lower() == 'pause':
                    pause = True
                    present_recording_screen(pause=pause)
                    udp_input = '0'  #reset the pause command to None
                s = udp.poll()  #polls udp while paused
                if s is not None and s.lower() == 'unpause':
                    pause = False
                    present_recording_screen(pause=False)
                    udp.send('confirm')
                    #if you wish to have the 'unpause' command in your data output,
                    # you'll have to send it twice!

        key = exp.keyboard.check()
        if key == ord("q"):
            break
        elif key == ord("p"):
            pause = not pause
            present_recording_screen(pause=pause)
        elif key == misc.constants.K_UP:
            plotter.scale += 0.01
        elif key == misc.constants.K_DOWN:
            plotter.scale -= 0.01

        if remote_control:
            if udp_input != '0':
                if udp_input.lower() == 'pause':
                    pause = True
                    udp.send('confirm')
                    present_recording_screen(pause=pause)
                elif udp_input.lower() == 'quit':
                    udp.send('confirm')
                    break

def run():
    trakstar, exp, remote_control = initialize()
    filename = prepare_recoding(trakstar, exp, remote_control, trakstar.udp)
    wait_for_start_recording_event(trakstar.udp, exp, remote_control),
    record_data(trakstar, exp, remote_control, trakstar.udp)
    end()

if __name__ == "__main__":
    run()
