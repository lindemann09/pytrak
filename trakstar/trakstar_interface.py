import time
import ctypes
import atc3dg_functions as api

def print_system_configuration(sys_conf):
    print "n sensors ", sys_conf.numberSensors
    print "n boards ", sys_conf.numberBoards
    
def error_handler(error_code):
    print "Error: ", error_code
    txt =  " " * 500
    pbuffer = ctypes.c_char_p(txt)
    api.GetErrorText(error_code, pbuffer, ctypes.c_int(500), 
                        api.MessageType.VERBOSE_MESSAGE)
    print pbuffer.value
    api.CloseBIRDSystem()
    raise RuntimeError("trakSTAR Error")
    
def convert2data_dict(precord, attached_sensors):
    global import_ctime
    record = precord.contents
    d = {}
    d["time"] = int((record.time0 - import_ctime) * 1000)
    if 0 in attached_sensors:
        d[0] = [record.x0, record.y0, record.z0,
               record.a0, record.e0, record.r0, record.quality0]
    if 1 in attached_sensors:
        d[1] = [record.x1, record.y1, record.z1,
               record.a1, record.e1, record.r1, record.quality1]
    if 2 in attached_sensors:
        d[2] = [record.x2, record.y2, record.z2,
                       record.a2, record.e2, record.r2, record.quality2]
    if 3 in attached_sensors:
        d[3] = [record.x3, record.y3, record.z3,
               record.a3, record.e3, record.r3, record.quality3]
    return d

def data_dict2string(data_dict, angles=False, quality=False, time=True):
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


def get_configuration():
    """Returns system_configuration and attchedSensorsIDs (list of int)
    """
    sys_conf = api.SYSTEM_CONFIGURATION()
    psys_conf = ctypes.pointer(sys_conf)
    api.GetBIRDSystemConfiguration(psys_conf)
    # attached sensors
    sensor_conf = api.SENSOR_CONFIGURATION()
    psensor_conf = ctypes.pointer(sensor_conf)
    attached_sensors = []
    for cnt in range(sys_conf.numberSensors):
        error_code = api.GetSensorConfiguration(ctypes.c_ushort(cnt),
                                    psensor_conf)
        print sensor_conf.attached, sensor_conf.serialNumber
        
        if error_code!=0:
            error_handler(error_code)
        elif sensor_conf.attached:
            attached_sensors.append(cnt)       
    return sys_conf, attached_sensors

def init_trakStar():
    print "Initialize trakstar"
    error_code = api.InitializeBIRDSystem()
    if error_code!=0:
        error_handler(error_code)
        
    print "Select transmitter 0"
    transmitter_id = ctypes.c_ushort(0)
    api.SetSystemParameter(api.SystemParameterType.SELECT_TRANSMITTER,
                       ctypes.pointer(transmitter_id), 2)

    sys_conf, attached_sensors = get_configuration()
    print_system_configuration(sys_conf)
    print "attached sensors", attached_sensors

    for x in range(sys_conf.numberSensors):
        print "init sensor", x
        api.SetSensorParameter(ctypes.c_ushort(x),
                        api.SensorParameterType.DATA_FORMAT,
                        ctypes.pointer(api.DataFormatType.DOUBLE_POSITION_ANGLES_TIME_Q),
                        4)
    print "Done."
    return sys_conf, attached_sensors

def getSynchronousRecordDataDict(attached_sensors):
    record = api.DOUBLE_POSITION_ANGLES_TIME_Q_RECORD_AllSensors_Four()
    precord = ctypes.pointer(record)
    error_code = api.GetSynchronousRecord(api.ALL_SENSORS,
                                precord, 4 * 1 * 64)     
    if error_code!=0:
        error_handler(error_code)
    return convert2data_dict(precord, attached_sensors)


def close_trakStar():
    print "Closing trakSTAR"
    error_code = api.CloseBIRDSystem()
    if error_code!=0:
        error_handler(error_code)
    
import_ctime = time.time()

