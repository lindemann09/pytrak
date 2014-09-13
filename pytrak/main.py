# FIXME remote control not yet working

import os
import atexit
from expyriment import control, stimuli, design, io, misc

from __init__ import __version__
import settings
from settings import Command
from recording_screen import RecordingScreen
from plotter_xyz import PlotterXYZ
from trakstar import TrakSTARRecordingProcess, TrakSTARSettings, TrakSTARDataFileSettings
import change_trakstar_settings as ts_change


#TODO missing ip connection details

#globals
trakstar = None
exp = None

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

def initialize(remote_control=None, filename=None):
    """returns remote_control and file

     If remote_control or filename is None, the function will ask it (user input)

     """

    global trakstar, exp
    trakstar = TrakSTARRecordingProcess()
    trakstar.start()

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
    exp.mouse.show_cursor()

    if remote_control is None:
        logo_text_line(text="Use remote control? (y/N)").present()
        key = exp.keyboard.wait([ord("z"), ord("y"), ord("n"),
                        misc.constants.K_SPACE, misc.constants.K_RETURN ])[0]
        if key == ord("y") or key == ord("z"):
            remote_control = True
        else:
            remote_control = False

    if filename is None:
        bkg = logo_text_line("")
        filename = io.TextInput("Filename", background_stimulus=bkg).get()
        filename = filename.replace(" ", "_")

    logo_text_line(text="Trakstar is initializing...").present()

    while trakstar.is_alive() and not trakstar.flag_is_initialized.is_set():
        pass # wait finishing trackstar thread

    if trakstar.flag_is_initialized.is_set():
        logo_text_line(text="Trakstar initialized").present()
    else:
        logo_text_line(text="Trakstar failed to initialize").present()
        exp.keyboard.wait()
    return remote_control, filename

def prepare_recoding(remote_control, filename, trakstar_seetings):
    """get filename, allow changing of settings
    and make connection in remote control mode
    """

    global trakstar, exp

    # todo: display configuration
    if trakstar is None or not trakstar.flag_is_initialized.is_set():
        raise RuntimeError("Pytrak not initialized")

    ## remote control
    if remote_control:
        pass # FIXME include to trakstar process
    #    udp_connection.poll_last_data()  # clear buffer
    #    while not udp_connection.is_connected:  # wait for connection
    #        logo_text_line(text="Waiting for connection...").present()
    #        exp.clock.wait(100)
    #        udp_connection.poll()
    #       exp.keyboard.check()
    #     #get settings from remote
    #    s = udp_connection.poll()
    #    while s is None or s.lower() != 'done':
    #        logo_text_line(text="Waiting for settings...").present()
    #        exp.clock.wait(50)
    #        if s is not None:
    #            ts_change.remote(s)
    #        s = udp_connection.poll()
    #    udp_connection.send('confirm')
    #manual control
    else:
        logo_text_line(text="Change TrakSTAR settings? (y/N)").present()
        key = exp.keyboard.wait([ord("z"), ord("y"), ord("n"),
                        misc.constants.K_SPACE, misc.constants.K_RETURN ])[0]
        if key == ord("y") or key == ord("z"):
            menu = ts_change.menu(exp)
            menu.present()
            key = exp.keyboard.wait(range(ord("1"), ord("5") + 1) + [ord("q")])[0]
            while key != ord("q"):
                trakstar_seetings = ts_change.manual(exp, int(chr(int(key))),
                                                    trakstar_seetings)
                menu.present()
                key = exp.keyboard.wait(range(ord("1"), ord("5") + 1) +
                            [ord("q")])[0]

    #set system settings
    trakstar.command_queue.put(trakstar_seetings, timeout=1)
    comment_str = "Motion tracking data recorded with " + \
                   "Pytrak " + str(__version__)
    file_settings = TrakSTARDataFileSettings(filename = filename,
                            directory = settings.data_dir,
                            suffix = settings.data_suffix,
                            time_stamp_filename = settings.data_time_stamps,
                            write_angles = settings.data_write_angles,
                            write_quality = settings.data_write_quality,
                            write_udp = remote_control,
                            write_cpu_times = settings.data_write_cpu_time,
                            comment_line = comment_str)
    trakstar.command_queue.put(file_settings, timeout=1)


def wait_for_start_recording_event(remote_control, recording_screen):
    global trakstar, exp

    if trakstar is None or not trakstar.flag_is_initialized.is_set():
        raise RuntimeError("Pytrak not initialized")
    if remote_control:
        pass
   #     udp_connection.poll_last_data()  #clear buffer
   #     recording_screen.stimulus(infotext="Waiting to UDP start trigger...").present()
   #     s = None
   #     while s is None or not s.lower().startswith('start'):
   #         exp.keyboard.check()
   #         s = udp_connection.poll()
   #     udp_connection.send('confirm')
    else:
        recording_screen.stimulus(infotext="Press key to start recording").present()
        exp.keyboard.wait()


def end():
    control.end("Quitting Pytrak",goodbye_delay=0, fast_quit=True)
    exit()


def process_key_input(key=None):
    """processes input from key and udp port
    """
    if key == misc.constants.K_q or key == misc.constants.K_ESCAPE:
        return Command.quit
    elif key == misc.constants.K_p:
        return Command.toggle_pause
    elif key == misc.constants.K_UP:
        return Command.increase_scaling
    elif key == misc.constants.K_DOWN:
        return Command.decrease_scaling
    elif key == misc.constants.K_n:
        return Command.normalize_plotting
    elif key == misc.constants.K_SPACE:
        return Command.set_marker
    return None

# FIXME
# def process_udp_input(udp_input):
#    """maps udp input to keys and returns the key command"""
#    udp_command = udp_input.lower()
#    if udp_command == 'quit':
#        udp_connection.send('confirm')
#        return process_key_input(misc.constants.K_q)
#    elif udp_command == 'toggle_pause':
#        udp_connection.send('confirm')
#        return process_key_input(misc.constants.K_p)
#    return None

def record_data(remote_control, recording_screen):
    global trakstar, exp

    if trakstar is None or not trakstar.flag_is_initialized.is_set():
        raise RuntimeError("Pytrak not initialized")

    refresh_interval = 50
    refresh_timer = misc.Clock()
    #history = {} # make history
    #for sensor in trakstar.attached_sensors:
    #    history[sensor] = SensorHistory(history_size=5, number_of_parameter=3)

    recording_screen.stimulus().present()



    # start plotter threads
    plotter = PlotterXYZ(attached_sensors=trakstar.attached_sensors, ### FIXME get atched sensors
                         expyriment_screen_size=exp.screen.size,
                         refresh_time = 0.02)
    plotter.start()

    exp.keyboard.clear()
    trakstar.request_do_polling.set()
    quit_recording = False
    set_marker = False
    while not quit_recording:
        # process keyboard
        key = exp.keyboard.check(check_for_control_keys=False)
        command_array = [process_key_input(key)]

        # get data and process
        data_array = []
        while True:
            try:
                data_array.append(trakstar.data_queue.get_nowait())
            except:
                break

        for data in data_array:
            if len(data['udp']) > 0:
                set_marker = True
            plotter.add_values(data, set_marker=set_marker)
            set_marker = False
            if remote_control:
                pass
                #FIXME command_array.append(process_udp_input(data['udp']))
            #for sensor in trakstar.attached_sensors:
            #    history[sensor].update(data[sensor][:3])

        # refresh screen once in a while
        if refresh_timer.stopwatch_time >=refresh_interval:
            refresh_timer.reset_stopwatch()
            if trakstar.request_do_polling.is_set():
                plotter.update()
            else:
                recording_screen.stimulus("Paused recording").present()

        # process commands of last loop (ignore Nones)
        for command in filter(lambda x:x is not None, command_array):
            if command == Command.quit:
                quit_recording = True
                break
            elif command == Command.toggle_pause:
                if trakstar.request_do_polling.is_set():
                    trakstar.request_do_polling.clear()
                else:
                    recording_screen.stimulus().present()
                    trakstar.request_do_polling.set()
            elif command == Command.increase_scaling:
                plotter.scaling += 0.01
            elif command == Command.decrease_scaling:
                plotter.scaling -= 0.01
            elif command == Command.normalize_plotting:
                plotter.reset_start_values()
            elif command == Command.set_marker:
                set_marker = True

    plotter.stop()
    trakstar.request_stop.set()


def run(remote_control = None, filename=None):
    global trakstar, exp
    print "Pytrak", __version__

    trakstar_seetings = TrakSTARSettings()
    atexit.register(trakstar_seetings.save)
    trakstar_seetings.read()

    remote_control, filename = initialize(remote_control, filename)
    if not trakstar.flag_is_initialized.is_set():
        end()

    prepare_recoding(remote_control=remote_control, filename=filename, trakstar_seetings=trakstar_seetings)
    recording_screen = RecordingScreen(exp.screen.size, trakstar.filename)
    wait_for_start_recording_event(remote_control, recording_screen)
    record_data(remote_control, recording_screen)
    end()

if __name__ == "__main__":
    run()
