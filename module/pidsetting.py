import zhinst
import time
import reveal.plot
import re
from PyQt5 import QtWidgets
# pid计算只负责把输入的Q、amplitude、frequency进行计算，不管他们是怎么来的
def pid_calculate(device_id,pid_mode,inputchannel,inputchannel_number,
                    outputchannel,outputchannel_number,pid_module,
                    setpoint,phaseunwrap,gain,Q_value,h_frequency,h_amplitude,
                    center,lowwer,upper,targetbw,
                    kp_line,ki_line,kd_line,setpoint_data,label_pid_picture,combobox_input,combobox_output,aux_pll,aux_scale,aux_offset,
                    aux_max,aux_min,
                    pid_index):
    hf2 = False
    apilevel_example = 1 if hf2 else 6
    (daq, labone, props) = zhinst.utils.create_api_session(device_id, apilevel_example, server_host="localhost", server_port=8004)
    zhinst.utils.api_server_version_check(daq)
    # 根据不同的模式进行选择
    # 初始模式
    pid_mode_set = 0
    inputchannel_set = 2
    inputchannel_number_set = 0
    outputchannel_set = 5
    outputchannel_number_set = 2
    pid_module_set = 6
    phaseunwrap_set = 0
    aux_pll_set = -1
    # 选择pid模式
    if re.search("PID", pid_mode):
        pid_mode_set = 0
    elif(re.search("PLL", pid_mode)):
        pid_mode_set = 1
    else:
        pid_mode_set = 2
    # 选择input的模式
    if re.search("X解调",inputchannel):
        inputchannel_set = 0
    elif re.search("Y解调",inputchannel):
        inputchannel_set = 1
    elif re.search("R解调",inputchannel):
        inputchannel_set = 2
    elif re.search("θ解调",inputchannel):
        inputchannel_set = 3
    elif re.search("辅助输入",inputchannel):
        inputchannel_set = 4   
    elif re.search("辅助输出",inputchannel):
        inputchannel_set = 5
    # 选择input的通道
    if re.search("1",inputchannel_number):
        inputchannel_number_set = 0
    elif re.search("2",inputchannel_number):
        inputchannel_number_set = 1
    elif re.search("3",inputchannel_number):
        inputchannel_number_set = 2
    elif re.search("4",inputchannel_number):
        inputchannel_number_set = 3
    # 选择output的模式
    if re.search("输出振幅",outputchannel):
        outputchannel_set = 0
    elif re.search("振荡频率",outputchannel):
        outputchannel_set = 2
    elif re.search("解调相位",outputchannel):
        outputchannel_set = 3
    elif re.search("辅助输出",outputchannel):
        outputchannel_set = 5   
    elif re.search("信号输出",outputchannel):
        outputchannel_set = 7   
    # 选择output的通道
    if re.search("1",outputchannel_number):
        outputchannel_number_set = 0
    elif re.search("2",outputchannel_number):
        outputchannel_number_set = 1
    elif re.search("3",outputchannel_number):
        outputchannel_number_set = 2
    elif re.search("4",outputchannel_number):
        outputchannel_number_set = 3  
    # 选择PID/PLL的模型
    if re.search("全通滤波器",pid_module):
         pid_module_set = 0
    elif re.search("一阶低通滤波",pid_module):
         pid_module_set = 1
    elif re.search("二阶低通滤波",pid_module):
         pid_module_set = 2
    elif re.search("谐振器频率",pid_module):
         pid_module_set = 3
    elif re.search("锁相环",pid_module):
         pid_module_set = 4
    elif re.search("VCO",pid_module):
         pid_module_set = 5
    elif re.search("谐振器振幅",pid_module):
         pid_module_set = 6
    # 选择是否相位重建
    if re.search("是",phaseunwrap):
         phaseunwrap_set = 1
    elif re.search("否",phaseunwrap):
         phaseunwrap_set = 0
    # 选择新增辅助输出通道
    if re.search("X解调",aux_pll):
        aux_pll_set = 0
    elif re.search("Y解调",aux_pll):
        aux_pll_set = 1
    elif re.search("R解调",aux_pll):
        aux_pll_set = 2
    elif re.search("θ解调",aux_pll):
        aux_pll_set = 3
    elif re.search("PID输出",aux_pll):
        aux_pll_set = 5
    elif re.search("PID Shift",aux_pll):
        aux_pll_set = 9
    elif re.search("PID Error",aux_pll):
        aux_pll_set = 10
    elif re.search("TU filtered",aux_pll):
        aux_pll_set = 11   
    elif re.search("TU Output",aux_pll):
        aux_pll_set = 13     
    elif re.search("Manual",aux_pll):
        aux_pll_set = -1             
    if(pid_mode_set==0):
        # setpoint值
        daq.set([['/%s/pids/%d/mode'%(labone,pid_index), pid_mode_set],
        ["/%s/pids/%d/setpoint" % (labone, pid_index), setpoint],
        ['/%s/pids/%d/input'%(labone,pid_index), inputchannel_set],
        ['/%s/pids/%d/inputchannel'%(labone,pid_index), inputchannel_number_set],
        ['/%s/pids/%d/output'%(labone,pid_index), outputchannel_set],
        ['/%s/pids/%d/outputchannel'%(labone,pid_index), outputchannel_number_set],
        ["/%s/pids/%d/phaseunwrap" % (labone, pid_index), phaseunwrap_set],
        ['/%s/pids/%d/center'%(labone,pid_index), center],
        ['/dev4346/pids/%d/limitlower'%(pid_index), lowwer],
        ['/dev4346/pids/%d/limitupper'%(pid_index), upper]])
    elif(pid_mode_set==1):
        daq.set([['/%s/pids/%d/mode'%(labone,pid_index), pid_mode_set],
        ['/%s/pids/%d/input'%(labone,pid_index), 3],
        ['/%s/pids/%d/inputchannel'%(labone,pid_index), inputchannel_number_set],
        ['/%s/pids/%d/output'%(labone,pid_index), 2],
        ['/%s/pids/%d/outputchannel'%(labone,pid_index), outputchannel_number_set],
        ["/%s/pids/%d/phaseunwrap" % (labone, pid_index), phaseunwrap_set],
        ['/%s/pids/%d/center'%(labone,pid_index), center],
        ["/%s/pids/%d/setpoint" % (labone, pid_index), setpoint],
        ['/dev4346/pids/%d/limitlower'%(pid_index), lowwer],
        ['/dev4346/pids/%d/limitupper'%(pid_index), upper],
        ['/dev4346/auxouts/%d/outputselect'%(pid_index), aux_pll_set],
        ['/dev4346/auxouts/%d/scale'%(pid_index), aux_scale],
        ['/dev4346/auxouts/%d/offset'%(pid_index), aux_offset],
        ['/dev4346/auxouts/%d/limitlower'%(pid_index), aux_min],
        ['/dev4346/auxouts/%d/limitupper'%(pid_index), aux_max],
        ])
        combobox_input.setCurrentIndex(3)
        combobox_output.setCurrentIndex(1) 
    pidAdvisor = daq.pidAdvisor()
    pidAdvisor.set("device", labone)
    pidAdvisor.set("auto", False)
    pidAdvisor.set("pid/targetbw", targetbw)
    #PI
    pidAdvisor.set("pid/mode", 3)
    # PID index to use (first PID of device: 0)
    pidAdvisor.set("index", pid_index)
    # source = 6: Resonator amplitude
    pidAdvisor.set("dut/source", pid_module_set)
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
    print(targetbw,i_advisor,a)
    # sleep_time = 0.7/target_bw + 2.303/((-i_advisor)/a)
    # print("步进电机停留时间为%f"%sleep_time)
    kp_line.setText(str(round(p_advisor,5)))
    ki_line.setText(str(round(i_advisor,5))) 
    kd_line.setText(str(round(d_advisor,5)))
    setpoint_data.setText(str(round(setpoint,8)))
    
    step_x = result["/step"][0]["x"]
    step_grid = result["/step"][0]["grid"]

    ax,canvas,fig = reveal.plot.plot_2D(label_pid_picture)
    ax.set_title("PID/PLL阶跃图像",fontfamily='SimHei')
    ax.plot(step_grid,step_x)
    canvas.draw()
    label_pid_picture.show()

# 打开PID
def pid_open(kp_line,ki_line,kd_line,device_id,pid_value,pid_setpoint,pid_index):
# 开启PID：pid_value 默认为0，点击按钮时若为0，则设为1开启，若为1，则设为0关闭
    hf2 = False
    apilevel_example = 1 if hf2 else 6
    (daq, labone, props) = zhinst.utils.create_api_session(device_id, apilevel_example, server_host="localhost", server_port=8004)
    zhinst.utils.api_server_version_check(daq)
    exp_setting = [
    ["/%s/pids/%d/p"%(labone,pid_index),float(kp_line.text())],
    ["/%s/pids/%d/i"%(labone,pid_index),float(ki_line.text())],
    ["/%s/pids/%d/d"%(labone,pid_index),float(kd_line.text())],
    ["/%s/pids/%d/setpoint" % (labone, pid_index), pid_setpoint],
    ["/%s/pids/%d/enable" % (labone, pid_index), True],
    ["/%s/pids/%d/keepint" % (labone, pid_index), 1],
    ]
    daq.set(exp_setting)
    pid_value.setText("已开启")
def pid_close(device_id,pid_value,pid_index):
    hf2 = False
    apilevel_example = 1 if hf2 else 6
    (daq, labone, props) = zhinst.utils.create_api_session(device_id, apilevel_example, server_host="localhost", server_port=8004)
    zhinst.utils.api_server_version_check(daq)
    exp_setting = [
    ["/%s/pids/%d/enable" % (labone, pid_index), False],
    ]
    daq.set(exp_setting)
    pid_value.setText("未开启")

# 通道1
def load_para_1(ui):
    #  filePath, filetype = QtWidgets.QFileDialog.getOpenFileName(ui, "选取文件", "./",
    #                                                                     "*.*")
    #  file2 = open(filePath, "r")
    pass

def pid_calculate_1(device,pid_mode,inputchannel,inputchannel_number,
                    outputchannel,outputchannel_number,pid_module,
                    setpoint,phaseunwrap,gain,Q_value,h_frequency,h_amplitude,
                    center,lowwer,upper,targetbw,
                    kp_line,ki_line,kd_line,setpoint_data,label_pid_picture,combobox_input,combobox_output,aux_pll,aux_scale,aux_offset,
                    aux_max,aux_min):
    pid_calculate(device,pid_mode,inputchannel,inputchannel_number,
                    outputchannel,outputchannel_number,pid_module,
                    setpoint,phaseunwrap,gain,Q_value,h_frequency,h_amplitude,
                    center,lowwer,upper,targetbw,
                    kp_line,ki_line,kd_line,setpoint_data,label_pid_picture,combobox_input,combobox_output,aux_pll,aux_scale,aux_offset,
                    aux_max,aux_min,pid_index=0)

def pid_open_1(kp_line,ki_line,kd_line,device,pid_value,pid_setpoint):
    pid_open(kp_line,ki_line,kd_line,device,pid_value,pid_setpoint,pid_index=0)

def pid_close_1(device,pid_value):
    pid_close(device,pid_value,pid_index=0)

# 通道2
def load_para_2():
    pass
def pid_calculate_2(device,pid_mode,inputchannel,inputchannel_number,
                    outputchannel,outputchannel_number,pid_module,
                    setpoint,phaseunwrap,gain,Q_value,h_frequency,h_amplitude,
                    center,lowwer,upper,targetbw,
                    kp_line,ki_line,kd_line,setpoint_data,label_pid_picture,combobox_input,combobox_output,aux_pll,aux_scale,aux_offset,
                    aux_max,aux_min):
    pid_calculate(device,pid_mode,inputchannel,inputchannel_number,
                    outputchannel,outputchannel_number,pid_module,
                    setpoint,phaseunwrap,gain,Q_value,h_frequency,h_amplitude,
                    center,lowwer,upper,targetbw,
                    kp_line,ki_line,kd_line,setpoint_data,label_pid_picture,combobox_input,combobox_output,aux_pll,aux_scale,aux_offset,
                    aux_max,aux_min,pid_index=1)

def pid_open_2(kp_line,ki_line,kd_line,device,pid_value,pid_setpoint):
    pid_open(kp_line,ki_line,kd_line,device,pid_value,pid_setpoint,pid_index=1)

def pid_close_2(device,pid_value):
    pid_close(device,pid_value,pid_index=1)
# 通道3
def load_para_3():
    pass

def pid_calculate_3(device,pid_mode,inputchannel,inputchannel_number,
                    outputchannel,outputchannel_number,pid_module,
                    setpoint,phaseunwrap,gain,Q_value,h_frequency,h_amplitude,
                    center,lowwer,upper,targetbw,
                    kp_line,ki_line,kd_line,setpoint_data,label_pid_picture,combobox_input,combobox_output,aux_pll,aux_scale,aux_offset,
                    aux_max,aux_min):
    pid_calculate(device,pid_mode,inputchannel,inputchannel_number,
                    outputchannel,outputchannel_number,pid_module,
                    setpoint,phaseunwrap,gain,Q_value,h_frequency,h_amplitude,
                    center,lowwer,upper,targetbw,
                    kp_line,ki_line,kd_line,setpoint_data,label_pid_picture,combobox_input,combobox_output,aux_pll,aux_scale,aux_offset,
                    aux_max,aux_min,pid_index=2)

def pid_open_3(kp_line,ki_line,kd_line,device,pid_value,pid_setpoint):
    pid_open(kp_line,ki_line,kd_line,device,pid_value,pid_setpoint,pid_index=2)

def pid_close_3(device,pid_value):
    pid_close(device,pid_value,pid_index=2)
# 通道4
def load_para_4():
    pass

def pid_calculate_4(device_id,pid_mode,inputchannel,inputchannel_number,
                    outputchannel,outputchannel_number,pid_module,
                    setpoint,phaseunwrap,gain,Q_value,h_frequency,h_amplitude,
                    center,lowwer,upper,targetbw,
                    kp_line,ki_line,kd_line,setpoint_data,label_pid_picture,combobox_input,combobox_output,aux_pll,aux_scale,aux_offset,
                    aux_max,aux_min):
    pid_calculate(device_id,pid_mode,inputchannel,inputchannel_number,
                    outputchannel,outputchannel_number,pid_module,
                    setpoint,phaseunwrap,gain,Q_value,h_frequency,h_amplitude,
                    center,lowwer,upper,targetbw,
                    kp_line,ki_line,kd_line,setpoint_data,label_pid_picture,combobox_input,combobox_output,aux_pll,aux_scale,aux_offset,
                    aux_max,aux_min,pid_index=3)

def pid_open_4(kp_line,ki_line,kd_line,device,pid_value,pid_setpoint):
    pid_open(kp_line,ki_line,kd_line,device,pid_value,pid_setpoint,pid_index=3)

def pid_close_4(device,pid_value):
    pid_close(device,pid_value,pid_index=3)
