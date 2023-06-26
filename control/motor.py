import sys
import clr
import re
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


class Motor:
    def __init__(self):
        self.motor_id = "65864068"
        self.motor = None
        # 步进电机参数设置
        self.approach_speed = 1
        self.approach_accelerate = 1
        self.approach_step = 1

    def para_setting(self,**kwargs):
        InertialMotorConfiguration = self.motor.GetInertialMotorConfiguration(self.motor_id) # 初始化设备参数
        currentDeviceSettings = ThorlabsInertialMotorSettings.GetSettings(InertialMotorConfiguration) # 初始化设备参数
        for key,value in kwargs.items():
            if(key=="speed"):
                currentDeviceSettings.Drive.Channel(InertialMotorStatus.MotorChannels.Channel1).StepRate = value # 设置步速
            elif(key=="accelerate"):
                currentDeviceSettings.Drive.Channel(InertialMotorStatus.MotorChannels.Channel1).StepAcceleration = value # 设置加速时间
            elif(key=="step"):
                currentDeviceSettings.Jog.Channel(InertialMotorStatus.MotorChannels.Channel1).JogStep = value # 设置行走距离


    def jog(self):
        self.motor.Jog(InertialMotorStatus.MotorChannels.Channel1,InertialMotorJogDirection.Increase,60000)
    
    def jog_back(self):
        self.motor.Jog(InertialMotorStatus.MotorChannels.Channel1,InertialMotorJogDirection.Decrease,60000)
        