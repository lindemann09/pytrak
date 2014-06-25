"""TrakSTARInterface"""

__author__ = 'Oliver Lindemann <oliver.lindemann@cognitive-psychology.eu>,\
Raphael Wallroth <>'
__version__ = '0.2.3'

import os
import ctypes
import time
import atexit
import atc3dg_functions as api
from udp_connection import UDPConnection

class TrakSTARInterface(object):

    def __init__(self):
        self._record = api.DOUBLE_POSITION_ANGLES_TIME_Q_RECORD_AllSensors_Four()
        self._precord = ctypes.pointer(self._record)
        self.attached_sensors = None
        self.init_time = None
        self._file = None
        self._write_quality = None
        self._write_angles = None
        self._write_udp = None
        self.system_configuration = None
        self.udp = UDPConnection()
        atexit.register(self.close)

    def __del__(self):
        self.close(ignore_error=True)

    def close(self, ignore_error=True):
        print "closing trakstar"
        self.close_data_file()
        self.attached_sensors = None
        self.init_time = None
        self.system_configuration = None
        error_code = api.CloseBIRDSystem()
        if error_code!=0 and not ignore_error:
            self.error_handler(error_code)

    def open_data_file(self, filename, directory="data", suffix = ".csv",
                       time_stamp_filename=True, write_angles=False,
                       write_quality=False, write_udp=True):
        """if data file is open, data will be recorded"""
        self._write_angles = write_angles
        self._write_quality = write_quality
        self._write_udp = write_udp
        if not os.path.isdir(directory):
            os.mkdir(directory)
        self.close_data_file()

        fullname = directory +  os.path.sep + filename
        if time_stamp_filename:
            fullname = fullname +"_" + \
                     time.strftime("%Y%m%d%H%M", time.localtime())
        fullname = fullname + suffix
        self._file = open(fullname, 'w+')
        self._file.write("# Motion tracking data recorded with " +\
                             "PyTrak interface " + str(__version__) + \
                         "\n")
        varnames = "time,sensor,x,y,z"
        if write_angles:
            varnames += ",a,e,r"
        if write_quality:
            varnames += ",quality"
        if write_udp:
            varnames += ",udp"

        self._file.write(varnames + "\n")

    def close_data_file(self):
        """ close the file"""
        if self._file is not None:
            self._file.close()

    def initialize(self):
        if self.is_init():
            return
        print "Initializing trakstar ..."
        error_code = api.InitializeBIRDSystem()
        if error_code!=0:
            self._error_handler(error_code)

        transmitter_id = ctypes.c_ushort(0)
        api.SetSystemParameter(api.SystemParameterType.SELECT_TRANSMITTER,
                           ctypes.pointer(transmitter_id), 2)

        # read in System configuration
        self.read_system_configuration(print_configuration = True)

        # get attached sensors
        sensor_conf = api.SENSOR_CONFIGURATION()
        psensor_conf = ctypes.pointer(sensor_conf)
        attached_sensors = []
        for cnt in range(self.system_configuration.numberSensors):
            error_code = api.GetSensorConfiguration(ctypes.c_ushort(cnt),
                                        psensor_conf)
            print sensor_conf.attached, sensor_conf.serialNumber

            if error_code!=0:
                self._error_handler(error_code)
            elif sensor_conf.attached:
                attached_sensors.append(cnt)
        self.attached_sensors = attached_sensors
        print "attached sensors", self.attached_sensors

        # set sensors
        for x in range(self.system_configuration.numberSensors):
            api.SetSensorParameter(ctypes.c_ushort(x),
                api.SensorParameterType.DATA_FORMAT,
                ctypes.pointer(api.DataFormatType.DOUBLE_POSITION_ANGLES_TIME_Q),
                4)
        self.init_time = time.time()
        print "Done."

    def is_init(self):
        """Returns if trak ist initialized"""
        return (self.init_time is not None)

    def _error_handler(self, error_code):
        print "Error: ", error_code
        txt =  " " * 500
        pbuffer = ctypes.c_char_p(txt)
        api.GetErrorText(error_code, pbuffer, ctypes.c_int(500),
                            api.MessageType.VERBOSE_MESSAGE)
        print pbuffer.value
        self.close(ignore_error=True)
        raise RuntimeError("trakSTAR Error")


    @staticmethod
    def data2string(data_dict, angles=False, quality=False, times=True,
            udp=True):
        txt = ""
        for sensor in range(4):
            if data_dict.has_key(sensor):
                if times:
                    txt = txt + "{0},".format(data_dict["time"])
                txt = txt + "%d,%.4f,%.4f,%.4f" % \
                                    (sensor+1, data_dict[sensor][0],
                                    data_dict[sensor][1], data_dict[sensor][2])
                if angles:
                    txt = txt + ",%.4f,%.4f,%.4f" % (data_dict[sensor][3],
                                    data_dict[sensor][4], data_dict[sensor][5])
                if quality:
                    txt = txt + ",{0}".format(data_dict[sensor][6])
                if udp:
                    txt = txt + ",{0}".format(data_dict["udp"])

                txt = txt + "\n"
        return txt[:-1]

    def get_synchronous_data_dict(self):
        """polling data"""
        error_code = api.GetSynchronousRecord(api.ALL_SENSORS,
                                    self._precord, 4 * 1 * 64)
        time = int((self._record.time0 - self.init_time) * 1000)
        if error_code!=0:
            self._error_handler(error_code)

        udp_data = self.udp.poll_last_data()

        # convert2data_dict
        d = {}
        d["time"] = time
        if 0 in self.attached_sensors:
            d[0] = [self._record.x0, self._record.y0, self._record.z0,
                   self._record.a0, self._record.e0, self._record.r0,
                   self._record.quality0]
        if 1 in self.attached_sensors:
            d[1] = [self._record.x1, self._record.y1, self._record.z1,
                   self._record.a1, self._record.e1, self._record.r1,
                    self._record.quality1]
        if 2 in self.attached_sensors:
            d[2] = [self._record.x2, self._record.y2, self._record.z2,
                    self._record.a2, self._record.e2, self._record.r2,
                    self._record.quality2]
        if 3 in self.attached_sensors:
            d[3] = [self._record.x3, self._record.y3, self._record.z3,
                   self._record.a3, self._record.e3, self._record.r3,
                    self._record.quality3]
        d["udp"] = udp_data

        if self._file is not None:
            self._file.write(TrakSTARInterface.data2string(d,
                        angles = self._write_angles,
                        quality = self._write_quality,
                        udp = self._write_udp) + "\n")

        return d

    def read_system_configuration(self, print_configuration = True):
        """read system configuration from device"""
        sysconf = api.SYSTEM_CONFIGURATION()
        psys_conf = ctypes.pointer(sysconf)
        api.GetBIRDSystemConfiguration(psys_conf)
        if print_configuration:
            print "n sensors ", sysconf.numberSensors
            print "n boards ", sysconf.numberBoards
            print "measurement rate:", sysconf.measurementRate, " Hz."
            print "maximum range:", sysconf.maximumRange, " inches."
            print "metric data reporting: ", sysconf.metric
            print "power line frequency: ", sysconf.powerLineFrequency, " Hz."
        self.system_configuration  = sysconf


    def set_system_configuration(self, measurement_rate=80,
                                max_range=36, metric=True, power_line=60,
                               print_configuration = True):
        """
        measurement_rate in Hz: 20.0 < rate < 255.0
        max_range: valid values (in inches): 36.0, 72.0, 144.0
        metric: True (data in mm) or False (data in inches)
        power_line in Hz: 50.0 or 60.0 (frequency of the AC power source)
        """

        print "setting system configuration"

        mR = ctypes.c_double(measurement_rate)
        max_range = ctypes.c_double(max_range)
        metric = ctypes.c_int(int(metric))
        power_line = ctypes.c_double(power_line)

        error_code = api.SetSystemParameter(
                            api.SystemParameterType.MEASUREMENT_RATE,
                            ctypes.pointer(mR), 8)
        if error_code!=0:
            self._error_handler(error_code)
        error_code = api.SetSystemParameter(
                            api.SystemParameterType.MAXIMUM_RANGE,
                            ctypes.pointer(max_range), 8)
        if error_code!=0:
            self._error_handler(error_code)
        error_code = api.SetSystemParameter(api.SystemParameterType.METRIC,
                           ctypes.pointer(metric), 4)
        if error_code!=0:
            self._error_handler(error_code)
        error_code = api.SetSystemParameter(
                           api.SystemParameterType.POWER_LINE_FREQUENCY,
                           ctypes.pointer(power_line), 8)
        if error_code!=0:
            self._error_handler(error_code)

        self.read_system_configuration(print_configuration=print_configuration)
