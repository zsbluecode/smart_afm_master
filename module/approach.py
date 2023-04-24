import cv2
from PyQt5.QtWidgets import QMessageBox,QFileDialog,QApplication
from PyQt5 import sip
from PyQt5 import QtGui,QtCore
from PyQt5.QtMultimedia import QCamera,QCameraImageCapture
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
import threading as th
import zhinst
import numpy as np
import time
import basic.plot
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

def camera_open(label):
    global camera
    camera = QCamera()
    view = QCameraViewfinder()
    camera.setCaptureMode(QCamera.CaptureStillImage)
    camera.setViewfinder(view)
    camera.start()
    image_capture = QCameraImageCapture(camera)
    image_capture.capture( '/tmp/camera_image.jpg' )
    image_saved_path = '/tmp/camera_image.jpg'
    pixmap = QtGui.QPixmap(image_saved_path)
    label.setPixmap(pixmap.scaled(label.size()))


def camera_take(label_camera):
    filename, _ = QFileDialog.getSaveFileName(label_camera, "Save Image", "", "PNG(*.png);;JPEG(*.jpg *.jpeg)")
    if filename:
        # 保存图像
        pixmap = label_camera.grab()
        size = label_camera.size()
        pixmap_scaled = pixmap.scaled(size)
        pixmap_scaled.save(filename)
        # 显示保存成功的消息框
        QMessageBox.information(label_camera, "Saved", "The image has been saved.", QMessageBox.Ok)

def camera_close(label):
    global camera
    camera.stop()
    camera.setViewfinder(None)



def pid_approach(device_id,motor,motor_id,prograss,widget_1,aux_widget,
                 approach_speed,approach_accelerate,approach_step,approach_second_step,delaytime,approach_mode,setpoint_value_1,
                 setpoint_value_2,setpoint_value_3,setpoint_value_4,approach_aux_point):
# 使用步进电机移动
# 设置参数：每次移动完成后电机状态（开为1，闭为0）
    setpoint_value = 0
    setpoint=setpoint_value_1
    if re.search("1",approach_mode):
        setpoint_value=1
        setpoint=setpoint_value_1
    elif re.search("2",approach_mode):
        setpoint_value=2
        setpoint=setpoint_value_2
    elif re.search("3",approach_mode):
        setpoint_value=3
        setpoint=setpoint_value_3
    elif re.search("4",approach_mode):
        setpoint_value=4
        setpoint=setpoint_value_4
    if(setpoint_value==0):
        pass
    else:
        hf2 = False
        apilevel_example = 1 if hf2 else 6
        (daq, labone, props) = zhinst.utils.create_api_session(device_id, apilevel_example, server_host="localhost", server_port=8004)
        zhinst.utils.api_server_version_check(daq)
        global approach_state
        approach_state = 1
        vol_data = daq.getSample("/%s/demods/%d/sample" % (labone, 0))
        vol = np.abs(vol_data['x'][0]+1j*vol_data['y'][0])
        aux = daq.get('/%s/pids/%d/value'%(labone,0))
        aux_out = aux['dev4346']['pids']['0']['value']['value'][0]  
        if (setpoint_value==1):
            vol_data = daq.getSample("/%s/demods/%d/sample" % (labone, 0))
            vol = np.abs(vol_data['x'][0]+1j*vol_data['y'][0])
            aux = daq.get('/%s/pids/%d/value'%(labone,0))
            aux_out = aux['dev4346']['pids']['0']['value']['value'][0]  
        elif(setpoint_value==2):
            vol_data = daq.get('/%s/auxouts/%d/value'%(labone,0)) # pid auouts
            vol = vol_data["dev4346"]["auxouts"]["0"]["value"]["value"][0]
            aux = daq.get('/%s/pids/%d/value'%(labone,1))
            aux_out = aux['dev4346']['pids']['1']['value']['value'][0]  
        else:
            vol_data = daq.getSample("/%s/demods/%d/sample" % (labone, 0))
            vol = np.abs(vol_data['x'][0]+1j*vol_data['y'][0])
            aux = daq.get('/%s/pids/%d/value'%(labone,0))
            aux_out = aux['dev4346']['pids']['0']['value']['value'][0]  
            # 等待拓展
        time_x = []
        step_x = []
        approach_1 = []
        approach_2 = []
        widget_1.show()
        aux_widget.show()
        ##设置步进电机
        if not motor.IsConnected:
            DeviceManagerCLI.BuildDeviceList()
            motor =  TCubeInertialMotor.CreateTCubeInertialMotor(motor_id) # 设备连接
            motor.Connect(motor_id)
            time.sleep(3)
        if(motor.IsSettingsInitialized()):
            motor.StartPolling(250)
            motor.EnableDevice()
            time.sleep(3)
        InertialMotorConfiguration = motor.GetInertialMotorConfiguration(motor_id) # 初始化设备参数
        currentDeviceSettings = ThorlabsInertialMotorSettings.GetSettings(InertialMotorConfiguration) # 初始化设备参数
        currentDeviceSettings.Drive.Channel(InertialMotorStatus.MotorChannels.Channel1).StepRate = approach_speed # 设置步速
        currentDeviceSettings.Drive.Channel(InertialMotorStatus.MotorChannels.Channel1).StepAcceleration = approach_accelerate # 设置加速时间
        currentDeviceSettings.Jog.Channel(InertialMotorStatus.MotorChannels.Channel1).JogStep = approach_step # 设置行走距离
        motor.SetSettings(currentDeviceSettings, True, True)
        time_start = time.time()
        step_start = motor.GetPosition(InertialMotorStatus.MotorChannels.Channel1)
        if(setpoint_value==1):
            while(vol >= setpoint and approach_state == 1):
                # 步进前进
                motor.Jog(InertialMotorStatus.MotorChannels.Channel1,InertialMotorJogDirection.Increase,60000)
                # 获取新的vol、aux数值
                vol_data = daq.getSample("/%s/demods/%d/sample" % (labone, 0))
                vol = np.abs(vol_data['x'][0]+1j*vol_data['y'][0])
                aux = daq.get('/%s/pids/%d/value'%(labone,0))
                aux_out=aux['dev4346']['pids']['0']['value']['value'][0]
                ax,canvas,fig = basic.plot.plot_2D(widget_1)
                ax_2,canvas_2,fig_2 = basic.plot.plot_2D(aux_widget)
                if(len(time_x)<=100):
                    time_x.append(time.time()-time_start)
                    step_x.append(motor.GetPosition(InertialMotorStatus.MotorChannels.Channel1))
                    approach_1.append(vol)
                    approach_2.append(aux_out)
                else:
                    time_x.pop(0)
                    time_x.append(time.time()-time_start)
                    step_x.pop(0)
                    step_x.append(motor.GetPosition(InertialMotorStatus.MotorChannels.Channel1))
                    approach_1.pop(0)
                    approach_1.append(vol)
                    approach_2.pop(0)
                    approach_2.append(aux_out)
                ax.plot(step_x,approach_1)
                ax_2.plot(time_x,approach_2)
                ax.set_title("进针图像",fontfamily='SimHei')
                ax_2.set_title("PID图像",fontfamily='SimHei')
                canvas.draw()
                canvas_2.draw()
                QApplication.processEvents()  # 强制刷新窗口
                # prograss.setValue(i/1000*100)
                time.sleep(delaytime)
            if(vol<setpoint):
                print("到达setpoint，突变")
            approach_aux_state = 1
            # 第二步进针，以1步速度到达aux_out为3.5点
            currentDeviceSettings.Jog.Channel(InertialMotorStatus.MotorChannels.Channel1).JogStep = approach_second_step # 设置行走距离
            motor.SetSettings(currentDeviceSettings, True, True)
            while(aux_out-approach_aux_point > 0.1 and approach_state == 1):
                # 步进前进
                motor.Jog(InertialMotorStatus.MotorChannels.Channel1,InertialMotorJogDirection.Increase,60000)
                # 获取新的vol、aux数值
                vol_data = daq.getSample("/%s/demods/%d/sample" % (labone, 0))
                vol = np.abs(vol_data['x'][0]+1j*vol_data['y'][0])
                aux = daq.get('/%s/pids/%d/value'%(labone,0))
                aux_out=aux['dev4346']['pids']['0']['value']['value'][0]
                time.sleep(delaytime)
                print(motor.GetPosition(InertialMotorStatus.MotorChannels.Channel1))
                # print(dll.MCL_SingleReadZ(self.mcl))
                ax,canvas,fig = basic.plot.plot_2D(widget_1)
                ax_2,canvas_2,fig_2 = basic.plot.plot_2D(aux_widget)
                if(len(time_x)<=100):
                    time_x.append(time.time()-time_start)
                    step_x.append(motor.GetPosition(InertialMotorStatus.MotorChannels.Channel1))
                    approach_1.append(vol)
                    approach_2.append(aux_out)
                else:
                    time_x.pop(0)
                    time_x.append(time.time()-time_start)
                    step_x.pop(0)
                    step_x.append(motor.GetPosition(InertialMotorStatus.MotorChannels.Channel1))
                    approach_1.pop(0)
                    approach_1.append(vol)
                    approach_2.pop(0)
                    approach_2.append(aux_out)
                ax.plot(step_x,approach_1)
                ax_2.plot(time_x,approach_2)
                ax.set_title("进针图像",fontfamily='SimHei')
                ax_2.set_title("PID图像",fontfamily='SimHei')
                canvas.draw()
                canvas_2.draw()
                QApplication.processEvents()  # 强制刷新窗口
                # prograss.setValue(i/1000*100)
            if(aux_out-approach_aux_point<=0.1):
                print("进针完成")
            prograss.setValue(100)
        elif(setpoint_value==2):
            while(vol <= setpoint and approach_state == 1):
                # 步进前进
                motor.Jog(InertialMotorStatus.MotorChannels.Channel1,InertialMotorJogDirection.Increase,60000)
                # 获取新的vol、aux数值
                vol_data = daq.get('/%s/auxouts/%d/value'%(labone,0)) # pid auouts
                vol = vol_data["dev4346"]["auxouts"]["0"]["value"]["value"][0]
                aux = daq.get('/%s/pids/%d/value'%(labone,1))
                aux_out = aux['dev4346']['pids']['1']['value']['value'][0] 
                ax,canvas,fig = basic.plot.plot_2D(widget_1)
                ax_2,canvas_2,fig_2 = basic.plot.plot_2D(aux_widget)
                if(len(time_x)<=100):
                    time_x.append(time.time()-time_start)
                    step_x.append(motor.GetPosition(InertialMotorStatus.MotorChannels.Channel1))
                    approach_1.append(vol)
                    approach_2.append(aux_out)
                else:
                    time_x.pop(0)
                    time_x.append(time.time()-time_start)
                    step_x.pop(0)
                    step_x.append(motor.GetPosition(InertialMotorStatus.MotorChannels.Channel1))
                    approach_1.pop(0)
                    approach_1.append(vol)
                    approach_2.pop(0)
                    approach_2.append(aux_out)
                ax.plot(step_x,approach_1)
                ax_2.plot(time_x,approach_2)
                ax.set_title("进针图像",fontfamily='SimHei')
                ax_2.set_title("PID图像",fontfamily='SimHei')
                canvas.draw()
                canvas_2.draw()
                QApplication.processEvents()  # 强制刷新窗口
                # prograss.setValue(i/1000*100)
                time.sleep(delaytime)
            if(vol<setpoint):
                print("到达setpoint，突变")
            approach_aux_state = 1
            # 第二步进针，以1步速度到达aux_out为3.5点
            currentDeviceSettings.Jog.Channel(InertialMotorStatus.MotorChannels.Channel1).JogStep = approach_second_step # 设置行走距离
            motor.SetSettings(currentDeviceSettings, True, True)
            while(aux_out-approach_aux_point > 0.1 and approach_state == 1):
                # 步进前进
                motor.Jog(InertialMotorStatus.MotorChannels.Channel1,InertialMotorJogDirection.Increase,60000)
                # 获取新的vol、aux数值
                vol_data = daq.get('/%s/auxouts/%d/value'%(labone,0)) # pid auouts
                vol = vol_data["dev4346"]["auxouts"]["0"]["value"]["value"][0]
                aux = daq.get('/%s/pids/%d/value'%(labone,1))
                aux_out = aux['dev4346']['pids']['1']['value']['value'][0] 
                time.sleep(delaytime)
                print(motor.GetPosition(InertialMotorStatus.MotorChannels.Channel1))
                # print(dll.MCL_SingleReadZ(self.mcl))
                ax,canvas,fig = basic.plot.plot_2D(widget_1)
                ax_2,canvas_2,fig_2 = basic.plot.plot_2D(aux_widget)
                if(len(time_x)<=100):
                    time_x.append(time.time()-time_start)
                    step_x.append(motor.GetPosition(InertialMotorStatus.MotorChannels.Channel1))
                    approach_1.append(vol)
                    approach_2.append(aux_out)
                else:
                    time_x.pop(0)
                    time_x.append(time.time()-time_start)
                    step_x.pop(0)
                    step_x.append(motor.GetPosition(InertialMotorStatus.MotorChannels.Channel1))
                    approach_1.pop(0)
                    approach_1.append(vol)
                    approach_2.pop(0)
                    approach_2.append(aux_out)
                ax.plot(step_x,approach_1)
                ax_2.plot(time_x,approach_2)
                ax.set_title("进针图像",fontfamily='SimHei')
                ax_2.set_title("PID图像",fontfamily='SimHei')
                canvas.draw()
                canvas_2.draw()
                QApplication.processEvents()  # 强制刷新窗口
                # prograss.setValue(i/1000*100)
            if(aux_out-approach_aux_point<=0.1):
                print("进针完成")
            prograss.setValue(100)

def no_pid_approach(motor,motor_id,approach_speed,approach_acceleration,approach_step,delaytime,mode=1):
    global approach_state
    approach_state = 1
    ##设置步进电机
    if not motor.IsConnected:
        DeviceManagerCLI.BuildDeviceList()
        motor =  TCubeInertialMotor.CreateTCubeInertialMotor(motor_id) # 设备连接
        motor.Connect(motor_id)
        time.sleep(3)
    if(motor.IsSettingsInitialized()):
        motor.StartPolling(250)
        motor.EnableDevice()
        time.sleep(3)
    InertialMotorConfiguration = motor.GetInertialMotorConfiguration(motor_id) # 初始化设备参数
    currentDeviceSettings = ThorlabsInertialMotorSettings.GetSettings(InertialMotorConfiguration) # 初始化设备参数
    currentDeviceSettings.Drive.Channel(InertialMotorStatus.MotorChannels.Channel1).StepRate = approach_speed # 设置步速
    currentDeviceSettings.Drive.Channel(InertialMotorStatus.MotorChannels.Channel1).StepAcceleration = approach_acceleration # 设置加速时间
    currentDeviceSettings.Jog.Channel(InertialMotorStatus.MotorChannels.Channel1).JogStep = approach_step # 设置行走距离
    motor.SetSettings(currentDeviceSettings, True, True)
    time.sleep(3)
    if mode == 1:
        mode_jog = InertialMotorJogDirection.Increase
    else:
        mode_jog = InertialMotorJogDirection.Decrease
    QApplication.processEvents()  # 强制刷新窗口
    # 步进前进
    motor.Jog(InertialMotorStatus.MotorChannels.Channel1,mode_jog,60000)
    time.sleep(delaytime)
    print(motor.GetPosition(InertialMotorStatus.MotorChannels.Channel1))
    motor.StopPolling()
    motor.ShutDown()
    

def back(motor,motor_id,back_speed,back_acceleration,back_step,delaytime):
    no_pid_approach(motor,motor_id,back_speed,back_acceleration,back_step,delaytime,mode=2)

def approach_stop():
    global approach_state
    approach_state = 0
    


