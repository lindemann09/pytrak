from trakstar import TrakSTARInterface
from sensor_history import SensorHistory
from expyriment import control, stimuli, design, io, misc
from time import strftime

__author__ = 'Raphael Wallroth <>, \
Oliver Lindemann <oliver.lindemann@cognitive-psychology.eu>'
__version__ = '0.1.2'


trakstar = TrakSTARInterface()
print "Initialize TrakSTAR"
trakstar.initialize()

screen_size = io.Screen(colour=(0,63,0), open_gl=False, window_mode=False,
        window_size=(0,0)).size
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


t_wait = 1500
def invalid_value():
    stimuli.TextLine(text="Invalid value!").present()
    exp.clock.wait(t_wait)

def get_input(i):
    global measurement_rate, max_range, report_rate, power_line, metric
    if i == 1:
        measurement_rate = int(io.TextInput("Measurement rate (20 Hz < rate < 255 Hz):", length=3,
                                            ascii_filter=range(ord("0"),ord("9")+1)).get())
        if measurement_rate < 20 or measurement_rate > 255:
            measurement_rate = 80
            invalid_value()
        else:
            stimuli.TextLine(text="Measurement rate set to {0} Hz.".format(measurement_rate)).present()
            exp.clock.wait(t_wait)
        return
    elif i == 2:
        max_range = int(io.TextInput("Maximum range of transmitter (36, 72, 144 inches):", length=3,
                                     ascii_filter=range(ord("1"),ord("5"))+[ord("6"),ord("7")]).get())
        if max_range not in [36, 72, 144]:
            max_range = 36
            invalid_value()
        else:
            stimuli.TextLine(text="Maximum range of transmitter set to {0} inches.".format(max_range)).present()
            exp.clock.wait(t_wait)
        return
    elif i == 3:
        report_rate = int(io.TextInput("Report rate of the data (1 <= rate <= 127):", length=3,
                                       ascii_filter=range(ord("0"),ord("9")+1)).get())
        if report_rate < 1 or report_rate > 127:
            report_rate = 1
            invalid_value()
        else:
            stimuli.TextLine(text="Report rate of incoming data set to {0}.".format(report_rate)).present()
            exp.clock.wait(t_wait)
        return
    elif i == 4:
        power_line = int(io.TextInput("Power line frequency of the AC power source (50 or 60 Hz):",
                                      length=2, ascii_filter=[ord("0"),ord("5"),ord("6")]).get())
        if power_line not in [50, 60]:
            power_line = 60
            invalid_value()
        else:
            stimuli.TextLine(text="Power line frequency of the AC power source set to {0} Hz.".format(power_line)).present()
            exp.clock.wait(t_wait)
        return
    elif i == 5:
        metric = int(io.TextInput("Switch metric data reporting on/off (1/0):",
                                  length=1, ascii_filter=[ord("0"),ord("1")]).get())
        if metric not in [0, 1]:
            metric = True
            invalid_value()
        else:
            stimuli.TextLine(text="Metric data reporting set to {0}.".format(metric)).present()
            exp.clock.wait(t_wait)
        return

def get_udp_input(s):
    """
    Input received via udp to change TrakSTAR system settings.
    Every string begins with a description of the value to be changed,
    followed by a colon, and the value to be set.

    e.g.: "measurement: 50", "metric: 0"
    """
    global filename, measurement_rate, max_range, report_rate, power_line, metric
    if s.lower().startswith("filename"):
        _, filename = s.split(":")
        filename = filename.strip()
        return
    elif s.lower().startswith("measurement"):
        _, measurement_rate = s.split(":")
        measurement_rate = int(measurement_rate.strip())
        if measurement_rate < 20 or measurement_rate > 255:
            measurement_rate = 80
        return
    elif s.lower().startswith("maximum"):
        _, max_range = s.split(":")
        max_range = int(max_range.strip())
        if max_range not in [36, 72, 144]:
            max_range = 36
        return
    elif s.lower().startswith("report"):
        _, report_rate = s.split(":")
        report_rate = int(report_rate.strip())
        if report_rate < 1 or report_rate > 127:
            report_rate = 1
        return
    elif s.lower().startswith("power"):
        _, power_line = s.split(":")
        power_line = int(power_line.strip())
        if power_line not in [50, 60]:
            power_line = 60
        return
    elif s.lower().startswith("metric"):
        _, metric = s.split(":")
        metric = int(metric.strip())
        if metric not in [0, 1]:
            metric = True
        return

menu = stimuli.TextScreen("Settings:",
                          "1: Measurement rate\n"+
                          "2: Maximum range of transmitter\n"+
                          "3: Report rate of data\n"+
                          "4: Power line frequency\n"+
                          "5: Metric data reporting\n\n"+
                          "q: Quit settings",
                          text_justification=0,
                          size=[sz[0]/4, sz[1]/2])

filename, measurement_rate, max_range, report_rate, power_line, metric = '', 80, 36, 1, 60, True

stimuli.TextLine(text="Use remote control? (Y/N)").present()
key = exp.keyboard.wait([ord("z"), ord("y"), ord("n")])[0]

#remote control
if key == ord("y") or key == ord("z"):
    remote = True
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
            get_udp_input(s)
        s = trakstar.udp.poll()
    trakstar.udp.send('confirm')
#manual control
else:
    remote = False
    filename = io.TextInput("filename:").get()
    stimuli.TextLine(text="Change TrakSTAR settings? (Y/N)").present()
    key = exp.keyboard.wait([ord("z"), ord("y"), ord("n")])[0]
    if key == ord("y") or key == ord("z"):
        menu.present()
        key = exp.keyboard.wait(range(ord("1"),ord("5")+1)+[ord("q")])[0]
        while key != ord("q"):
            get_input(int(chr(int(key))))
            menu.present()
            key = exp.keyboard.wait(range(ord("1"),ord("5")+1)+[ord("q")])[0]


#set system settings
trakstar.set_system_configuration(measurement_rate=measurement_rate,
                                  max_range=max_range, power_line=power_line,
                                  metric=metric, report_rate=report_rate,
                                  print_configuration=True)

trakstar.open_data_file(filename=filename, directory="data",
                        suffix = ".csv", time_stamp_filename=True,
                        write_angles=False, write_quality=True,
                        write_udp=remote)

# make circles and history
show_circles = False
colours = { 1: misc.constants.C_RED,
            2: misc.constants.C_GREEN,
            3: misc.constants.C_YELLOW,
            4: misc.constants.C_BLUE }
circle_diameter = 40
circles = {}
history = {}
for sensor in trakstar.attached_sensors:
    circles[sensor] = stimuli.Circle(circle_diameter, colour=colours[sensor])
    stimuli.TextLine(str(sensor), text_size=circle_diameter/2, text_bold=True,
                     text_colour=misc.constants.C_WHITE).plot(circles[sensor])
    history[sensor] = SensorHistory(history_size=5, number_of_parameter=3)

info_col = (255, 150, 50)
txt_v = stimuli.TextLine("v: visualize sensors", position=[-sz[0]/2+100, -sz[1]/2+50],
                         text_size=15, text_colour=info_col)
txt_p = stimuli.TextLine("p: pause/unpause", position=[0, -sz[1]/2+50],
                         text_size=15, text_colour=info_col)
txt_q = stimuli.TextLine("q: quit recording", position=[sz[0]/2-100, -sz[1]/2+50],
                         text_size=15, text_colour=info_col)
txt_fn = stimuli.TextLine("filename: "+filename, position=[-sz[0]/2+100, sz[1]/2-50],
                            text_size=15, text_colour=info_col)
txt_date = stimuli.TextLine(text = "date: {0}".format(strftime("%d/%m/%Y")),
                            position=[sz[0]/2-100, sz[1]/2-50],
                            text_size=15, text_colour=info_col)
info_txts = [txt_v, txt_p, txt_q, txt_fn, txt_date]

txt_pause = stimuli.TextLine("PAUSED", position=[0,-50],text_size=50, text_colour=info_col)
canvas = stimuli.BlankScreen()

def update_screen(trakstar, circles, history, show_circles):
    if show_circles:
        for sensor in trakstar.attached_sensors:
            if not trakstar.system_configuration.metric:
                circles[sensor].position = (
                    int(round(history[sensor].moving_average[1]*10)),
                    int(round(history[sensor].moving_average[0]*10)))
            else:
                circles[sensor].position = (history[sensor].moving_average[1]/2,
                                            history[sensor].moving_average[0]/2)

    canvas.clear_surface()
    txt_box = stimuli.TextBox(text=TrakSTARInterface.data2string(data, times=False, udp=remote),
                    #text_justification = 0,
                    size = (sz[0], 70*len(trakstar.attached_sensors)), text_size=20)
    if show_circles:
        for circle in circles.values():
            circle.plot(canvas)
    txt_box.plot(canvas)
    for txt in info_txts:
        txt.plot(canvas)
    canvas.present()

pause = False
cnt = 0
exp.keyboard.clear()

if remote:
    s = trakstar.udp.poll_last_data() #clear buffer
    while s is None or not s.lower().startswith('start'):
        stimuli.TextLine(text="Waiting to start recording...").present()
        exp.keyboard.check()
        exp.clock.wait(100)
        s = trakstar.udp.poll()
    trakstar.udp.send('confirm')
    trakstar.udp.poll_last_data() #clear buffer
else:
    stimuli.TextLine(text="Press key to start recording").present()
    exp.keyboard.wait()

trakstar.reset_timer()

while True:
    if not pause:
        cnt += 1
        data = trakstar.get_synchronous_data_dict() #polls udp while unpaused
        udp_input = data['udp'] #temporary variable to check for udp input read in by trakstar.get_synchronous_data_dict() 
        for sensor in trakstar.attached_sensors:
            history[sensor].update(data[sensor][:3])
        if cnt % 40 == 1:
            update_screen(trakstar, circles, history, show_circles)
    else:
        if remote:
            if udp_input.lower() == 'pause':
                txt_pause.plot(canvas)
                canvas.present()
                udp_input = '0' #reset the pause command to None
            s = trakstar.udp.poll() #polls udp while paused
            if s is not None and s.lower() == 'unpause':
                pause = False
                trakstar.udp.send('confirm')
                #if you wish to have the 'unpause' command in your data output, you'll have to send it twice!
        
    key = exp.keyboard.check()
    if key == ord("v"):
        show_circles = not show_circles
    elif key == ord("p"):
        pause = not pause
    elif key == ord("q"):
        break

    if remote:
        if udp_input != '0':
            if udp_input.lower() == 'pause':
                pause = True                
                trakstar.udp.send('confirm')
            elif udp_input.lower() == 'quit':
                trakstar.udp.send('confirm')
                break     




trakstar.close_data_file()
trakstar.close()
stimuli.TextLine(text="Closing trakSTAR").present()
control.end()
