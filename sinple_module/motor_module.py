# 步进电机库
import sys
import clr
import time
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

def move(motor_id,approach_speed,approach_step,approach_acceleration,delaytime,mode):
# 使用步进电机移动
# 设置参数：每次移动完成后电机状态（开为1，闭为0）
    DeviceManagerCLI.BuildDeviceList()
    motor = TCubeInertialMotor.CreateTCubeInertialMotor(motor_id) # 设备连接
    motor.Connect(motor_id) # 设备连接
    motor.StartPolling(250)
    motor.EnableDevice()
    time.sleep(3) # 这里的延时必须加上
    InertialMotorConfiguration = motor.GetInertialMotorConfiguration(motor_id) # 初始化设备参数
    currentDeviceSettings = ThorlabsInertialMotorSettings.GetSettings(InertialMotorConfiguration) # 初始化设备参数
    currentDeviceSettings.Drive.Channel(InertialMotorStatus.MotorChannels.Channel1).StepRate = approach_speed # 设置步速
    currentDeviceSettings.Drive.Channel(InertialMotorStatus.MotorChannels.Channel1).StepAcceleration = approach_acceleration # 设置加速时间
    currentDeviceSettings.Jog.Channel(InertialMotorStatus.MotorChannels.Channel1).JogStep = approach_step # 设置行走距离
    motor.SetSettings(currentDeviceSettings, True, True)
    if mode == 1:
        mode_jog = InertialMotorJogDirection.Increase
    else:
        mode_jog = InertialMotorJogDirection.Decrease
    while 1:
        # 步进前进
        motor.Jog(InertialMotorStatus.MotorChannels.Channel1,mode_jog,60000)
        time.sleep(delaytime)
        print(motor.GetPosition(InertialMotorStatus.MotorChannels.Channel1))

# 设备序号，步进电机速度，步进电机步长，步进电机加速度，停留时间，模式（前进/后退）
move("65864068",5,10,1,0.1,1)