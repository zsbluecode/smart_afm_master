from PyQt5 import uic
from PyQt5.QtCore import Qt
import sys
from PyQt5.QtWidgets import QApplication
from module import deviceconnection,parasetting,sweep,pidsetting,approach,scan,class_afm
import ctypes
import zhinst
import clr
# 创建QApplication对象
app = QApplication(sys.argv)
afm = class_afm.afm()

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


# 加载UI文件
ui = uic.loadUi("ui.ui")

# 连接仪器
# Labone
server_host: str = "localhost"
server_port: int = None
hf2 = False
apilevel_example = 1 if hf2 else 6
if not server_port:
    server_port = 8005 if hf2 else 8004
try:
    (daq, labone, props) = zhinst.utils.create_api_session(ui.lineEdit_labone_no.text(), apilevel_example, server_host=server_host, server_port=server_port)
    zhinst.utils.api_server_version_check(daq)
    ui.label_labone_state.setText("已连接")
    # 设定Labone初始值
    exp_setting = [
    ["/%s/oscs/%d/freq" % (labone, 0), 32536.47],
    ["/%s/demods/%d/enable" % (labone, 0), 1],
    ["/%s/sigouts/%d/autorange"%(labone,0), 1],
    ["/%s/demods/%d/rate" % (labone, 0), 100000],
    ["/%s/demods/%d/adcselect" % (labone, 0), 1],
    ["/%s/demods/%d/bindwidth" % (labone, 0), 100],
    ["/%s/demods/%d/oscselect" % (labone, 0), 0],
    ["/%s/sigouts/%d/on" % (labone, 0), 1],
    ["/%s/sigouts/%d/enables/%d" % (labone, 0, 0), 1],
    ["/%s/sigouts/%d/enables/%d" % (labone, 0, 1), 0],
    ["/%s/sigouts/%d/range" % (labone, 0), 1],
    ["/%s/sigouts/%d/amplitudes/%d" % (labone, 0, 0),0.01,],
    ["/%s/sigins/%d/scaling"%(labone,0),1,]
    ]
    daq.set(exp_setting)
    daq.sync()
except:
    ui.label_labone_state.setText("未连接")
# Motor
DeviceManagerCLI.BuildDeviceList()
motor_id = ui.lineEdit_motor_no.text()
motor = TCubeInertialMotor.CreateTCubeInertialMotor(motor_id) # 设备连接
try:
    if not motor.IsConnected:
        motor.Connect(motor_id) # 设备连接
        ui.label_motor_state.setText("已连接")
    if(motor.IsSettingsInitialized()): 
        motor.StartPolling(250)
        motor.EnableDevice()
except:
    ui.label_motor_state.setText("未连接")
# MCL
dll = ctypes.windll.LoadLibrary("module/Madlib.dll")
handle = dll.MCL_InitHandle()
if (handle==1):
    ui.label_mcl_state.setText("已连接")
    dll.MCL_SingleReadN.restype = ctypes.c_double
    dll.MCL_SingleReadZ.restype = ctypes.c_double
else:
    ui.label_mcl_state.setText("未连接")

# 连接函数 1
# 参数：三种仪器的名称
# 页面显示：三种仪器连接情况
ui.pushButton_connection.clicked.connect(lambda: deviceconnection.connect(motor,motor_id,dll,handle,ui.label_labone_state,ui.label_motor_state,ui.label_mcl_state,ui.lineEdit_labone_no.text()
            ,ui.lineEdit_motor_no.text(),ui.lineEdit_mcl_no.text()))

# 参数设置函数 2
# 参数：信号通道、激励电压、共振峰频率、带宽
# 页面显示：锁相放大器连接情况
ui.pushButton_labone_para_setting.clicked.connect(lambda: parasetting.parasetting(ui.lineEdit_labone_no.text(),ui.label_labone_state,ui.comboBox_labone_channel.currentText(),
                                                float(ui.lineEdit_labone_voltage.text()),float(ui.lineEdit_labone_frequency.text()),
                                                int(ui.lineEdit_labone_bindwidth.text())))
# 扫频函数 3
# 参数：开始、结束扫频频率、扫频样本点数、扫频次数、扫频模式、扫频带宽
# 页面显示：扫频图像（这里暂时不使用try方式）
ui.pushButton_sweep.clicked.connect(lambda: sweep.sweep(ui.lineEdit_labone_no.text(),ui.progressBar_sweep,ui.lineEdit_h_frequency,ui.lineEdit_Q_value,ui.lineEdit_h_amplitude,
                                    ui.label_sweep_picture,int(ui.lineEdit_start_sweep.text()),
                                    int(ui.lineEdit_stop_sweep.text()),int(ui.lineEdit_sample_sweep.text()),
                                    int(ui.lineEdit_count_sweep.text()),ui.comboBox_mode_sweep.currentText(),
                                    int(ui.lineEdit_bindwidth_sweep.text())))
ui.pushButton_sweep_stop.clicked.connect(lambda: sweep.sweep_stop())
ui.pushButton_sweep_save.clicked.connect(lambda: sweep.sweep_save(ui.label_pid_picture_1))

# pid/pll控制函数 4
# 首先需要根据当前的Q值、共振峰频率、最大共振峰导入相对应的值
ui.pushButton_load_labone_setting_1.clicked.connect(lambda: pidsetting.load_para_1(ui))
# 输入：device_id、PID的通道、PID的输入mode、通道、PID的输出mode、通道、PID的模型mode、PID的setpoint、重建phaseunwrap
# 计算PID的gain、Q、h_frequency、h_amplitude、center、lower、upper、target_bw
# 输出：Kp、Ki、Kd，setpoint实际值
ui.pushButton_calculate_pid_1.clicked.connect(lambda: pidsetting.pid_calculate_1(ui.lineEdit_labone_no.text(),
    ui.comboBox_pid_mode_channel_1.currentText(),ui.comboBox_pid_inputchannel_channel_1.currentText(),
    ui.comboBox_pid_inputchannel_number_channel_1.currentText(),ui.comboBox_pid_outputchannel_channel_1.currentText(),
    ui.comboBox_pid_outputchannel_number_channel_1.currentText(),ui.comboBox_pid_module_channel_1.currentText(),
    float(ui.lineEdit_setpoint_channel_1.text()),ui.comboBox_pid_phaseunwrap_1.currentText(),
    float(ui.lineEdit_gain_channel_1.text()),float(ui.lineEdit_Q_value.text()),float(ui.lineEdit_h_frequency.text()),
    float(ui.lineEdit_h_amplitude.text()),float(ui.lineEdit_center_channel_1.text()),float(ui.lineEdit_lower_channel_1.text()),
    float(ui.lineEdit_upper_channel_1.text()),float(ui.lineEdit_targetbw_channel_1.text()),
    ui.lineEdit_kp_channel_1,ui.lineEdit_ki_channel_1,ui.lineEdit_kd_channel_1,ui.lineEdit_setpoint_data_channel_1,
    ui.label_pid_picture_1,ui.comboBox_pid_inputchannel_channel_1,ui.comboBox_pid_outputchannel_channel_1,ui.comboBox_pid_aux_PLL_1.currentText(),
    float(ui.lineEdit_pid_scale_vol_1.text()),float(ui.lineEdit_aux_offset_1.text()),float(ui.lineEdit_aux_offset_max_1.text()),
    float(ui.lineEdit_aux_offset_min_1.text())
))
ui.pushButton_open_pid_1.clicked.connect(lambda: pidsetting.pid_open_1(ui.lineEdit_kp_channel_1,ui.lineEdit_ki_channel_1,ui.lineEdit_kd_channel_1,ui.lineEdit_labone_no.text(),ui.label_pid_state_state_1,float(ui.lineEdit_setpoint_data_channel_1.text())))
ui.pushButton_close_pid_1.clicked.connect(lambda: pidsetting.pid_close_1(ui.lineEdit_labone_no.text(),ui.label_pid_state_state_1))

ui.pushButton_load_labone_setting_2.clicked.connect(lambda: pidsetting.load_para_2())
ui.pushButton_calculate_pid_2.clicked.connect(lambda: pidsetting.pid_calculate_2(ui.lineEdit_labone_no.text(),
    ui.comboBox_pid_mode_channel_2.currentText(),ui.comboBox_pid_inputchannel_channel_2.currentText(),
    ui.comboBox_pid_inputchannel_number_channel_2.currentText(),ui.comboBox_pid_outputchannel_channel_2.currentText(),
    ui.comboBox_pid_outputchannel_number_channel_2.currentText(),ui.comboBox_pid_module_channel_2.currentText(),
    float(ui.lineEdit_setpoint_channel_2.text()),ui.comboBox_pid_phaseunwrap_2.currentText(),
    float(ui.lineEdit_gain_channel_2.text()),float(ui.lineEdit_Q_value.text()),float(ui.lineEdit_h_frequency.text()),
    float(ui.lineEdit_h_amplitude.text()),float(ui.lineEdit_center_channel_2.text()),float(ui.lineEdit_lower_channel_2.text()),
    float(ui.lineEdit_upper_channel_2.text()),float(ui.lineEdit_targetbw_channel_2.text()),
    ui.lineEdit_kp_channel_2,ui.lineEdit_ki_channel_2,ui.lineEdit_kd_channel_2,ui.lineEdit_setpoint_data_channel_2,
    ui.label_pid_picture_2,ui.comboBox_pid_inputchannel_channel_2,ui.comboBox_pid_outputchannel_channel_2,ui.comboBox_pid_aux_PLL_2.currentText(),
    float(ui.lineEdit_pid_scale_vol_2.text()),float(ui.lineEdit_aux_offset_2.text()),float(ui.lineEdit_aux_offset_max_2.text()),
    float(ui.lineEdit_aux_offset_min_2.text()
)))
ui.pushButton_open_pid_2.clicked.connect(lambda: pidsetting.pid_open_2(ui.lineEdit_kp_channel_2,ui.lineEdit_ki_channel_2,ui.lineEdit_kd_channel_2,ui.lineEdit_labone_no.text(),ui.label_pid_state_state_2,float(ui.lineEdit_setpoint_data_channel_2.text())))
ui.pushButton_close_pid_2.clicked.connect(lambda: pidsetting.pid_close_2(ui.lineEdit_labone_no.text(),ui.label_pid_state_state_2))

ui.pushButton_load_labone_setting_3.clicked.connect(lambda: pidsetting.load_para_3())
ui.pushButton_calculate_pid_3.clicked.connect(lambda: pidsetting.pid_calculate_3(ui.lineEdit_labone_no.text(),
    ui.comboBox_pid_mode_channel_3.currentText(),ui.comboBox_pid_inputchannel_channel_3.currentText(),
    ui.comboBox_pid_inputchannel_number_channel_3.currentText(),ui.comboBox_pid_outputchannel_channel_3.currentText(),
    ui.comboBox_pid_outputchannel_number_channel_3.currentText(),ui.comboBox_pid_module_channel_3.currentText(),
    float(ui.lineEdit_setpoint_channel_3.text()),ui.comboBox_pid_phaseunwrap_3.currentText(),
    float(ui.lineEdit_gain_channel_3.text()),float(ui.lineEdit_Q_value.text()),float(ui.lineEdit_h_frequency.text()),
    float(ui.lineEdit_h_amplitude.text()),float(ui.lineEdit_center_channel_3.text()),float(ui.lineEdit_lower_channel_3.text()),
    float(ui.lineEdit_upper_channel_3.text()),float(ui.lineEdit_targetbw_channel_3.text()),
    ui.lineEdit_kp_channel_3,ui.lineEdit_ki_channel_3,ui.lineEdit_kd_channel_3,ui.lineEdit_setpoint_data_channel_3,
    ui.label_pid_picture_3,ui.comboBox_pid_inputchannel_channel_3,ui.comboBox_pid_outputchannel_channel_3,ui.comboBox_pid_aux_PLL_3.currentText(),
    float(ui.lineEdit_pid_scale_vol_3.text()),float(ui.lineEdit_aux_offset_3.text()),float(ui.lineEdit_aux_offset_max_3.text()),
    float(ui.lineEdit_aux_offset_min_3.text())))
ui.pushButton_open_pid_3.clicked.connect(lambda: pidsetting.pid_open_3(ui.lineEdit_kp_channel_3,ui.lineEdit_ki_channel_3,ui.lineEdit_kd_channel_3,ui.lineEdit_labone_no.text(),ui.label_pid_state_state_3,float(ui.lineEdit_setpoint_data_channel_3.text())))
ui.pushButton_close_pid_3.clicked.connect(lambda: pidsetting.pid_close_3(ui.lineEdit_labone_no.text(),ui.label_pid_state_state_3))

ui.pushButton_load_labone_setting_4.clicked.connect(lambda: pidsetting.load_para_4())
ui.pushButton_calculate_pid_4.clicked.connect(lambda: pidsetting.pid_calculate_4(ui.lineEdit_labone_no.text(),
    ui.comboBox_pid_mode_channel_4.currentText(),ui.comboBox_pid_inputchannel_channel_4.currentText(),
    ui.comboBox_pid_inputchannel_number_channel_4.currentText(),ui.comboBox_pid_outputchannel_channel_4.currentText(),
    ui.comboBox_pid_outputchannel_number_channel_4.currentText(),ui.comboBox_pid_module_channel_4.currentText(),
    float(ui.lineEdit_setpoint_channel_4.text()),ui.comboBox_pid_phaseunwrap_4.currentText(),
    float(ui.lineEdit_gain_channel_4.text()),float(ui.lineEdit_Q_value.text()),float(ui.lineEdit_h_frequency.text()),
    float(ui.lineEdit_h_amplitude.text()),float(ui.lineEdit_center_channel_4.text()),float(ui.lineEdit_lower_channel_4.text()),
    float(ui.lineEdit_upper_channel_4.text()),float(ui.lineEdit_targetbw_channel_4.text()),
    ui.lineEdit_kp_channel_4,ui.lineEdit_ki_channel_4,ui.lineEdit_kd_channel_4,ui.lineEdit_setpoint_data_channel_4,
    ui.label_pid_picture_4,ui.comboBox_pid_inputchannel_channel_4,ui.comboBox_pid_outputchannel_channel_4,ui.comboBox_pid_aux_PLL_1.currentText(),
    float(ui.lineEdit_pid_scale_vol_1.text()),float(ui.lineEdit_aux_offset_1.text()),float(ui.lineEdit_aux_offset_max_1.text()),
    float(ui.lineEdit_aux_offset_min_1.text())
))
ui.pushButton_open_pid_4.clicked.connect(lambda: pidsetting.pid_open_4(ui.lineEdit_kp_channel_4,ui.lineEdit_ki_channel_4,ui.lineEdit_kd_channel_4,ui.lineEdit_labone_no.text(),ui.label_pid_state_state_4,float(ui.lineEdit_setpoint_data_channel_4.text())))
ui.pushButton_close_pid_4.clicked.connect(lambda: pidsetting.pid_close_4(ui.lineEdit_labone_no.text(),ui.label_pid_state_state_4))

# 进针函数 5

ui.pushButton_usb_camera_open.clicked.connect(lambda: approach.camera_open(ui.label_use_camera))
ui.pushButton_usb_camera_take.clicked.connect(lambda: approach.camera_take(ui.label_use_camera))
ui.pushButton_usb_camera_close.clicked.connect(lambda: approach.camera_close(ui.label_use_camera))


ui.pushButton_approach.clicked.connect(lambda: approach.pid_approach(ui.lineEdit_labone_no.text(),motor,motor_id,
                                        ui.progressBar_approach,ui.label_approach_picture,ui.label_approach_pid_picture,
                int(ui.lineEdit_approach_speed.text()),int(ui.lineEdit_approach_acceleration.text()),
                int(ui.lineEdit_approach_step.text()),int(ui.lineEdit_second_approach_step.text()),
                float(ui.lineEdit_approach_delaytime.text()),ui.comboBox_approach_mode.currentText(),
                float(ui.lineEdit_setpoint_data_channel_1.text()),float(ui.lineEdit_setpoint_data_channel_2.text()),
                float(ui.lineEdit_setpoint_data_channel_3.text()),float(ui.lineEdit_setpoint_data_channel_4.text()),
                float(ui.lineEdit_approach_aux_point.text())
                ))

ui.pushButton_approach_2.clicked.connect(lambda: approach.no_pid_approach(motor,motor_id,int(ui.lineEdit_approach_speed.text()),
                                int(ui.lineEdit_approach_acceleration.text()),int(ui.lineEdit_approach_step.text()),
                                float(ui.lineEdit_approach_delaytime.text())))
ui.pushButton_back.clicked.connect(lambda: approach.back(motor,motor_id,int(ui.lineEdit_back_speed.text()),
                                int(ui.lineEdit_approach_acceleration.text()),int(ui.lineEdit_back_step.text()),
                                float(ui.lineEdit_approach_delaytime.text())))
ui.pushButton_approach_stop.clicked.connect(lambda: approach.approach_stop())

# 扫描函数 6
ui.pushButton_scan.clicked.connect(lambda: scan.scan(dll,handle,ui.progressBar_scan_picture,ui.label_scan_picture,
                            int(ui.lineEdit_scan_width.text()),int(ui.lineEdit_scan_length.text()),
                            int(ui.lineEdit_scan_sample.text()),float(ui.lineEdit_scan_delaytime.text()),
                            ui.comboBox_scan_mode.currentText(),ui.label_mcl_state))
ui.pushButton_scan_stop.clicked.connect(lambda: scan.scan_stop())
ui.pushButton_scan_save.clicked.connect(lambda: scan.scan_save(ui.label_scan_picture))

# 运行程序
ui.show()

# 进入QApplication事件循环
sys.exit(app.exec_())
