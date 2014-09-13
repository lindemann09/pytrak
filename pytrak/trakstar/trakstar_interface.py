"""TrakSTARInterface"""
import atexit
from multiprocessing import Process, Event, Queue, Value
import ConfigParser
from pytrak.trakstar import atc3dg_functions as api

__author__ = 'Raphael Wallroth <rwallroth@uni-potsdam.de>, \
Oliver Lindemann <oliver.lindemann@cognitive-psychology.eu>'

import os
import ctypes
from time import localtime, strftime, time
import numpy as np
from udp_connection import UDPConnection

def data_dict2string(data_dict, angles=False, quality=False, times=True,
                cpu_times=False, udp=True):
    txt = ""
    for sensor in range(1, 5):
        if data_dict.has_key(sensor):
            if times:
                txt = txt + "{0},".format(data_dict["time"])
            txt = txt + "%d,%.4f,%.4f,%.4f" % \
                        (sensor, data_dict[sensor][0],
                         data_dict[sensor][1], data_dict[sensor][2])
            if angles:
                txt = txt + ",%.4f,%.4f,%.4f" % (data_dict[sensor][3],
                                                 data_dict[sensor][4],
                                                 data_dict[sensor][5])
            if quality:
                txt = txt + ",{0}".format(data_dict[sensor][6])
            if udp:
                if len(data_dict["udp"])>0:
                    txt = txt + ",{0}".format(data_dict["udp"])
                else:
                    txt = txt + ",0"
            if cpu_times:
                txt = txt + ",{0}".format(data_dict["cpu_time"])

            txt = txt + "\n"
    return txt[:-1]

def get_attached_sensors(data_dic):
    """return an array with the ids of attached sensors from a data dict"""
    return filter(lambda x:data_dic.has_key(x), [1,2,3,4])


def copy_data_dict(old):
    """deep copy of the data dict"""
    new = old.copy()
    # copy of numpyarray for each attached sensor
    for s in filter(lambda x:new.has_key(x), [1,2,3,4]):
        new[s] = np.copy(old[s])
    return new


class TrakSTARDataFileSettings(object):

    def __init__(self, filename, directory="data", suffix=".csv",
                       time_stamp_filename=False, write_angles=False,
                       write_quality=False, write_cpu_times=False,
                       write_udp=True, comment_line=""):
        self.filename = filename
        self.directory = directory
        self.suffix = suffix
        self.time_stamp_filename = time_stamp_filename
        self.write_angles = write_angles
        self.write_quality = write_quality
        self.write_cpu_times = write_cpu_times
        self.write_udp = write_udp
        self.comment_line = comment_line


class TrakSTARSettings(object):
    cfg_filename = "pytrak.cfg"
    cfg_section = 'TrakStar'
    
    def __init__(self, measurement_rate = 80,max_range = 36, report_rate = 1,
                 power_line = 60, metric = True):

        """

        Parameter
        ---------
            measurement_rate in Hz: 20.0 < rate < 255.0
            max_range: valid values (in inches): 36.0, 72.0, 144.0
            metric: True (data in mm) or False (data in inches)
            power_line in Hz: 50.0 or 60.0 (frequency of the AC power source)
            report_rate: (int), between 1 and 127 --> report every 2nd, 3rd, etc. value

        """

        self.measurement_rate = measurement_rate
        self.max_range = max_range
        self.report_rate = report_rate
        self.power_line = power_line
        self.metric = metric

    def read(self):
        config = ConfigParser.ConfigParser()
        try:
            config.read(self.cfg_filename)
            self.measurement_rate = config.getint(TrakSTARSettings.cfg_section, 'measurement_rate')
            self.max_range = config.getint(TrakSTARSettings.cfg_section, 'max_range')
            self.report_rate = config.getint(TrakSTARSettings.cfg_section, 'report_rate')
            self.power_line = config.getint(TrakSTARSettings.cfg_section, 'power_line')
            self.metric = config.getboolean(TrakSTARSettings.cfg_section, 'metric')
        except:
            print "Creating settings file: ", TrakSTARSettings.cfg_filename
            self.save()
            return False
        return True

    def save(self):
        config = ConfigParser.RawConfigParser()
        config.add_section(self.cfg_section)
        config.set(self.cfg_section, "measurement_rate", self.measurement_rate)
        config.set(self.cfg_section, "max_range", self.max_range)
        config.set(self.cfg_section, "report_rate", self.report_rate)
        config.set(self.cfg_section, "power_line", self.power_line)
        config.set(self.cfg_section, "metric", self.metric)
        with open(self.cfg_filename, 'wb') as configfile:
            config.write(configfile)


class TrakSTARInterface(object):
    """ The trakSTAR interface"""

    def __init__(self):
        self._record = api.DOUBLE_POSITION_ANGLES_TIME_Q_RECORD_AllSensors_Four()
        self._precord = ctypes.pointer(self._record)
        self._file = None
        self._write_quality = None
        self._write_angles = None
        self._write_udp = None

        self.filename = None
        self.directory = None
        self.system_configuration = None
        self.attached_sensors = None
        self._init_time = None
        self._is_init = False

        self.udp = UDPConnection()
        print self.udp

    def __del__(self):
        self.close(ignore_error=True)

    def close(self, ignore_error=True):
        self.close_data_file()
        if not self.is_init:
            return
        print "* closing trakstar"
        self.attached_sensors = None
        self.system_configuration = None
        error_code = api.CloseBIRDSystem()
        if error_code != 0 and not ignore_error:
            self.error_handler(error_code)
        self._is_init = False

    def open_data_file(self, file_settings):
        """if data file is open, data will be recorded

        Parameters
        -----------
        file_settings: trakstar_data_file_settings

        """
        self._write_angles = file_settings.write_angles
        self._write_quality = file_settings.write_quality
        self._write_cpu_times = file_settings.write_cpu_times
        self._write_udp = file_settings.write_udp
        if not os.path.isdir(file_settings.directory):
            os.mkdir(file_settings.directory)
        self.close_data_file()

        if file_settings.filename is None or\
                        len(file_settings.filename) == 0:
            filename = "pytrak_recording"
        while True:
            if time_stamp_filename:
                self.filename = filename + "_" + strftime("%Y%m%d%H%M", localtime())\
                            + file_settings.suffix
            else:
                self.filename = filename + file_settings.suffix

            if os.path.isfile(file_settings.directory + os.path.sep + self.filename):
                #
                print "data file already exists, using time_stamp"
                time_stamp_filename = True
            else:
                break


        self.directory = file_settings.directory
        self._file = open(file_settings.directory + os.path.sep + self.filename, 'w+')
        if len(file_settings.comment_line)>0:
            self._file.write("#" + file_settings.comment_line + "\n")
        varnames = "time,sensor,x,y,z"
        if self._write_angles:
            varnames += ",a,e,r"
        if self._write_quality:
            varnames += ",quality"
        if self._write_udp:
            varnames += ",udp"
        if self._write_cpu_times:
            varnames += ",cpu_time"

        self._file.write(varnames + "\n")

    def close_data_file(self):
        """ close the file"""
        if self._file is not None:
            self._file.close()

    def initialize(self):
        if self.is_init:
            return
        print "* Initializing trakstar ..."
        error_code = api.InitializeBIRDSystem()
        if error_code != 0:
            self._error_handler(error_code)

        transmitter_id = ctypes.c_ushort(0)
        api.SetSystemParameter(api.SystemParameterType.SELECT_TRANSMITTER,
                               ctypes.pointer(transmitter_id), 2)

        # read in System configuration
        self.read_configurations(print_configuration=True)

        # set sensors
        for x in range(self.system_configuration.numberSensors):
            api.SetSensorParameter(ctypes.c_ushort(x),
                                   api.SensorParameterType.DATA_FORMAT,
                ctypes.pointer(api.DataFormatType.DOUBLE_POSITION_ANGLES_TIME_Q),
                                   4)
        self.reset_timer()
        self._is_init = True

    def reset_timer(self):
        self._init_time = time()

    @property
    def is_init(self):
        """Returns True if trakstar is initialized"""
        return self._is_init

    def _error_handler(self, error_code):
        print "** Error: ", error_code
        txt = " " * 500
        pbuffer = ctypes.c_char_p(txt)
        api.GetErrorText(error_code, pbuffer, ctypes.c_int(500),
                         api.MessageType.VERBOSE_MESSAGE)
        print pbuffer.value
        self.close(ignore_error=True)
        raise RuntimeError("** trakSTAR Error")


    def get_synchronous_data_dict(self, write_data_file=True):
        """polling data"""
        error_code = api.GetSynchronousRecord(api.ALL_SENSORS,
                                              self._precord, 4 * 1 * 64)
        cpu_time = int((time() - self._init_time) * 1000)
        trakstar_time = int((self._record.time0 - self._init_time) * 1000)
        if error_code != 0:
            self._error_handler(error_code)

        udp_data = self.udp.poll()

        # convert2data_dict
        d = {}
        d["time"] = trakstar_time
        d["cpu_time"] = cpu_time
        if 1 in self.attached_sensors:
            d[1] = np.array([self._record.x0, self._record.y0, self._record.z0,
                             self._record.a0, self._record.e0, self._record.r0,
                             self._record.quality0])
        if 2 in self.attached_sensors:
            d[2] = np.array([self._record.x1, self._record.y1, self._record.z1,
                             self._record.a1, self._record.e1, self._record.r1,
                             self._record.quality1])
        if 3 in self.attached_sensors:
            d[3] = np.array([self._record.x2, self._record.y2, self._record.z2,
                             self._record.a2, self._record.e2, self._record.r2,
                             self._record.quality2])
        if 4 in self.attached_sensors:
            d[4] = np.array([self._record.x3, self._record.y3, self._record.z3,
                             self._record.a3, self._record.e3, self._record.r3,
                             self._record.quality3])

        if udp_data is None:
            d["udp"] = ""
        else:
            d["udp"] = udp_data

        if self._file is not None and write_data_file:
            self._file.write(data_dict2string(d,
                               angles=self._write_angles,
                               quality=self._write_quality,
                               udp=self._write_udp,
                               cpu_times=self._write_cpu_times) + "\n")

        return d

    def read_configurations(self, print_configuration=True):
        """read system and sensor configuration from device"""

        #system configuration
        sysconf = api.SYSTEM_CONFIGURATION()
        psys_conf = ctypes.pointer(sysconf)

        # report SystemConfiguration
        error_code = api.GetBIRDSystemConfiguration(psys_conf)
        if error_code != 0:
            self._error_handler(error_code)
        self.system_configuration = sysconf

        report_rate = 0
        # TODO report rate is not read out yet
        #report_rate = ctypes.c_ubyte()
        #print report_rate
        #error_code = api.GetSystemParameter(api.SystemParameterType.REPORT_RATE,
        #                                    ctypes.pointer(report_rate), 2)
        #if error_code != 0:
        #    self._error_handler(error_code)
        #print report_rate



        # read attached sensors config
        sensor_conf = api.SENSOR_CONFIGURATION()
        psensor_conf = ctypes.pointer(sensor_conf)
        attached_sensors = []
        for cnt in range(self.system_configuration.numberSensors):
            error_code = api.GetSensorConfiguration(ctypes.c_ushort(cnt),
                                                    psensor_conf)
            if error_code != 0:
                self._error_handler(error_code)
            elif sensor_conf.attached:
                attached_sensors.append(cnt + 1)
        self.attached_sensors = attached_sensors

        if print_configuration:
            print TrakSTARInterface.configuration_text(self.attached_sensors,
                                 sysconf.measurementRate, sysconf.maximumRange,
                                 bool(sysconf.metric), sysconf.powerLineFrequency,
                                 report_rate)

    def set_system_configuration(self, trakstar_settings, print_configuration=True):
        """
        trakstar_settings: TrakSTARSetting
        """

        print "* setting system configuration"

        mR = ctypes.c_double(trakstar_settings.measurement_rate)
        max_range = ctypes.c_double(trakstar_settings.max_range)
        metric = ctypes.c_int(int(trakstar_settings.metric))
        power_line = ctypes.c_double(trakstar_settings.power_line)
        report_rate = ctypes.c_ushort(trakstar_settings.report_rate)

        error_code = api.SetSystemParameter(
            api.SystemParameterType.MEASUREMENT_RATE,
            ctypes.pointer(mR), 8)
        if error_code != 0:
            self._error_handler(error_code)
        error_code = api.SetSystemParameter(
            api.SystemParameterType.MAXIMUM_RANGE,
            ctypes.pointer(max_range), 8)
        if error_code != 0:
            self._error_handler(error_code)
        error_code = api.SetSystemParameter(api.SystemParameterType.METRIC,
                                            ctypes.pointer(metric), 4)
        if error_code != 0:
            self._error_handler(error_code)
        error_code = api.SetSystemParameter(
            api.SystemParameterType.POWER_LINE_FREQUENCY,
            ctypes.pointer(power_line), 8)
        if error_code != 0:
            self._error_handler(error_code)
        error_code = api.SetSystemParameter(api.SystemParameterType.REPORT_RATE,
                                            ctypes.pointer(report_rate), 2)
        if error_code != 0:
            self._error_handler(error_code)

        self.read_configurations(print_configuration=print_configuration)

    @staticmethod
    def configuration_text(attached_sensors, measurementRate, maximumRange,
                           metric, powerLineFrequency, reportRate):
        """Creates text from configuration"""
        txt = ""
        txt = txt + "attached sensors: " + repr(attached_sensors)
        txt = txt + "\nmaximum range: " + str(maximumRange) + " inches"
        txt = txt + "\nmetric data reporting: " + str(bool(metric))
        txt = txt + "\npower line frequency: " + str(powerLineFrequency) + " Hz"
        txt = txt + "\nreport rate: " +str(reportRate)
        return txt


class TrakSTARRecordingProcess(Process):

    def __init__(self):
        """
        Control process with the following events
            request_stop: quit recording
            request_do_polling : start and pause polling

            flag_is_initialized: indicates init status

        Queues
            command_queue: received data

        """
        super(TrakSTARRecordingProcess, self).__init__()

        self.request_stop = Event()
        self.request_do_polling = Event()
        self.flag_is_initialized = Event()

        self.command_queue = Queue()
        self._data_queue = Queue()

        self._attached_sensors = Value('b', 0)
        atexit.register(self.request_stop.set)

    @property
    def attached_sensors(self):
        return self._attached_sensors.value

    def get_data(self):
        """Returns an array with all available queued data
        """

        data_array = []
        while True:
            try:
                data_array.append(self._data_queue.get_nowait())
            except:
                break
        return data_array

    def run(self):
        trakstar = TrakSTARInterface()
        self.flag_is_initialized.clear()
        trakstar.initialize()

        if trakstar.is_init:
            self.flag_is_initialized.set()
            self._attached_sensors.value = trakstar.attached_sensors
            trakstar.reset_timer()

            while not self.request_stop.is_set():
                if self.request_do_polling.is_set():
                    data = trakstar.get_synchronous_data_dict()
                    self._data_queue.put_not_wait(data)
                else:
                    self.request_do_polling.wait(timeout=0.2)

                # commands
                try:
                    command = self.command_queue.get_notwait()
                except:
                    command = None

                if isinstance(command, TrakSTARSettings):
                    # change settings
                    self.request_do_polling.clear() # pause
                    trakstar.set_system_configuration(
                                    trakstar_settings = command,
                                    print_configuration=True)
                    self._attached_sensors.value = trakstar.attached_sensors
                elif isinstance(command, TrakSTARDataFileSettings):
                    # open data file
                    trakstar.open_data_file(file_settings=command)

        trakstar.close()

