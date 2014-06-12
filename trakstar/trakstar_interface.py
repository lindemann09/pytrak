import ctypes
import atc3dg_functions as api
#import time

class TrakSTARInterface(object):

    def __init__(self):
        self._record = api.DOUBLE_POSITION_ANGLES_TIME_Q_RECORD_AllSensors_Four()
        self._precord = ctypes.pointer(self._record)
        self.system_configuration = None
        self.attached_sensors = None
        self.init_time = None
        
    def __del__(self):
        self.close(ignore_error=True)
    
    def close(self, ignore_error=False):
        self.system_configuration = None
        self.attached_sensors = None
        self.init_time = None
        error_code = api.CloseBIRDSystem()
        if error_code!=0 and not ignore_error:
            self.error_handler(error_code)

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
        self.system_configuration = api.SYSTEM_CONFIGURATION()
        psys_conf = ctypes.pointer(self.system_configuration)
        api.GetBIRDSystemConfiguration(psys_conf)
        print "n sensors ", self.system_configuration.numberSensors
        print "n boards ", self.system_configuration.numberBoards

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
        #self.init_time = time.time()
        print "Done."

    def is_init(self):
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
    def data2string(data_dict, angles=False, quality=False, time=True):
        txt = ""
        for sensor in range(4):
            if data_dict.has_key(sensor):
                if time:
                    txt = txt + "{0},".format(data_dict["time"])
                txt = txt + "%d,%.4f,%.4f,%.4f" % (sensor, data_dict[sensor][0],
                                         data_dict[sensor][1], data_dict[sensor][2])
                if angles:
                    txt = txt + ",%.4f,%.4f,%.4f" % (data_dict[sensor][3],
                                                 data_dict[sensor][4], data_dict[sensor][5])
                if quality:
                    txt = txt + ",{0}".format(data_dict[sensor][6])    
                txt = txt + "\n"          
        return txt[:-1]

    def getSynchronousRecordDataDict(self, init_time):
        error_code = api.GetSynchronousRecord(api.ALL_SENSORS,
                                    self._precord, 4 * 1 * 64)     
        if error_code!=0:
            self._error_handler(error_code)
        # convert2data_dict
        d = {}
        d["time"] = int((self._record.time0 - init_time) * 1000)
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
        return d
    

    def SetSystemConfiguration(self, system_configuration):
        #TODO
        pass
