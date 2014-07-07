import os
from time import strftime
from threading import Thread

from expyriment import control, stimuli, design, io, misc

from pytrak import settings
from sensor_history import SensorHistory
from plotter import PlotterXYZ
from trakstar import TrakSTARInterface, TrakSTARRecordingThread


__author__ = 'Raphael Wallroth <rwallroth@uni-potsdam.de>, \
Oliver Lindemann <oliver.lindemann@cognitive-psychology.eu>'
__version__ = '0.2.0'

trakstar = None
exp = None
udp = None

def logo_text_line(text):
    blank = stimuli.Canvas(size=(600, 400))
    logo = stimuli.Picture(filename=os.path.join(os.path.dirname(__file__),
                            "pytrak_logo.png"), position = (0, 150))
    logo.scale(0.6)
    stimuli.TextLine(text="Version " + __version__, position=(0,80),
                     text_size = 14,
                     text_colour=misc.constants.C_EXPYRIMENT_ORANGE).plot(blank)
    logo.plot(blank)
    stimuli.TextLine(text=text).plot(blank)
    return blank

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

def text_line(text, position, text_size=15, text_colour=(255, 150, 50)):
    """helper function"""
    return stimuli.TextLine(text, position=position,
                            text_size=text_size, text_colour=text_colour)

def initialize(ask_for_remote_control):
    """returns remote control if asked for"""
    global trakstar, exp
    trakstar = TrakSTARInterface()
    thr_init_trackstar = Thread(target = trakstar.initialize)
    thr_init_trackstar.start()

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

    if ask_for_remote_control:
        logo_text_line(text="Use remote control? (Y/N)").present()
        key = exp.keyboard.wait([ord("z"), ord("y"), ord("n")])[0]
        if key == ord("y") or key == ord("z"):
            remote_control = True
        else:
            remote_control = False
    else:
        remote_control = None

    logo_text_line(text="Trakstar is initializing...").present()
    thr_init_trackstar.join() # wait finishing trackstar thread

    if trakstar.is_init:
        udp = trakstar.udp
        logo_text_line(text="Trakstar initialized").present()
    else:
        logo_text_line(text="Trakstar failed to initialize").present()
        exp.keyboard.wait()
    return remote_control

def prepare_recoding(remote_control, filename=None):
    """get filename, allow changing of settings
    and make connection in remote control mode
    """

    if trakstar is None or exp is None:
        raise RuntimeError("Pytrak not initialized")
    # remote control
    if remote_control:
        udp.poll_last_data()  # clear buffer
        while not udp.is_connected:  # wait for connection
            logo_text_line(text="Waiting for connection...").present()
            exp.clock.wait(100)
            udp.poll()
            exp.keyboard.check()
        #get settings from remote
        s = udp.poll()
        while s is None or s.lower() != 'done':
            logo_text_line(text="Waiting for settings...").present()
            exp.clock.wait(50)
            if s is not None:
                settings.get_udp_input(s)
            s = udp.poll()
        udp.send('confirm')
    #manual control
    else:
        if filename is None:
            bkg = logo_text_line("")
            filename = io.TextInput("filename:",
                                    background_stimulus=bkg).get()
        logo_text_line(text="Change TrakSTAR settings? (y/N)").present()
        key = exp.keyboard.wait([ord("z"), ord("y"), ord("n"), misc.constants.K_SPACE,
                                 misc.constants.K_RETURN, ])[0]
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
    trakstar.set_system_configuration(
                            measurement_rate = settings.measurement_rate,
                            max_range = settings.max_range,
                            power_line = settings.power_line,
                            metric = settings.metric,
                            report_rate = settings.report_rate,
                            print_configuration = True)

    comment_str = "Motion tracking data recorded with " + \
                   "Pytrak " + str(__version__)
    trakstar.open_data_file(filename = filename,
                            directory = "data",
                            suffix = ".csv",
                            time_stamp_filename = True,
                            write_angles = False,
                            write_quality = True,
                            write_udp = remote_control,
                            write_cpu_times = False,
                            comment_line = comment_str) #TODO: in settings



def wait_for_start_recording_event(remote_control):
    if trakstar is None or exp is None:
        raise RuntimeError("Pytrak not initialized")
    if remote_control:
        udp.poll_last_data()  #clear buffer
        logo_text_line(text="Waiting to start recording...").present()
        while s is None or not s.lower().startswith('start'):
            exp.keyboard.check()
            s = udp.poll()
        udp.send('confirm')
    else:
        logo_text_line(text="Press key to start recording").present()
        exp.keyboard.wait()

def present_recording_screen(pause=False):
    if trakstar is None or exp is None:
        raise RuntimeError("Pytrak not initialized")
    sz = control.defaults.window_size
    txt_v = text_line("v: visualize sensors", [-sz[0] / 2 + 100, -sz[1] / 2 + 50])
    txt_p = text_line("p: pause/unpause", [0, -sz[1] / 2 + 50])
    txt_q = text_line("q: quit recording", [sz[0] / 2 - 100, -sz[1] / 2 + 50])
    txt_fn = text_line("filename: " + trakstar.filename,
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
    if trakstar is not None:
        logo_text_line(text="Closing trakSTAR").present()
        trakstar.close_data_file()
        trakstar.close()
    control.end("Quitting Pytrak",goodbye_delay=0, fast_quit=True)

def record_data(remote_control):
    if trakstar is None or exp is None:
        raise RuntimeError("Pytrak not initialized")

    scale = 1
    pause = False
    history = {} # make history
    for sensor in trakstar.attached_sensors:
        history[sensor] = SensorHistory(history_size=5, number_of_parameter=3)

    present_recording_screen()

    plotter = PlotterXYZ(attached_sensors=trakstar.attached_sensors,
                         expyriment_screen_size=exp.screen.size,
                         refresh_time = 0.02)
    plotter.start()
    trakstar_thread = TrakSTARRecordingThread(trakstar)
    trakstar_thread.start()
    trakstar_thread.start_recording()
    exp.keyboard.clear()

    refresh_interval = 0.02
    refresh_timer = misc.Clock()
    while True:
        if not pause:
            data, n_missed_data = trakstar_thread.get_data(wait_new_data=False)
            #exp.clock.reset_stopwatch()
            if data is not None:
                udp_input = data['udp'] # temporary variable to check for udp input
                                    # read in by trakstar.get_synchronous_data_dict()
                #for sensor in trakstar.attached_sensors:
                #    history[sensor].update(data[sensor][:3])
                plotter.add_values(data, set_marker=False)
                if refresh_timer.stopwatch_time >=refresh_interval:
                    #exp.clock.reset_stopwatch()
                    plotter.update()
                    refresh_timer.stopwatch_time
                    #print exp.clock.stopwatch_time
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

        key = exp.keyboard.check(check_for_control_keys=False)
        if key == ord("q") or key == misc.constants.K_ESCAPE:
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

    plotter.stop()
    trakstar_thread.stop()

def run(remote_control = None, filename=None):
    global trakstar, exp, udp
    print "Pytrak", __version__
    if remote_control is None:
        remote_control = initialize(ask_for_remote_control = True)
    else:
        initialize(ask_for_remote_control = False)
    if not trakstar.is_init:
        end()
        #raw_input("Press <Enter> to close....")

    prepare_recoding(remote_control=remote_control, filename=filename)
    wait_for_start_recording_event(remote_control)
    record_data(remote_control)
    end()

if __name__ == "__main__":
    run()
