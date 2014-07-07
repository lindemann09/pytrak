"""TrakSTARInterface"""
from pytrak.trakstar import atc3dg_functions as api

__author__ = 'Raphael Wallroth <rwallroth@uni-potsdam.de>, \
Oliver Lindemann <oliver.lindemann@cognitive-psychology.eu>'

import os
import ctypes
from time import localtime, strftime, time
import atexit
import numpy as np
from udp_connection import UDPConnection


class TrakSTARInterface(object):
    def __init__(self):
        self._record = api.DOUBLE_POSITION_ANGLES_TIME_Q_RECORD_AllSensors_Four()
        self._precord = ctypes.pointer(self._record)
        self._file = None
        self._write_quality = None
        self._write_angles = None
        self._write_udp = None
        self._last_cpu_time = 0

        self.filename = None
        self.directory = None
        self.system_configuration = None
        self.attached_sensors = None
        self.init_time = None
        self._is_init = False

        self.udp = UDPConnection()
        print self.udp
        atexit.register(self.close)

    def __del__(self):
        self.close(ignore_error=True)

    def close(self, ignore_error=True):
        if not self.is_init:
            return
        print "* closing trakstar"
        self.close_data_file()
        self.attached_sensors = None
        self.system_configuration = None
        error_code = api.CloseBIRDSystem()
        if error_code != 0 and not ignore_error:
            self.error_handler(error_code)
        self._is_init = False

    def open_data_file(self, filename, directory="data", suffix=".csv",
                       time_stamp_filename=True, write_angles=False,
                       write_quality=False, write_cpu_times=False,
                       write_udp=True, comment_line=""):
        """if data file is open, data will be recorded"""
        self._write_angles = write_angles
        self._write_quality = write_quality
        self._write_cpu_times = write_cpu_times
        self._write_udp = write_udp
        if not os.path.isdir(directory):
            os.mkdir(directory)
        self.close_data_file()

        if filename is None or len(filename) == 0:
            filename = "pytrak_recording"
        if time_stamp_filename:
            filename = filename + "_" + strftime("%Y%m%d%H%M", localtime())
        filename = filename + suffix
        self.filename = filename
        self.directory = directory
        self._file = open(directory + os.path.sep + filename, 'w+')
        if len(comment_line)>0:
            self._file.write("#" + comment_line + "\n")
        varnames = "time,sensor,x,y,z"
        if write_angles:
            varnames += ",a,e,r"
        if write_quality:
            varnames += ",quality"
        if write_udp:
            varnames += ",udp"
        if write_cpu_times:
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
        self.init_time = time()

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


    @staticmethod
    def data2string(data_dict, angles=False, quality=False, times=True,
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
                                                     data_dict[sensor][4], data_dict[sensor][5])
                if quality:
                    txt = txt + ",{0}".format(data_dict[sensor][6])
                if udp:
                    txt = txt + ",{0}".format(data_dict["udp"])
                if cpu_times:
                    txt = txt + ",{0}".format(data_dict["cpu_time"])

                txt = txt + "\n"
        return txt[:-1]

    def get_synchronous_data_dict(self, write_data_file=True):
        """polling data"""
        error_code = api.GetSynchronousRecord(api.ALL_SENSORS,
                                              self._precord, 4 * 1 * 64)
        cpu_time = int((time() - self.init_time) * 1000)
        sampling_delay = cpu_time - self._last_cpu_time
        self._last_cpu_time = cpu_time
        #if sampling_delay > 10:
        #    print sampling_delay
        trakstar_time = int((self._record.time0 - self.init_time) * 1000)
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
            d["udp"] = "0"
        else:
            d["udp"] = udp_data

        if self._file is not None and write_data_file:
            self._file.write(TrakSTARInterface.data2string(d,
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
        api.GetBIRDSystemConfiguration(psys_conf)
        self.system_configuration = sysconf

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
            print "  attached sensors", self.attached_sensors
            print "  measurement rate:", sysconf.measurementRate, " Hz."
            print "  maximum range:", sysconf.maximumRange, " inches."
            print "  metric data reporting:", bool(sysconf.metric)
            print "  power line frequency:", sysconf.powerLineFrequency, " Hz."
            #print "  report rate:", sysconf.reportRate


    def set_system_configuration(self, measurement_rate=80, max_range=36,
                                 metric=True, power_line=60, report_rate=1,
                                 print_configuration=True):
        """
        measurement_rate in Hz: 20.0 < rate < 255.0
        max_range: valid values (in inches): 36.0, 72.0, 144.0
        metric: True (data in mm) or False (data in inches)
        power_line in Hz: 50.0 or 60.0 (frequency of the AC power source)
        report_rate: (int), between 1 and 127 --> report every 2nd, 3rd, etc. value
        """

        print "* setting system configuration"

        mR = ctypes.c_double(measurement_rate)
        max_range = ctypes.c_double(max_range)
        metric = ctypes.c_int(int(metric))
        power_line = ctypes.c_double(power_line)
        report_rate = ctypes.c_ushort(report_rate)

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
