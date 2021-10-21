""" Interface for ATC3DG.dll (.so)
Definitions of constants and structures required
(adapted from ATC3DG.h)

Author: O. Lindemann
"""

import ctypes as ct

# ###########################################################
# ENUMERATED CONSTANTS
############################################################
enum_type = ct.c_ushort
device_status = ct.c_ulong

ALL_SENSORS = 0xffff

#*****************************************************************************
#
#    ERROR MESSAGE format is as follows:
#    ===================================
#
#    All commands return a 32-bit integer with the following bit definitions:
#
#   3 3 2 2 2 2 2 2 2 2 2 2 1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0
#   1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0
#  +-+-+-+-+-+-+-----------+-------+-------------------------------+
#  |E|W|X|R|B|M|  Reserved |Address|             Code              |
#  +-+-+-+-+-+-+-----------+-------+-------------------------------+
#
#  where
#
#    E - indicates an ERROR
#    (Operation either cannot or will not proceed as intended
#    e.g. EEPROM error of some kind. Requires hardware reset
#    of system and/or replacement of hardware)
#    W - indicates a WARNING
#    (Operation may proceed but remedial action needs to be taken
#    e.g. Sensor has been removed. Fix by replacing Sensor)
#      X - indicates Transmitter related message
#      R - indicates Sensor related message
#    (If neither X nor R is set then the message is a SYSTEM message)
#    B - indicates message originated in the BIRD hardware
#    M - indicates there are more messages pending (no longer used)
#
#    Address gives the index number of the device generating the message
#    (Driver and system messages always have address 0)
#
#      Code - is the status code as enumerated in BIRD_ERROR_CODES
#
#*****************************************************************************
class BIRD_ERROR_CODES:
    (BIRD_ERROR_SUCCESS,  #00 < > No error
     BIRD_ERROR_PCB_HARDWARE_FAILURE,  #01 < > indeterminate failure on PCB
     BIRD_ERROR_TRANSMITTER_EEPROM_FAILURE,  #02 <I> transmitter bad eeprom
     BIRD_ERROR_SENSOR_SATURATION_START,  #03 <I> sensor has gone into saturation
     BIRD_ERROR_ATTACHED_DEVICE_FAILURE,  #04 <O> either a sensor or transmitter reports bad
     BIRD_ERROR_CONFIGURATION_DATA_FAILURE,  #05 <O> device EEPROM detected but corrupt
     BIRD_ERROR_ILLEGAL_COMMAND_PARAMETER,  #06 < > illegal PARAMETER_TYPE passed to driver
     BIRD_ERROR_PARAMETER_OUT_OF_RANGE,  #07 < > PARAMETER_TYPE legal, but PARAMETER out of range
     BIRD_ERROR_NO_RESPONSE,  #08 <O> no response at all from target card firmware
     BIRD_ERROR_COMMAND_TIME_OUT,  #09 < > time out before response from target board
     BIRD_ERROR_INCORRECT_PARAMETER_SIZE,  #10 < > size of parameter passed is incorrect
     BIRD_ERROR_INVALID_VENDOR_ID,  #11 <O> driver started with invalid PCI vendor ID
     BIRD_ERROR_OPENING_DRIVER,  #12 < > couldn't start driver
     BIRD_ERROR_INCORRECT_DRIVER_VERSION,  #13 < > wrong driver version found
     BIRD_ERROR_NO_DEVICES_FOUND,  #14 < > no BIRDs were found anywhere
     BIRD_ERROR_ACCESSING_PCI_CONFIG,  #15 < > couldn't access BIRDs config space
     BIRD_ERROR_INVALID_DEVICE_ID,  #16 < > device ID out of range
     BIRD_ERROR_FAILED_LOCKING_DEVICE,  #17 < > couldn't lock driver
     BIRD_ERROR_BOARD_MISSING_ITEMS,  #18 < > config space items missing
     BIRD_ERROR_NOTHING_ATTACHED,  #19 <O> card found but no sensors or transmitters attached
     BIRD_ERROR_SYSTEM_PROBLEM,  #20 <O> non specific system problem
     BIRD_ERROR_INVALID_SERIAL_NUMBER,  #21 <O> serial number does not exist in system
     BIRD_ERROR_DUPLICATE_SERIAL_NUMBER,  #22 <O> 2 identical serial numbers passed in set command
     BIRD_ERROR_FORMAT_NOT_SELECTED,  #23 <O> data format not selected yet
     BIRD_ERROR_COMMAND_NOT_IMPLEMENTED,  #24 < > valid command, not implemented yet
     BIRD_ERROR_INCORRECT_BOARD_DEFAULT,  #25 < > incorrect response to reading parameter
     BIRD_ERROR_INCORRECT_RESPONSE,  #26 <O> response received, but data,values in error
     BIRD_ERROR_NO_TRANSMITTER_RUNNING,  #27 < > there is no transmitter running
     BIRD_ERROR_INCORRECT_RECORD_SIZE,  #28 < > data record size does not match data format size
     BIRD_ERROR_TRANSMITTER_OVERCURRENT,  #29 <I> transmitter over-current detected
     BIRD_ERROR_TRANSMITTER_OPEN_CIRCUIT,  #30 <I> transmitter open circuit or removed
     BIRD_ERROR_SENSOR_EEPROM_FAILURE,  #31 <I> sensor bad eeprom
     BIRD_ERROR_SENSOR_DISCONNECTED,  #32 <I> previously good sensor has been removed
     BIRD_ERROR_SENSOR_REATTACHED,  #33 <I> previously good sensor has been reattached
     BIRD_ERROR_NEW_SENSOR_ATTACHED,  #34 <O> new sensor attached
     BIRD_ERROR_UNDOCUMENTED,  #35 <I> undocumented error code received from bird
     BIRD_ERROR_TRANSMITTER_REATTACHED,  #36 <I> previously good transmitter has been reattached
     BIRD_ERROR_WATCHDOG,  #37 < > watchdog timeout
     BIRD_ERROR_CPU_TIMEOUT_START,  #38 <I> CPU ran out of time executing algorithm (start)
     BIRD_ERROR_PCB_RAM_FAILURE,  #39 <I> BIRD on-board RAM failure
     BIRD_ERROR_INTERFACE,  #40 <I> BIRD PCI interface error
     BIRD_ERROR_PCB_EPROM_FAILURE,  #41 <I> BIRD on-board EPROM failure
     BIRD_ERROR_SYSTEM_STACK_OVERFLOW,  #42 <I> BIRD program stack overrun
     BIRD_ERROR_QUEUE_OVERRUN,  #43 <I> BIRD error message queue overrun
     BIRD_ERROR_PCB_EEPROM_FAILURE,  #44 <I> PCB bad EEPROM
     BIRD_ERROR_SENSOR_SATURATION_END,  #45 <I> Sensor has gone out of saturation
     BIRD_ERROR_NEW_TRANSMITTER_ATTACHED,  #46 <O> new transmitter attached
     BIRD_ERROR_SYSTEM_UNINITIALIZED,  #47 < > InitializeBIRDSystem not called yet
     BIRD_ERROR_12V_SUPPLY_FAILURE,  #48 <I > 12V Power supply not within specification
     BIRD_ERROR_CPU_TIMEOUT_END,  #49 <I> CPU ran out of time executing algorithm (end)
     BIRD_ERROR_INCORRECT_PLD,  #50 < > PCB PLD not compatible with this API DLL
     BIRD_ERROR_NO_TRANSMITTER_ATTACHED,  #51 < > No transmitter attached to this ID
     BIRD_ERROR_NO_SENSOR_ATTACHED,  #52 < > No sensor attached to this ID

     # new error codes added 2/27/03
     # (Version 1,31,5,01)  multi-sensor, synchronized
     BIRD_ERROR_SENSOR_BAD,  #53 < > Non-specific hardware problem
     BIRD_ERROR_SENSOR_SATURATED,  #54 < > Sensor saturated error
     BIRD_ERROR_CPU_TIMEOUT,  #55 < > CPU unable to complete algorithm on current cycle
     BIRD_ERROR_UNABLE_TO_CREATE_FILE,  #56 < > Could not create and open file for saving setup
     BIRD_ERROR_UNABLE_TO_OPEN_FILE,  #57 < > Could not open file for restoring setup
     BIRD_ERROR_MISSING_CONFIGURATION_ITEM,  #58 < > Mandatory item missing from configuration file
     BIRD_ERROR_MISMATCHED_DATA,  #59 < > Data item in file does not match system value
     BIRD_ERROR_CONFIG_INTERNAL,  #60 < > Internal error in config file handler
     BIRD_ERROR_UNRECOGNIZED_MODEL_STRING,  #61 < > Board does not have a valid model string
     BIRD_ERROR_INCORRECT_SENSOR,  #62 < > Invalid sensor type attached to this board
     BIRD_ERROR_INCORRECT_TRANSMITTER,  #63 < > Invalid transmitter type attached to this board

     # new error code added 1/18/05
     # (Version 1.31.5.22)
     #    multi-sensor,
     #    synchronized-fluxgate,
     #    integrating micro-sensor,
     #    flat panel transmitter
     BIRD_ERROR_ALGORITHM_INITIALIZATION,  #64 < > Flat panel algorithm initialization failed

     # new error code for multi-sync
     BIRD_ERROR_LOST_CONNECTION,  #65 < > USB connection has been lost
     BIRD_ERROR_INVALID_CONFIGURATION,  #66 < > Invalid configuration

     # VPD error code
     BIRD_ERROR_TRANSMITTER_RUNNING) = list(map(enum_type, list(range(68))))  #67 < > TX running while reading/writing VPD

    BIRD_ERROR_MAXIMUM_VALUE = 0x7F  #         ## value = number of error codes ##


class MessageType:
    (SIMPLE_MESSAGE,  # short string describing error code
     VERBOSE_MESSAGE ) = list(map(enum_type, list(range(2))))  # long string describing error code


class TransmitterParameterType:
    (SERIAL_NUMBER_TX,  # attached transmitter's serial number
     REFERENCE_FRAME,  # structure of type DOUBLE_ANGLES_RECORD
     XYZ_REFERENCE_FRAME,  # boolean value to select/deselect mode
     VITAL_PRODUCT_DATA_TX,  # single byte parameter to be read/write from VPD section of xmtr EEPROM
     MODEL_STRING_TX,  # 11 byte null terminated character string
     PART_NUMBER_TX,  # 16 byte null terminated character string
     END_OF_TX_LIST) = list(map(enum_type, list(range(7))))


class SensorParameterType:
    (DATA_FORMAT,  # enumerated constant of type DATA_FORMAT_TYPE
     ANGLE_ALIGN,  # structure of type DOUBLE_ANGLES_RECORD
     HEMISPHERE,  # enumerated constant of type HEMISPHERE_TYPE
     FILTER_AC_WIDE_NOTCH,  # boolean value to select/deselect filter
     FILTER_AC_NARROW_NOTCH,  # boolean value to select/deselect filter
     FILTER_DC_ADAPTIVE,  # double value in range 0.0 (no filtering) to 1.0 (max)
     FILTER_ALPHA_PARAMETERS,  # structure of type ADAPTIVE_PARAMETERS
     FILTER_LARGE_CHANGE,  # boolean value to select/deselect filter
     QUALITY,  # structure of type QUALITY_PARAMETERS
     SERIAL_NUMBER_RX,  # attached sensor's serial number
     SENSOR_OFFSET,  # structure of type DOUBLE_POSITION_RECORD
     VITAL_PRODUCT_DATA_RX,  # single byte parameter to be read/write from VPD section of sensor EEPROM
     VITAL_PRODUCT_DATA_PREAMP,  # single byte parameter to be read/write from VPD section of preamp EEPROM
     MODEL_STRING_RX,  # 11 byte null terminated character string
     PART_NUMBER_RX,  # 16 byte null terminated character string
     MODEL_STRING_PREAMP,  # 11 byte null terminated character string
     PART_NUMBER_PREAMP,  # 16 byte null terminated character string
     END_OF_RX_LIST) = list(map(enum_type, list(range(18))))


class BoardParameterType:
    (SERIAL_NUMBER_PCB,  # installed board's serial number
     BOARD_SOFTWARE_REVISIONS,  # Extra SW_REV's added 10-5-06 JBD
     POST_ERROR_PCB,
     DIAGNOSTIC_TEST_PCB,
     VITAL_PRODUCT_DATA_PCB,  # single byte parameter to be read/write from VPD section of xmtr EEPROM
     MODEL_STRING_PCB,  # 11 byte null terminated character string
     PART_NUMBER_PCB,  # 16 byte null terminated character string
     END_OF_PCB_LIST_BRD) = list(map(enum_type, list(range(8))))


class SystemParameterType:
    (SELECT_TRANSMITTER,  # short int equal to transmitterID of selected transmitter
     POWER_LINE_FREQUENCY,  # double value (range is hardware dependent)
     AGC_MODE,  # enumerated constant of type AGC_MODE_TYPE
     MEASUREMENT_RATE,  # double value (range is hardware dependent)
     MAXIMUM_RANGE,  # double value (range is hardware dependent)
     METRIC,  # boolean value to select metric units for position
     VITAL_PRODUCT_DATA,
     POST_ERROR,
     DIAGNOSTIC_TEST,
     REPORT_RATE,  # single byte 1-127
     COMMUNICATIONS_MEDIA,  # Media structure
     LOGGING,  # Boolean
     RESET,  # Boolean
     AUTOCONFIG,  # BYTE 1-127
     END_OF_LIST) = list(map(enum_type, list(range(15))))  # end of list place holder


class CommunicationsMediaType:
    (USB,  # Auto select USB driver
     RS232,  # Force to RS232
     TCPIP) = list(map(enum_type, list(range(3))))  # Force to TCP/IP


class FilterOption:
    (NO_FILTER,
     DEFAULT_FLOCK_FILTER) = list(map(enum_type, list(range(2))))


class HemisphereType:
    (FRONT,
     BACK,
     TOP,
     BOTTOM,
     LEFT,
     RIGHT) = list(map(enum_type, list(range(6))))


class AgcModeType:
    (TRANSMITTER_AND_SENSOR_AGC,  # Old style normal addressing mode
     SENSOR_AGC_ONLY) = list(map(enum_type, list(range(2))))  # Old style extended addressing mode


class DataFormatType:
    (NO_FORMAT_SELECTED,

     # SHORT (integer) formats
     SHORT_POSITION,
     SHORT_ANGLES,
     SHORT_MATRIX,
     SHORT_QUATERNIONS,
     SHORT_POSITION_ANGLES,
     SHORT_POSITION_MATRIX,
     SHORT_POSITION_QUATERNION,

     # DOUBLE (floating point) formats
     DOUBLE_POSITION,
     DOUBLE_ANGLES,
     DOUBLE_MATRIX,
     DOUBLE_QUATERNIONS,
     DOUBLE_POSITION_ANGLES,  # system default
     DOUBLE_POSITION_MATRIX,
     DOUBLE_POSITION_QUATERNION,

     # DOUBLE (floating point) formats with time stamp appended
     DOUBLE_POSITION_TIME_STAMP,
     DOUBLE_ANGLES_TIME_STAMP,
     DOUBLE_MATRIX_TIME_STAMP,
     DOUBLE_QUATERNIONS_TIME_STAMP,
     DOUBLE_POSITION_ANGLES_TIME_STAMP,
     DOUBLE_POSITION_MATRIX_TIME_STAMP,
     DOUBLE_POSITION_QUATERNION_TIME_STAMP,

     # DOUBLE (floating point) formats with time stamp appended and quality #
     DOUBLE_POSITION_TIME_Q,
     DOUBLE_ANGLES_TIME_Q,
     DOUBLE_MATRIX_TIME_Q,
     DOUBLE_QUATERNIONS_TIME_Q,
     DOUBLE_POSITION_ANGLES_TIME_Q,
     DOUBLE_POSITION_MATRIX_TIME_Q,
     DOUBLE_POSITION_QUATERNION_TIME_Q,

     # These DATA_FORMAT_TYPE codes contain every format in a single structure
     SHORT_ALL,
     DOUBLE_ALL,
     DOUBLE_ALL_TIME_STAMP,
     DOUBLE_ALL_TIME_STAMP_Q,
     DOUBLE_ALL_TIME_STAMP_Q_RAW,  # this format contains a raw data matrix and
     # is for factory use only...

     # DOUBLE (floating point) formats with time stamp appended, quality # and button
     DOUBLE_POSITION_ANGLES_TIME_Q_BUTTON,
     DOUBLE_POSITION_MATRIX_TIME_Q_BUTTON,
     DOUBLE_POSITION_QUATERNION_TIME_Q_BUTTON,

     # New types for button and wrapper
     DOUBLE_POSITION_ANGLES_MATRIX_QUATERNION_TIME_Q_BUTTON,

     MAXIMUM_FORMAT_CODE) = list(map(enum_type, list(range(39))))


class BoardTypes:
    (ATC3DG_MEDSAFE,  # Standalone, DSP, 4 sensor
     PCIBIRD_STD1,  # single standard sensor
     PCIBIRD_STD2,  # dual standard sensor
     PCIBIRD_8mm1,  # single 8mm sensor
     PCIBIRD_8mm2,  # dual 8mm sensor
     PCIBIRD_2mm1,  # single 2mm sensor (microsensor)
     PCIBIRD_2mm2,  # dual 2mm sensor (microsensor)
     PCIBIRD_FLAT,  # flat transmitter, 8mm
     PCIBIRD_FLAT_MICRO1,  # flat transmitter, single TEM sensor (all types)
     PCIBIRD_FLAT_MICRO2,  # flat transmitter, dual TEM sensor (all types)
     PCIBIRD_DSP4,  # Standalone, DSP, 4 sensor
     PCIBIRD_UNKNOWN,  # default
     ATC3DG_BB) = list(map(enum_type, list(range(13))))  # BayBird


class DeviceTypes:
    (STANDARD_SENSOR,  # 25mm standard sensor
     TYPE_800_SENSOR,  # 8mm sensor
     STANDARD_TRANSMITTER,  # TX for 25mm sensor
     MINIBIRD_TRANSMITTER,  # TX for 8mm sensor
     SMALL_TRANSMITTER,  # "compact" transmitter
     TYPE_500_SENSOR,  # 5mm sensor
     TYPE_180_SENSOR,  # 1.8mm microsensor
     TYPE_130_SENSOR,  # 1.3mm microsensor
     TYPE_TEM_SENSOR,  # 1.8mm, 1.3mm, 0.Xmm microsensors
     UNKNOWN_SENSOR,  # default
     UNKNOWN_TRANSMITTER,  # default
     TYPE_800_BB_SENSOR,  # BayBird sensor
     TYPE_800_BB_STD_TRANSMITTER,  # BayBird standard TX
     TYPE_800_BB_SMALL_TRANSMITTER,  # BayBird small TX
     TYPE_090_BB_SENSOR) = list(map(enum_type, list(range(15))))  # Baybird 0.9 mm sensor


#################################################
# important structs
# not all struct from atc32dg.h
#################################################


class TRANSMITTER_CONFIGURATION(ct.Structure):
    _fields_ = [
        ('serialNumber', ct.c_long),
        ('boardNumber', ct.c_ushort),
        ('channelNumber', ct.c_ushort),
        ('DEVICE_TYPES', enum_type),
        ('attached', ct.c_int)]


class SENSOR_CONFIGURATION(ct.Structure):
    _fields_ = [
        ('serialNumber', ct.c_long),
        ('boardNumber', ct.c_ushort),
        ('channelNumber', ct.c_ushort),
        ('DEVICE_TYPES', enum_type),
        ('attached', ct.c_int)]


class BOARD_CONFIGURATION(ct.Structure):
    _fields_ = [
        ('serialNumber', ct.c_long),
        ('BOARD_TYPES', ct.c_ushort),
        ('revision', ct.c_ushort),
        ('numberTransmitters', ct.c_ushort),
        ('numberSensors', ct.c_ushort),
        ('firmwareNumber', ct.c_ushort),
        ('firmwareRevision', ct.c_ushort),
        ('modelString', ct.c_char * 10)]


class SYSTEM_CONFIGURATION(ct.Structure):
    _fields_ = [
        ('measurementRate', ct.c_double),
        ('powerLineFrequency', ct.c_double),
        ('maximumRange', ct.c_double),
        ('agcMode', enum_type),
        ('numberBoards', ct.c_int),
        ('numberSensors', ct.c_int),
        ('numberTransmitters', ct.c_int),
        ('transmitterIDRunning', ct.c_int),
        ('metric', ct.c_int),
        ('reportRate', ct.c_ushort)]


class ADAPTIVE_PARAMETERS(ct.Structure):
    _fields_ = [
        ('alphaMin', ct.c_ushort * 7),
        ('alphaMax', ct.c_ushort * 7),
        ('vm', ct.c_ushort * 7),
        ('alphaOn', ct.c_int)]


class QUALITY_PARAMETERS(ct.Structure):
    _fields_ = [
        ('error_slope', ct.c_short),
        ('error_offset', ct.c_short),
        ('error_sensitivity', ct.c_ushort),
        ('filter_alpha', ct.c_ushort)]


class POST_ERROR_PARAMETER(ct.Structure):
    _fields_ = [
        ('error', ct.c_ushort),
        ('channel', ct.c_char),
        ('fatal', ct.c_char),
        ('moreErrors', ct.c_char)]


class BOARD_REVISIONS(ct.Structure):
    _fields_ = [
        ('boot_loader_sw_number', ct.c_ushort),
        ('boot_loader_sw_revision', ct.c_ushort),
        ('mdsp_sw_number', ct.c_ushort),
        ('mdsp_sw_revision', ct.c_ushort),
        ('nondipole_sw_number', ct.c_ushort),
        ('nondipole_sw_revision', ct.c_ushort),
        ('fivedof_sw_number', ct.c_ushort),
        ('fivedof_sw_revision', ct.c_ushort),
        ('sixdof_sw_number', ct.c_ushort),
        ('sixdof_sw_revision', ct.c_ushort),
        ('dipole_sw_number', ct.c_ushort),
        ('dipole_sw_revision', ct.c_ushort)]


#
# Data formatting structures
#

class SHORT_POSITION(ct.Structure):
    _fields_ = list(zip("xyz", [ct.c_short] * 3))


class SHORT_ANGLES(ct.Structure):
    _fields_ = list(zip("aer", [ct.c_short] * 3))


class SHORT_MATRIX(ct.Structure):
    _fields_ = [("s", (ct.c_short * 3) * 3)]  # TODO check


class SHORT_QUATERNIONS(ct.Structure):
    _fields_ = [("q", ct.c_short * 4)]  # check


class SHORT_POSITION_ANGLES(ct.Structure):
    _fields_ = SHORT_POSITION._fields_ + \
               SHORT_ANGLES._fields_


class SHORT_MATRIX(ct.Structure):
    _fields_ = SHORT_POSITION._fields_ + \
               SHORT_MATRIX._fields_


class SHORT_POSITION_QUATERNION(ct.Structure):
    _fields_ = SHORT_POSITION._fields_ + \
               SHORT_QUATERNIONS._fields_


class DOUBLE_POSITION(ct.Structure):
    _fields_ = list(zip("xyz", [ct.c_double] * 3))


class DOUBLE_ANGLES(ct.Structure):
    _fields_ = list(zip("aer", [ct.c_double] * 3))


class DOUBLE_MATRIX(ct.Structure):
    _fields_ = [("s", (ct.c_double * 3) * 3)]  # TODO check


class DOUBLE_QUATERNIONS(ct.Structure):
    _fields_ = [("q", ct.c_double * 4)]  # check


class DOUBLE_POSITION_ANGLES(ct.Structure):
    _fields_ = DOUBLE_POSITION._fields_ + \
               DOUBLE_ANGLES._fields_


class DOUBLE_POSITION_MATRIX(ct.Structure):
    _fields_ = DOUBLE_POSITION._fields_ + \
               DOUBLE_MATRIX._fields_


class DOUBLE_POSITION_QUATERNION(ct.Structure):
    _fields_ = DOUBLE_POSITION._fields_ + \
               DOUBLE_QUATERNIONS._fields_


class DOUBLE_POSITION_TIME_STAMP(ct.Structure):
    _fields_ = DOUBLE_POSITION._fields_ + \
               [('time', ct.c_double)]


class DOUBLE_ANGLES_TIME_STAMP(ct.Structure):
    _fields_ = DOUBLE_ANGLES._fields_ + \
               [('time', ct.c_double)]


class DOUBLE_MATRIX_TIME_STAMP(ct.Structure):
    _fields_ = DOUBLE_MATRIX._fields_ + \
               [('time', ct.c_double)]


class DOUBLE_QUATERNIONS_TIME_STAMP(ct.Structure):
    _fields_ = DOUBLE_QUATERNIONS._fields_ + \
               [('time', ct.c_double)]


class DOUBLE_POSITION_ANGLES_TIME_STAMP(ct.Structure):
    _fields_ = DOUBLE_POSITION_ANGLES._fields_ + \
               [('time', ct.c_double)]


class DOUBLE_POSITION_MATRIX(ct.Structure):
    _fields_ = DOUBLE_POSITION_MATRIX._fields_ + \
               [('time', ct.c_double)]


class DOUBLE_POSITION_QUATERNION_STAMP_RECORD(ct.Structure):
    _fields_ = DOUBLE_POSITION_QUATERNION._fields_ + \
               [('time', ct.c_double)]


class DOUBLE_POSITION_TIME_Q(ct.Structure):
    _fields_ = DOUBLE_POSITION._fields_ + \
               [('time', ct.c_double), ('quality', ct.c_ushort)]


class DOUBLE_ANGLES_TIME_Q(ct.Structure):
    _fields_ = DOUBLE_ANGLES._fields_ + \
               [('time', ct.c_double), ('quality', ct.c_ushort)]


class DOUBLE_MATRIX_TIME_Q(ct.Structure):
    _fields_ = DOUBLE_MATRIX._fields_ + \
               [('time', ct.c_double), ('quality', ct.c_ushort)]


class DOUBLE_QUATERNIONS_TIME_Q(ct.Structure):
    _fields_ = DOUBLE_QUATERNIONS._fields_ + \
               [('time', ct.c_double), ('quality', ct.c_ushort)]


class DOUBLE_POSITION_ANGLES_TIME_Q(ct.Structure):
    _fields_ = DOUBLE_POSITION_ANGLES._fields_ + \
               [('time', ct.c_double), ('quality', ct.c_ushort)]


##*******************************************************************
## We added the following stucture "DOUBLE_POSITION_ANGLES_TIME_Q_RECORD_AllSensors"
## because MATLAB does not support Arrays of a structure embedded within a structure

class DOUBLE_POSITION_ANGLES_TIME_Q_RECORD_AllSensors_Four(ct.Structure):
    _fields_ = [
        ('x0', ct.c_double),
        ('y0', ct.c_double),
        ('z0', ct.c_double),
        ('a0', ct.c_double),
        ('e0', ct.c_double),
        ('r0', ct.c_double),
        ('time0', ct.c_double),
        ('quality0', ct.c_int),
        ('x1', ct.c_double),
        ('y1', ct.c_double),
        ('z1', ct.c_double),
        ('a1', ct.c_double),
        ('e1', ct.c_double),
        ('r1', ct.c_double),
        ('time1', ct.c_double),
        ('quality1', ct.c_int),
        ('x2', ct.c_double),
        ('y2', ct.c_double),
        ('z2', ct.c_double),
        ('a2', ct.c_double),
        ('e2', ct.c_double),
        ('r2', ct.c_double),
        ('time2', ct.c_double),
        ('quality2', ct.c_int),
        ('x3', ct.c_double),
        ('y3', ct.c_double),
        ('z3', ct.c_double),
        ('a3', ct.c_double),
        ('e3', ct.c_double),
        ('r3', ct.c_double),
        ('time3', ct.c_double),
        ('quality3', ct.c_int),
    ]


# omitted button structures

class SHORT_ALL_RECORD(ct.Structure):
    _fields_ = SHORT_POSITION_ANGLES._fields_ + \
               SHORT_MATRIX._fields_ + \
               SHORT_QUATERNIONS._fields_


class DOUBLE_ALL_RECORD(ct.Structure):
    _fields_ = DOUBLE_POSITION_ANGLES._fields_ + \
               DOUBLE_MATRIX._fields_ + \
               DOUBLE_QUATERNIONS._fields_


class DOUBLE_ALL_TIME_STAMP_RECORD(ct.Structure):
    _fields_ = DOUBLE_POSITION_ANGLES._fields_ + \
               DOUBLE_MATRIX._fields_ + \
               DOUBLE_QUATERNIONS._fields_ + \
               [('time', ct.c_double)]


class DOUBLE_ALL_TIME_STAMP_Q_RECORD(ct.Structure):
    _fields_ = DOUBLE_POSITION_ANGLES._fields_ + \
               DOUBLE_MATRIX._fields_ + \
               DOUBLE_QUATERNIONS._fields_ + \
               [('time', ct.c_double), ('quality', ct.c_ushort)]


class DOUBLE_ALL_TIME_STAMP_Q_RAW_RECORD(ct.Structure):
    _fields_ = DOUBLE_POSITION_ANGLES._fields_ + \
               DOUBLE_MATRIX._fields_ + \
               DOUBLE_QUATERNIONS._fields_ + \
               [('time', ct.c_double), ('quality', ct.c_ushort), \
                ('raw', (ct.c_double * 3) * 3)]
