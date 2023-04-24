# Labone库
import zhinst.utils

# 步进电机库
import sys
import clr

sys.path.append(r"C:\Program Files\Thorlabs\Kinesis")
clr.AddReference("Thorlabs.MotionControl.DeviceManagerCLI")
clr.AddReference("Thorlabs.MotionControl.GenericMotorCLI")
clr.AddReference("Thorlabs.MotionControl.TCube.InertialMotorCLI")

from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.TCube.InertialMotorCLI import * 

from Thorlabs.MotionControl.GenericMotorCLI.ControlParameters import *
from Thorlabs.MotionControl.GenericMotorCLI.AdvancedMotor import *
from Thorlabs.MotionControl.GenericMotorCLI.KCubeMotor import *
from Thorlabs.MotionControl.GenericMotorCLI.Settings import *

# 压电位移台库
import ctypes

def connect(motor,motor_id,dll,handle,
            reveal_labone,reveal_motor,reveal_mcl,labone_name,motor_name,mcl_name):
# 连接Labone，使用全局变量daq、labone、props进行记录
    server_host: str = "localhost"
    server_port: int = None
    hf2 = False
    apilevel_example = 1 if hf2 else 6
    if not server_port:
        server_port = 8005 if hf2 else 8004
    try:
        (daq, labone, props) = zhinst.utils.create_api_session(labone_name, apilevel_example, server_host=server_host, server_port=server_port)
        zhinst.utils.api_server_version_check(daq)
        reveal_labone.setText("已连接")
        # 设定Labone初始值
        exp_setting = [
        ["/%s/oscs/%d/freq" % (labone, 0), 32768],
        ["/%s/demods/%d/enable" % (labone, 0), 1],
        ["/%s/sigouts/%d/autorange"%(labone,0), 1],
        ["/%s/demods/%d/rate" % (labone, 0), 1000],
        ["/%s/demods/%d/adcselect" % (labone, 0), 1],
        ["/%s/demods/%d/bindwidth" % (labone, 0), 100],
        ["/%s/demods/%d/oscselect" % (labone, 0), 0],
        ["/%s/sigouts/%d/on" % (labone, 0), 1],
        ["/%s/sigouts/%d/enables/%d" % (labone, 0, 0), 1],
        ["/%s/sigouts/%d/enables/%d" % (labone, 0, 1), 0],
        ["/%s/sigouts/%d/range" % (labone, 0), 1],
        ["/%s/sigouts/%d/amplitudes/%d" % (labone, 0, 0),0.005,],]
        daq.set(exp_setting)
        daq.sync()
    except:
        reveal_labone.setText("未连接")
    motor_id = motor_name
    DeviceManagerCLI.BuildDeviceList()
    motor = TCubeInertialMotor.CreateTCubeInertialMotor(motor_id) # 设备连接
    print(motor.IsConnected)
    try:
        if not motor.IsConnected:
            motor.Connect(motor_name) # 设备连接
            reveal_motor.setText("已连接")
        if(motor.IsSettingsInitialized()): 
            motor.StartPolling(250)
            motor.EnableDevice()
    except:
        reveal_motor.setText("未连接")
    dll = ctypes.windll.LoadLibrary(r"C:\Users\wzs\Desktop\newModelAfm\new_model\module\Madlib.dll")
    handle = dll.MCL_InitHandle()
    print(handle)
    if (handle==1):
        reveal_mcl.setText("已连接")
        dll.MCL_SingleReadN.restype = ctypes.c_double
        dll.MCL_SingleReadZ.restype = ctypes.c_double
    else:
        reveal_mcl.setText("未连接")