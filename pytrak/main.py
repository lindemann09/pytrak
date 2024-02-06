import os
from threading import Thread
from expyriment import control, stimuli, design, io, misc

from .__init__ import __version__
from . import settings
from .settings import Command
from .recording_screen import RecordingScreen
from .plotter_xyz import PlotterXYZ
from .trakstar import TrakSTARInterface, TrakSTARRecordingThread
from .sensor_history import SensorHistory



#TODO missing ip connection details

trakstar = None
exp = None
udp_connection = None

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

    global trakstar, udp_connection, exp
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
    thr_init_trackstar.join() # wait finishing trackstar thread

    if trakstar.is_init:
        udp_connection = trakstar.udp
        logo_text_line(text="Trakstar initialized").present()
    else:
        logo_text_line(text="Trakstar failed to initialize").present()
        exp.keyboard.wait()
    return remote_control, filename

def prepare_recoding(remote_control, filename):
    """get filename, allow changing of settings
    and make connection in remote control mode
    """
    # todo: display configuration
    if trakstar is None or exp is None:
        raise RuntimeError("Pytrak not initialized")
    # remote control
    if remote_control:
        udp_connection.poll_last_data()  # clear buffer
        while not udp_connection.is_connected:  # wait for connection
            logo_text_line(text="Waiting for connection...").present()
            exp.clock.wait(100)
            udp_connection.poll()
            exp.keyboard.check()
        #get settings from remote
        s = udp_connection.poll()
        while s is None or s.lower() != 'done':
            logo_text_line(text="Waiting for settings...").present()
            exp.keyboard.process_control_keys()
            exp.clock.wait(50)
            if s is not None:
                settings.process_udp_input(s)
            s = udp_connection.poll()
        udp_connection.send('confirm')
    #manual control
    else:
        logo_text_line(text="Change TrakSTAR settings? (y/N)").present()
        key = exp.keyboard.wait([ord("z"), ord("y"), ord("n"),
                        misc.constants.K_SPACE, misc.constants.K_RETURN ])[0]
        if key == ord("y") or key == ord("z"):
            menu = settings.get_menu(exp)
            menu.present()
            key = exp.keyboard.wait(list(range(ord("1"), ord("5") + 1)) + [ord("q")])[0]
            while key != ord("q"):
                settings.get_input(exp, int(chr(int(key))))
                menu.present()
                key = exp.keyboard.wait(list(range(ord("1"), ord("5") + 1)) +
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
                            directory = settings.data_dir,
                            suffix = settings.data_suffix,
                            time_stamp_filename = settings.data_time_stamps,
                            write_angles = settings.data_write_angles,
                            write_quality = settings.data_write_quality,
                            write_udp = remote_control,
                            write_cpu_times = settings.data_write_cpu_time,
                            comment_line = comment_str)


def wait_for_start_recording_event(remote_control, recording_screen):
    if trakstar is None or exp is None:
        raise RuntimeError("Pytrak not initialized")
    if remote_control:
        udp_connection.poll_last_data()  #clear buffer
        recording_screen.stimulus(infotext="Waiting to UDP start trigger...").present()
        s = None
        while s is None or not s.lower().startswith('start'):
            exp.keyboard.check()
            s = udp_connection.poll()
        udp_connection.send('confirm')
    else:
        recording_screen.stimulus(infotext="Press key to start recording").present()
        exp.keyboard.wait()


def end():
    if trakstar is not None:
        #logo_text_line(text="Closing trakSTAR").present()
        trakstar.close_data_file()
        trakstar.close()
    control.end("Quitting Pytrak",goodbye_delay=0, fast_quit=True)

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
    elif key == misc.constants.K_r:
        return Command.set_reference_position
    return None

def process_udp_input(udp_input):
    """maps udp input to keys and returns the key command"""
    udp_command = udp_input.lower()
    if udp_command == 'quit':
        udp_connection.send('confirm')
        return process_key_input(misc.constants.K_q)
    elif udp_command == 'toggle_pause':
        udp_connection.send('confirm')
        return process_key_input(misc.constants.K_p)
    return None

def record_data(remote_control, recording_screen):
    if trakstar is None or exp is None:
        raise RuntimeError("Pytrak not initialized")

    refresh_interval = 50
    refresh_timer = misc.Clock()
    history = SensorHistory(history_size = 10, number_of_parameter=3) # TODO: set history size

    recording_screen.stimulus().present()

    #start trakstar thread
    trakstar_thread = TrakSTARRecordingThread(trakstar)
    trakstar_thread.start()
    # start plotter threads
    plotter = PlotterXYZ(attached_sensors=trakstar.attached_sensors,
                         expyriment_screen_size=exp.screen.size,
                         refresh_time = 0.02)
    plotter.start()

    exp.keyboard.clear()
    trakstar_thread.start_recording()
    quit_recording = False
    set_marker = False
    was_moving = None
    was_inside = None
    detection_sensor_id = 1 # TODO: which sensor?
    while not quit_recording:
        # process keyboard
        key = exp.keyboard.check(check_for_control_keys=False)
        command_array = [process_key_input(key)]

        # get data and process
        data_array = trakstar_thread.get_data_array()
        for data in data_array:
            if detection_sensor_id in data:
                history.update(data[detection_sensor_id][:3]) 
                ## movement detection
                # move = history.is_moving(velocity_threshold=4,
                #                         min_n_samples=10,
                #                         sampling_rate=80) # TODO settings!
                #if move is not None and move != was_moving:
                #    set_marker = True
                #    was_moving = move
                #    if remote_control: # output
                #        if move:
                #            udp_connection.send("M_START")
                #        else:
                #            udp_connection.send("M_STOP")

                # position detection
                inside = history.is_in_reference_area()
                if inside is not None and inside != was_inside:
                    set_marker = True
                    was_inside = inside
                    if remote_control: # output
                        if inside:
                            udp_connection.send("D_INSIDE")
                        else:
                            udp_connection.send("D_OUTSIDE")
                
            if len(data['udp']) > 0:
                set_marker = True
            plotter.add_values(data, set_marker=set_marker)
            set_marker = False

            if remote_control: # input
                command_array.append(process_udp_input(data['udp']))

        # refresh screen once in a while
        if refresh_timer.stopwatch_time >=refresh_interval:
            refresh_timer.reset_stopwatch()
            if trakstar_thread.is_recording:
                plotter.update()
            else:
                recording_screen.stimulus("Paused recording").present()

        # process commands of last loop (ignore Nones)
        for command in [x for x in command_array if x is not None]:
            if command == Command.quit:
                quit_recording = True
                break
            elif command == Command.toggle_pause:
                if trakstar_thread.is_recording:
                    trakstar_thread.pause_recording()
                else:
                    recording_screen.stimulus().present()
                    trakstar_thread.start_recording()
            elif command == Command.increase_scaling:
                plotter.scaling += 0.01
            elif command == Command.decrease_scaling:
                plotter.scaling -= 0.01
            elif command == Command.normalize_plotting:
                plotter.reset_start_values()
            elif command == Command.set_reference_position:
                print("set reference point")
                history.set_reference_area(radius= 10) # TODO settings
            elif command == Command.set_marker:
                set_marker = True

    plotter.stop()
    trakstar_thread.stop()


def run(remote_control = None, filename=None):
    global trakstar, exp, udp_connection
    print("Pytrak", __version__)
    remote_control, filename = initialize(remote_control, filename)
    if not trakstar.is_init:
        end()
        #raw_input("Press <Enter> to close....")

    prepare_recoding(remote_control=remote_control, filename=filename)
    recording_screen = RecordingScreen(exp.screen.size, trakstar.filename)
    wait_for_start_recording_event(remote_control, recording_screen)
    record_data(remote_control, recording_screen)
    end()

if __name__ == "__main__":
    run()
