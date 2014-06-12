""" Interface for ATC3DG.dll (.so)
Function prototypes for the BIRD system API 
adapted from ATC3DG.h

untested BETA version

Author: O. Lindemann
"""

import sys
import ctypes
from atc3dg_types import *

if sys.platform.startswith("linux"):
    # linux isn't tested
    print "Please ensure that ATCdaemon[32/64] is running"
    if ctypes.sizeof(ctypes.c_voidp)*8 == 64:
        dll_name = "/usr/lib64/ATC3DGlib64.so"
    else:
        dll_name = "/usr/lib/ATC3DGlib32.so"
else:
    if ctypes.sizeof(ctypes.c_voidp)*8 == 64:
        dll_name = "ATC3DG64.DLL"
    else:
        dll_name = "ATC3DG.DLL"

print "loading library {0}".format(dll_name)
_api = ctypes.CDLL(dll_name)


""" InitializeBIRDSystem    Starts and initializes driver, resets
                        hardware and interrogates hardware. Builds
                        local database of system resources.

    Parameters Passed:  none

    Return Value:       error status

    Remarks:            Can be used anytime a catastrophic failure
                        has occurred and the system needs to be
                        restarted.untab
"""
InitializeBIRDSystem = _api._InitializeBIRDSystem
InitializeBIRDSystem.restype = ctypes.c_int


""" GetBIRDSystemConfiguration

    Parameters Passed:  SYSTEM_CONFIGURATION* 

    Return Value:       error status

    Remarks:            Returns SYSTEM_CONFIGURATION structure
                        It contains values equal to the number of
                        transmitters, sensors and boards detected
                        in the system. (The board information is for 
                        test/diagnostic purposes, all commands
                        reference sensors and transmitters only) Once 
                        the number of devices is known, (e.g. n) the 
                        range of IDs for those devices becomes 0..(n-1)
"""
GetBIRDSystemConfiguration = _api._GetBIRDSystemConfiguration
GetBIRDSystemConfiguration.restype = ctypes.c_int
GetBIRDSystemConfiguration.argtypes = [ctypes.POINTER(SYSTEM_CONFIGURATION)]


""" GetTransmitterConfiguration

    Parameters Passed:  USHORT transmitterID
                        TRANSMITTER_CONFIGURATION *transmitterConfiguration

    Return Value:       error status

    Remarks:            After getting system config the user can then pass 
                        the index of a transmitter of interest to this function
                        which will then return the config for that transmitter.
                        Items of interest are the serial number and status.

"""
GetTransmitterConfiguration = _api._GetTransmitterConfiguration
GetTransmitterConfiguration.restype = ctypes.c_int
GetTransmitterConfiguration.argtypes = [ctypes.c_ushort, 
                                ctypes.POINTER(TRANSMITTER_CONFIGURATION)]

""" GetSensorConfiguration

    Parameters Passed:  USHORT sensorID,
                        SENSOR_CONFIGURATION* sensorConfiguration

    Return Value:       error status

    Remarks:            Similar to the transmitter function.            

"""
GetSensorConfiguration = _api._GetSensorConfiguration
GetSensorConfiguration.restype = ctypes.c_int
GetSensorConfiguration.argtypes = [ctypes.c_ushort, 
                                ctypes.POINTER(SENSOR_CONFIGURATION)]

""" GetBoardConfiguration

    Parameters Passed:  USHORT boardID,
                        BOARD_CONFIGURATION* boardConfiguration

    Return Value:       error status

    Remarks:            Similar to the Sensor and Transmitter
                        functions. Also returns information on
                        how many sensors and transmitters are
                        attached. NOTE: Board information is not
                        needed during normal operation this is
                        only provided for "accounting" purposes.

"""
GetBoardConfiguration = _api._GetBoardConfiguration
GetBoardConfiguration.restype = ctypes.c_int
GetBoardConfiguration.argtypes = [ctypes.c_ushort, 
                                ctypes.POINTER(BOARD_CONFIGURATION)]
""" GetAsynchronousRecord

    Parameters Passed:  USHORT sensorID,
                        void *pRecord,
                        int recordSize

    Return Value:       error status

    Remarks:            Returns data immediately in the currently 
                        selected format from the last measurement 
                        cycle. Requires user providing a buffer large 
                        enough for the result otherwise an error is 
                        generated and data lost.
                        (Old style BIRD POINT mode)            

"""
GetAsynchronousRecord = _api._GetAsynchronousRecord
GetAsynchronousRecord.restype = ctypes.c_int
GetAsynchronousRecord.argtypes = [ctypes.c_ushort, ctypes.c_void_p, ctypes.c_int]


""" GetSynchronousRecord

    Parameters Passed:  USHORT sensorID,
                        void *pRecord,
                        int recordSize

    Return Value:       error status

    Remarks:            Returns a record after next measurement cycle. Puts 
                        system into mode where records are generated 1/cycle.
                        Will return one and only one record per measurement
                        cycle. Will queue the records for each measurement
                        cycle if command not issued sufficiently often. If 
                        command issued too often will time-out with no data.
                        (old style BIRD STREAM mode)            

"""
GetSynchronousRecord = _api._GetSynchronousRecord
GetSynchronousRecord.restype = ctypes.c_ushort
GetSynchronousRecord.argtypes = [ctypes.c_ushort, ctypes.c_void_p, ctypes.c_int]


""" GetSystemParameter

    Parameters Passed:  PARAMETER_TYPE  parameterType,
                        void            *pBuffer,
                        int             bufferSize

    Return Value:       error status

    Remarks:            When a properly enumerated parameter type constant
                        is used, the command will return the parameter value
                        to the buffer provided by the user. An error is
                        generated if the buffer is incorrectly sized

"""
GetSystemParameter = _api._GetSystemParameter
GetSystemParameter.restype = ctypes.c_int
GetSystemParameter.argtypes = [enum_type, ctypes.c_void_p, ctypes.c_int]


""" SetSystemParameter

    Parameters Passed:  PARAMETER_TYPE  parameterType,
                        void            *pBuffer,
                        int             bufferSize

    Return Value:       error status

    Remarks:            Similar to GetSystemParameter but allows user
                        to set (write) the parameter.

"""
SetSystemParameter = _api._SetSystemParameter
SetSystemParameter.restype = ctypes.c_int
SetSystemParameter.argtypes = [enum_type, ctypes.c_void_p, ctypes.c_int]


""" GetSensorParameter

    Parameters Passed:  USHORT          sensorID,
                        PARAMETER_TYPE  parameterType,
                        void            *pBuffer,
                        int             bufferSize

    Return Value:       error status

    Remarks:            When a sensor is selected with a valid index (ID) 
                        and a properly enumerated parameter type constant
                        is used, the command will return the parameter value
                        to the buffer provided by the user. An error is
                        generated if the buffer is incorrectly sized

"""
GetSensorParameter = _api._GetSensorParameter
GetSensorParameter.restype = ctypes.c_int
GetSensorParameter.argtypes = [ctypes.c_ushort, enum_type, 
                               ctypes.c_void_p, ctypes.c_int]


""" SetSensorParameter

    Parameters Passed:  USHORT          sensorID,
                        PARAMETER_TYPE  parameterType,
                        void            *pBuffer,
                        int             bufferSize

    Return Value:       error status

    Remarks:            Similar to GetSensorParameter but allows user
                        to set (write) the parameter.

"""
SetSensorParameter = _api._SetSensorParameter
SetSensorParameter.restype = ctypes.c_int
SetSensorParameter.argtypes = [ctypes.c_ushort, enum_type, 
                               ctypes.c_void_p, ctypes.c_int]


""" GetTransmitterParameter

    Parameters Passed:  USHORT          transmitterID,
                        PARAMETER_TYPE  parameterType,
                        void            *pBuffer,
                        int             bufferSize

    Return Value:       error status

    Remarks:            Same as Sensor command            

"""
GetTransmitterParameter = _api._GetTransmitterParameter
GetTransmitterParameter.restype = ctypes.c_int
GetTransmitterParameter.argtypes = [ctypes.c_ushort, enum_type, 
                               ctypes.c_void_p, ctypes.c_int]

""" SetTransmitterParameter

    Parameters Passed:  USHORT          transmitterID,
                        PARAMETER_TYPE  parameterType,
                        void            *pBuffer,
                        int             bufferSize

    Return Value:       error status

    Remarks:            Same as sensor command            

"""
SetTransmitterParameter = _api._SetTransmitterParameter
SetTransmitterParameter.restype = ctypes.c_int
SetTransmitterParameter.argtypes = [ctypes.c_ushort, enum_type, 
                               ctypes.c_void_p, ctypes.c_int]

""" GetBIRDError

    Parameters Passed:  none

    Return Value:       error status

    Remarks:            Returns next error in queue 
                        if available

"""
GetBIRDError = _api._GetBIRDError
GetBIRDError.restype = ctypes.c_int

""" GetErrorText

    Parameters Passed:  int errorCode
                        char *pBuffer
                        int bufferSize
                        int type

    Return Value:       error status as a text string

    Remarks:            ErrorCode contains the error code returned from 
                        either a command or in response to GetBIRDError
                        and which is to be described by a text string.
                        Pass a pointer pBuffer to a buffer to contain
                        the result of the command. The size of the
                        buffer is contained in bufferSize. The type
                        parameter is an enumerated constant of
                        the type MESSAGE_TYPE.  
"""
GetErrorText = _api._GetErrorText
GetErrorText.restype = ctypes.c_int
GetErrorText.argtypes = [ctypes.c_int, ctypes.c_char_p, ## TODO: ctypes.POINTER(ctypes.c_char)?
                        ctypes.c_int, enum_type]

""" GetSensorStatus(USHORT sensorID)"""
GetSensorStatus = _api._GetSensorStatus
GetSensorStatus.restype = device_status
GetSensorStatus.argtypes = [ctypes.c_ushort]


""" GetTransmitterStatus( USHORT transmitterID)"""
GetTransmitterStatus = _api._GetTransmitterStatus
GetTransmitterStatus.restype = device_status
GetTransmitterStatus.argtypes = [ctypes.c_ushort]

""" GetBoardStatus( USHORT boardID) """
GetBoardStatus = _api._GetBoardStatus
GetBoardStatus.restype = device_status
GetBoardStatus.argtypes = [ctypes.c_ushort]

""" GetSystemStatus() """
GetSystemStatus = _api._GetSystemStatus
GetSystemStatus.restype = device_status
GetSystemStatus.argtypes = [ctypes.c_ushort]


""" SaveSystemConfiguration( LPCSTR  lpFileName); """
SaveSystemConfiguration = _api._SaveSystemConfiguration
SaveSystemConfiguration.restype = ctypes.c_int
SaveSystemConfiguration.argtypes = [ctypes.c_char_p]

""" RestoreSystemConfiguration( LPCSTR  lpFileName) """
RestoreSystemConfiguration = _api._RestoreSystemConfiguration
RestoreSystemConfiguration.restype = ctypes.c_int
RestoreSystemConfiguration.argtypes = [ctypes.c_char_p]


""" GetBoardParameter(
    USHORT                      boardID,
    enum BOARD_PARAMETER_TYPE   parameterType,
    void                        *pBuffer,
    int                         bufferSize);
"""
GetBoardParameter = _api._GetBoardParameter
GetBoardParameter.restype = ctypes.c_ushort
GetBoardParameter.argtypes = [ctypes.c_ushort, enum_type, 
                            ctypes.c_void_p, ctypes.c_int]

""" SetBoardParameter(
    USHORT                      boardID,
    enum BOARD_PARAMETER_TYPE   parameterType,
    void                        *pBuffer,
    int                         bufferSize)
"""
SetBoardParameter = _api._SetBoardParameter
SetBoardParameter.restype = ctypes.c_ushort
SetBoardParameter.argtypes = [ctypes.c_ushort, enum_type, 
                            ctypes.c_void_p, ctypes.c_int]

"""CloseBIRDSystem() """
CloseBIRDSystem = _api._CloseBIRDSystem
CloseBIRDSystem.restype = ctypes.c_ushort
