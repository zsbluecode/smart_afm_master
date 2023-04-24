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
# 其他库
import time
import numpy as np
import threading as th
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QVBoxLayout,QApplication,QMessageBox,QFileDialog
from PyQt5 import sip
import datetime

def plot_2D(widget):
    fig = Figure(figsize=(5,4),dpi=100)
    canvas = FigureCanvas(fig)
    print(widget.layout())
    if(widget.layout() is None):
    # 如果没有布局，创建一个新的水平布局并将其设置为QWidget的布局
        layout = QVBoxLayout(widget)
    else:
        layout = widget.layout()
    print(layout,layout.count())
    if (layout.count()):
        sip.delete(layout.takeAt(0).widget())
    layout.addWidget(canvas)
    print(layout.count())
    # 绘制图像
    ax = fig.add_subplot(111)
    return ax,canvas,fig
    

# Q值计算函数
def calculate_data(x,y):
    #减去y的背景值
    background=y[0]
    y[:]=[i-background for i in y]
    #找出中心频率以及最大的y
    center = x[y.index(max(y))]
    peak = max(y)
    half_peak_left=0
    half_peak_right=1
    #用每个点与半峰高的值的误差来找出最接近半峰高的点
    erro = [np.abs(i-peak/2) for i in y]
    half_peak_left = x[erro.index(min(erro[0:y.index(max(y))]))]
    half_peak_right = x[erro.index(min(erro[y.index(max(y)):]))]
    q=center/(half_peak_right-half_peak_left)
    return(q)    

def connect(reveal,labone_name,motor_name,mcl_name):
# 连接Labone，使用全局变量daq、labone、props进行记录
    server_host: str = "localhost"
    server_port: int = None
    hf2 = False
    apilevel_example = 1 if hf2 else 6
    if not server_port:
        server_port = 8005 if hf2 else 8004
    global daq,labone,props
    try:
        (daq, labone, props) = zhinst.utils.create_api_session(labone_name, apilevel_example, server_host=server_host, server_port=server_port)
        zhinst.utils.api_server_version_check(daq)
        print("锁相放大器连接成功")
        # 设定Labone初始值
        exp_setting = [
        ["/%s/oscs/%d/freq" % (labone, 0), 32768],
        ["/%s/demods/%d/enable" % (labone, 0), 1],
        ["/%s/sigouts/%d/autorange"%(labone,0), 1],
        # ["/%s/demods/%d/currins/0/scaling" % (labone,0),1],
        ["/%s/demods/%d/rate" % (labone, 0), 1000],
        ["/%s/demods/%d/adcselect" % (labone, 0), 1],
        ["/%s/demods/%d/timeconstant" % (labone, 0), 0.0008],
        ["/%s/demods/%d/oscselect" % (labone, 0), 0],
        ["/%s/sigouts/%d/on" % (labone, 0), 1],
        ["/%s/sigouts/%d/enables/%d" % (labone, 0, 0), 1],
         ["/%s/sigouts/%d/enables/%d" % (labone, 0, 1), 0],
        ["/%s/sigouts/%d/range" % (labone, 0), 1],
        ["/%s/sigouts/%d/amplitudes/%d" % (labone, 0, 0),0.005,],]
        daq.set(exp_setting)
        daq.sync()
    except:
        print("锁相放大器未连接成功")
    global motor,motor_id
    motor_id = motor_name
    DeviceManagerCLI.BuildDeviceList()
    motor = TCubeInertialMotor.CreateTCubeInertialMotor(motor_id) # 设备连接
    try:
        if not motor.IsConnected:
            motor.Connect(motor_name) # 设备连接
            print("步进电机连接成功")
        if(motor.IsSettingsInitialized()): 
            motor.StartPolling(250)
            motor.EnableDevice()
    except:
        print("步进电机连接失败")
    global dll,handle
    dll = ctypes.windll.LoadLibrary(r"C:\Users\wzs\Desktop\newModelAfm\new_model\module\Madlib.dll")
    handle = dll.MCL_InitHandle()
    print(handle)
    if (handle==1):
        print("压电位移台已经连接")
        dll.MCL_SingleReadN.restype = ctypes.c_double
        dll.MCL_SingleReadZ.restype = ctypes.c_double
    else:
        print("压电位移台未连接成功")



def data(widget,pushbutton):
    start_time = time.time()
    time_x = []
    data_y = []
    if(pushbutton.text()=="开启实时图像"):
        pushbutton.setText("关闭实时图像")
    else:
        pushbutton.setText("开启实时图像")
    while(pushbutton.text()=="关闭实时图像"):
        ax,canvas,fig = plot_2D(widget)
        vol_data = daq.getSample("/%s/demods/%d/sample" % (labone, 0))
        vol = np.abs(vol_data['x'][0]+1j*vol_data['y'][0])
        if(len(time_x)<=100):
            time_x.append(time.time()-start_time)
            data_y.append(vol)
        else:
            time_x.pop(0)
            time_x.append(time.time()-start_time)
            data_y.pop(0)
            data_y.append(vol)
        ax.plot(time_x,data_y)
        ax.set_title("实时图像",fontfamily='SimHei')
        canvas.draw()
        QApplication.processEvents()  # 强制刷新窗口
        time.sleep(0.005)  

def sweep(widget,max_frequency,q_value,amplitude,start_sweep,stop_sweep,sample_count,loop_count):
# 扫描函数
# 输入变量：开始扫描频率、结束扫描频率，扫描样本点，扫描次数
    global max_r,Q_value,h_frequency
    sweeper = daq.sweep()
    sweeper.set("device", labone)
    sweeper.set("gridnode", "oscs/%d/freq" % 0)
    sweeper.set("start", start_sweep)
    sweeper.set("stop", stop_sweep)
    sweeper.set("samplecount", sample_count)
    sweeper.set("xmapping", 1)
    sweeper.set("bandwidthcontrol", 2)
    sweeper.set("bandwidthoverlap", 0)
    sweeper.set("scan", 0)
    sweeper.set("loopcount", loop_count)
    sweeper.set("settling/time", 0)
    sweeper.set("settling/inaccuracy", 0.001)
    sweeper.set("averaging/tc", 10)
    sweeper.set("averaging/sample", 10)
    path = "/%s/demods/%d/sample" % (labone,0)
    sweeper.subscribe(path)
    sweeper.set("save/filename", "sweep_with_save")
    sweeper.set("save/fileformat", "hdf5")
    sweeper.execute()
    print("扫频参数设置完成")
    start = time.time()
    timeout = 20000  # [s]
    print("Will perform", loop_count, "sweeps...")
    while not sweeper.finished():  # Wait until the sweep is complete, with timeout.
        time.sleep(0.2)
        progress = sweeper.progress()
        print(f"Individual sweep progress: {progress[0]:.2%}.", end="\r")
        if (time.time() - start) > timeout:
            print("\nSweep still not finished, forcing finish...")
            sweeper.finish()
    print("")
    return_flat_dict = True
    data = sweeper.read(return_flat_dict)
    sweeper.unsubscribe(path)
    assert (data), "read() returned an empty data dictionary, did you subscribe to any paths?"
    assert path in data, "No sweep data in data dictionary: it has no key '%s'" % path
    samples = data[path]
    print("Returned sweeper data contains", len(samples), "sweeps.")
    assert (len(samples) == loop_count), "The sweeper returned an unexpected number of sweeps: `%d`. Expected: `%d`." % (len(samples),loop_count,)
    for sample in samples:
        frequency = sample[0]["frequency"]
        R = np.abs(sample[0]["x"] + 1j * sample[0]["y"])
        R=R.tolist()
        frequency=frequency.tolist()
        max_r = max(R)
        Q_value = calculate_data(frequency,R)
    sweep_x = frequency
    sweep_y = R
    h_frequency = frequency[R.index(max(R))]
    amplitude.setText(str(round(max_r,5)))
    q_value.setText(str(round(Q_value,5)))
    max_frequency.setText(str(round(h_frequency,5)))
    
    ax,canvas,fig = plot_2D(widget)
    ax.set_title("扫频图像",fontfamily='SimHei')
    ax.plot(sweep_x,sweep_y)
    canvas.draw()
    widget.show()
    exp_setting_2 = [
        ["/%s/oscs/%d/freq" % (labone, 0), h_frequency],]
    daq.set(exp_setting_2)

def pid_setting(line_kp,line_ki,line_kd,gain,target_bw,lower,upper,center):
# 参数：增益、目标带宽
# PID 设置：仅是计算并且设定好PID
    print(gain)        
    zhinst.utils.api_server_version_check(daq)
    daq.sync()
    daq.set([['/%s/pids/0/mode'%(labone), 0],
    ['/%s/pids/0/input'%(labone), 2],
    ['/%s/pids/0/inputchannel'%(labone), 0],
    ['/%s/pids/0/output'%(labone), 5],
    ['/%s/pids/0/outputchannel'%(labone), 2],
    ['/%s/pids/0/center'%(labone), center],
    ['/dev4346/pids/0/limitlower', lower],
    ['/dev4346/pids/0/limitupper', upper]])
    pid_index = 0  # PID index.
    pidAdvisor = daq.pidAdvisor()
    pidAdvisor.set("device", labone)
    pidAdvisor.set("auto", False)
    pidAdvisor.set("pid/targetbw", target_bw)
    #PI
    pidAdvisor.set("pid/mode", 3)
    # PID index to use (first PID of device: 0)
    pidAdvisor.set("index", pid_index)
    # source = 6: Resonator amplitude
    pidAdvisor.set("dut/source", 6)
    pidAdvisor.set('dut/fcenter',h_frequency)
    pidAdvisor.set('dut/gain', gain)
    pidAdvisor.set('dut/q',Q_value)
    print('q_value{}'.format(Q_value))
    print('gain{}'.format(gain))
    print('h_frequency{}'.format(h_frequency))
    pidAdvisor.set("pid/p", 0)
    pidAdvisor.set("pid/i", 0)
    pidAdvisor.set("pid/d", 0)
    # Start the module thread
    pidAdvisor.execute()
    pidAdvisor.set("calculate", 1)
    print("Starting advising. Optimization process may run up to a minute...")
    calculate = 1

    t_start = time.time()
    t_timeout = t_start + 90
    while calculate == 1:
        time.sleep(0.1)
        calculate = pidAdvisor.getInt("calculate")
        progress = pidAdvisor.progress()
        print(f"Advisor progress: {progress[0]:.2%}.", end="\r")
        if time.time() > t_timeout:
            pidAdvisor.finish()
            raise Exception("PID advising failed due to timeout.")
    print("")
    print(f"Advice took {time.time() - t_start:0.1f} s.")
    pidAdvisor.set( 'todevice',1)
    result = pidAdvisor.get("*", True)
    # assert result, "pidAdvisor returned an empty data dictionary?"

    # if result is not None:
    pidAdvisor.set("todevice", 1)
    p_advisor = result["/pid/p"][0]
    i_advisor = result["/pid/i"][0]
    d_advisor = result["/pid/d"][0]

    print(
    f"The pidAdvisor calculated the following gains, \
        P: {p_advisor}, I: {i_advisor}, D: {d_advisor}.")
    a = 1-p_advisor
    print(target_bw,i_advisor,a)
    # sleep_time = 0.7/target_bw + 2.303/((-i_advisor)/a)
    # print("步进电机停留时间为%f"%sleep_time)
    line_kp.setText(str(round(p_advisor,2)))
    line_ki.setText(str(round(i_advisor,2))) 
    line_kd.setText(str(round(d_advisor,2)))

def pid_start(pid_value,pid_setpoint):
# 开启PID：pid_value 默认为0，点击按钮时若为0，则设为1开启，若为1，则设为0关闭
    global setpoint
    setpoint_percent = pid_setpoint
    pid_index = 0  # PID index.
    ##输入信号的峰值
    print("max_sigin=%f"%(max_r))
    setpoint = setpoint_percent*max_r
    phase_unwrap = False
    out_channel = 0
    out_mixer_channel = 1
    print("setpoint值为：%f"%(setpoint))
    print(pid_value.text())
    if pid_value.text()=="PID开始":
        time.sleep(1)
        exp_setting = [
        # ["/%s/sigouts/%d/on" % (labone, out_channel), 1],
        # ["/%s/sigouts/%d/enables/%d" % (labone, out_channel, out_mixer_channel), True],
        # ["/%s/sigouts/%d/range" % (labone, out_channel), 0.01],
        # ["/%s/sigouts/%d/amplitudes/%d" % (labone, out_channel, out_mixer_channel), 0.01],
        ["/%s/pids/%d/setpoint" % (labone, pid_index), setpoint],
        ["/%s/pids/%d/enable" % (labone, pid_index), True],
        ["/%s/pids/%d/phaseunwrap" % (labone, pid_index), phase_unwrap],
        ["/%s/pids/%d/keepint" % (labone, pid_index), 1],
        ["/%s/oscs/%d/freq" % (labone, 0), h_frequency],
        ]
        daq.set(exp_setting)
        pid_value.setText("PID结束")
    else:
        daq.set([["/%s/pids/%d/enable" % (labone, pid_index), False]])
        pid_value.setText("PID开始")

def change_pid_para(p_value,i_value,daq,device):
# 实时改动pid
    t=th.Thread(target=change_pid_para_thread,args=(p_value,i_value,daq,device))
    t.isDaemon(True)
    t.start()

def change_pid_para_thread(p_value,i_value,daq,device):
    daq.set(["%s/PIDS/0/p" % (device), p_value])
    daq.set(["%s/PIDS/0/i" % (device), i_value])

def move_forward(prograss,widget_1,aux_widget,approach_speed,approach_step,approach_second_step,delaytime):
# 使用步进电机移动
# 设置参数：每次移动完成后电机状态（开为1，闭为0）
    global approach_state,motor_id,motor
    approach_state = 1
    print("setpoint值为：%f"%(setpoint))
    vol_data = daq.getSample("/%s/demods/%d/sample" % (labone, 0))
    vol = np.abs(vol_data['x'][0]+1j*vol_data['y'][0])
    aux = daq.get('/%s/pids/%d/value'%(labone,0))
    aux_out = aux['dev4346']['pids']['0']['value']['value'][0]    
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
    currentDeviceSettings.Drive.Channel(InertialMotorStatus.MotorChannels.Channel1).StepAcceleration = 10000 # 设置加速时间
    currentDeviceSettings.Jog.Channel(InertialMotorStatus.MotorChannels.Channel1).JogStep = approach_step # 设置行走距离
    motor.SetSettings(currentDeviceSettings, True, True)
    time_start = time.time()
    step_start = motor.GetPosition(InertialMotorStatus.MotorChannels.Channel1)
    print(vol,setpoint,approach_state)
    while(vol >= setpoint and approach_state == 1):
        # 步进前进
        motor.Jog(InertialMotorStatus.MotorChannels.Channel1,InertialMotorJogDirection.Increase,60000)
        # 获取新的vol、aux数值
        vol_data = daq.getSample("/%s/demods/%d/sample" % (labone, 0))
        vol = np.abs(vol_data['x'][0]+1j*vol_data['y'][0])
        aux = daq.get('/%s/pids/%d/value'%(labone,0))
        aux_out=aux['dev4346']['pids']['0']['value']['value'][0]
        ax,canvas,fig = plot_2D(widget_1)
        ax_2,canvas_2,fig_2 = plot_2D(aux_widget)
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
    while(aux_out-3.5 > 0.1 and approach_state == 1):
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
        ax,canvas,fig = plot_2D(widget_1)
        ax_2,canvas_2,fig_2 = plot_2D(aux_widget)
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
    if(aux_out-3.5<=0.1):
        print("进针完成")
    prograss.setValue(100)
    motor.StopPolling()
    motor.ShutDown()

def move_stop():
    global approach_state
    approach_state = 0

def move_backword(step):
    global motor,motor_id
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
    currentDeviceSettings.Drive.Channel(InertialMotorStatus.MotorChannels.Channel1).StepRate = 500 # 设置步速
    currentDeviceSettings.Drive.Channel(InertialMotorStatus.MotorChannels.Channel1).StepAcceleration = 10000 # 设置加速时间
    currentDeviceSettings.Jog.Channel(InertialMotorStatus.MotorChannels.Channel1).JogStep = step # 设置行走距离
    motor.SetSettings(currentDeviceSettings, True, True)
    for i in range(0,5):
        motor.Jog(InertialMotorStatus.MotorChannels.Channel1,InertialMotorJogDirection.Decrease,60000)
        # 获取新的vol、aux数值
        vol_data = daq.getSample("/%s/demods/%d/sample" % (labone, 0))
        vol = np.abs(vol_data['x'][0]+1j*vol_data['y'][0])
        aux = daq.get('/%s/pids/%d/value'%(labone,0))
        aux_out=aux['dev4346']['pids']['0']['value']['value'][0]
        # 读取当前vol、aux、步进、压电位移台数值
        print("vol的值为%f"%vol)
        print("aux_out的值为%f"%aux_out)
        print(motor.GetPosition(InertialMotorStatus.MotorChannels.Channel1))
        # print(dll.MCL_SingleReadZ(self.mcl))
        time.sleep(0.2)
    motor.StopPolling()
    motor.ShutDown()

def scan_picture(prograss_2,widget,scan_width,scan_height,scan_unit,scan_delay_time,mode):
    global scan_state,scan_data
    scan_state = 1
    point_x = int(scan_width/scan_unit)
    point_y = int(scan_height/scan_unit)
    print(dll.MCL_SingleReadZ(handle))
    scan_unit = scan_unit/1000
    scan_data = [[0 for j in range(0,point_y)]for i in range(0,point_x)]
    scan_data_aux = [[0 for j in range(0,point_y)]for i in range(0,point_x)]
    widget.show()
    count = 0
    if mode == "横扫":
        for i in range(0,point_x):
            for j in range(0,point_y):
                # 平移
                if(scan_state==1):
                    count += 1
                    time.sleep(scan_delay_time)
                    ax,canvas,fig = plot_2D(widget)
                    scan_data[i][j] = dll.MCL_SingleReadZ(handle) # 读取地形
                    heatmap = ax.imshow(scan_data, cmap='hot', interpolation='nearest')
                    fig.colorbar(heatmap,extend='neither')
                    canvas.draw()
                    QApplication.processEvents()  # 强制刷新窗口
                    prograss_2.setValue(count/(point_x*point_y)*100)
                    data_aux = daq.getSample("/%s/demods/%d/sample" % (labone, 0)) # 读取电压
                    if(i%2==0):
                        scan_data_aux[i][j] = np.abs(data_aux['x'][0]+1j*data_aux['y'][0])
                    else:
                        scan_data_aux[i][point_y-j-1] = np.abs(data_aux['x'][0]+1j*data_aux['y'][0])
                    if (j < point_y - 1 and i%2==0):
                        dll.MCL_SingleWriteN(ctypes.c_double((j+1)*scan_unit),1,handle) # x轴移动
                    elif(j < point_y - 1 and i%2==1):
                        dll.MCL_SingleWriteN(ctypes.c_double((point_y-j-2)*scan_unit),1,handle)
                    else:
                        dll.MCL_SingleWriteN(ctypes.c_double((i+1)*scan_unit),2,handle)
                    print("z运动",dll.MCL_SingleReadZ(handle),"x运动",dll.MCL_SingleReadN(1,handle),"y运动",dll.MCL_SingleReadN(2,handle)
                          ,"x位置",i,"y位置",j)
                else:
                    pass
        prograss_2.setValue(100)
    else :
        for i in range(0,point_x):
            for j in range(0,point_y):
                # 平移
                if(scan_state==1):
                    count += 1
                    time.sleep(scan_delay_time)
                    ax,canvas,fig = plot_2D(widget)
                    if(i%2==0):
                        scan_data[i][j] = dll.MCL_SingleReadZ(handle) # 读取地形
                    else:
                        scan_data[i][point_y-j-1] = dll.MCL_SingleReadZ(handle)
                    print(dll.MCL_SingleReadZ(handle))
                    heatmap = ax.imshow(scan_data, cmap='hot', interpolation='nearest')
                    fig.colorbar(heatmap,extend='neither')
                    canvas.draw()
                    QApplication.processEvents()  # 强制刷新窗口
                    prograss_2.setValue(count/(point_x*point_y)*100)
                    if (j < point_y-1 and i%2==0):
                        dll.MCL_SingleWriteN(ctypes.c_double((j+1)*scan_unit),2,handle) # y轴移动
                    elif(j < point_y-1 and i%2==1):
                        dll.MCL_SingleWriteN(ctypes.c_double((point_y-j-2)*scan_unit),2,handle)
                    else:
                        dll.MCL_SingleWriteN(ctypes.c_double((i+1)*scan_unit),1,handle)
                    print("z运动",dll.MCL_SingleReadZ(handle),"x运动",dll.MCL_SingleReadN(1,handle),"y运动",dll.MCL_SingleReadN(2,handle)
                          ,"x位置",i,"y位置",j)
                else:
                    pass
        prograss_2.setValue(100)
def scan_stop():
    global scan_state
    scan_state = 0

def save_figure(widget):
    # 打开文件对话框
    arr = np.array(scan_data)
    # 获取当前时间
    now = datetime.datetime.now()

    # 格式化日期时间
    date_time = now.strftime("%Y-%m-%d_%H-%M-%S")

    # 生成文件名并保存数组
    file_name = f"my_array_{date_time}.npy"
    np.save(file_name, arr)
    # 将数组保存到本地
    np.save('my_array.npy', arr)
    filename, _ = QFileDialog.getSaveFileName(widget, "Save Image", "", "PNG(*.png);;JPEG(*.jpg *.jpeg)")
    if filename:
        # 保存图像
        pixmap = widget.grab()
        size = widget.size()
        pixmap_scaled = pixmap.scaled(size)
        pixmap_scaled.save(filename)
        # 显示保存成功的消息框
        QMessageBox.information(widget, "Saved", "The image has been saved.", QMessageBox.Ok)
