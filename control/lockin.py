import zhinst.utils
import re
import time
import datetime
import numpy as np


class Lockin:
    def __init__(self):
        # 仪器参数
        self.device_id = "dev4346"
        self.api_example = 6
        self.server_host: str = "localhost"
        self.server_port = 8004
        self.daq = None
        self.labone = None
        self.props = None
        # 锁相放大器设置参数
        # 锁相放大器开关、输入电压、
        self.lockin_state = 1 # 锁相状态为开
        self.output_voltage = 0.01 # 输出电压为0.01V
        self.output_voltage_0 = 1 # 输出电压0状态为开
        self.output_voltage_1 = 0 # 输出电压1状态为关 
        self.frequency = 32768 # 解调频率为32768hz
        self.rate = 100000 # 采样率
        self.input_channel = 1 # 解调通道
        self.bindwidth = 100 # 锁相带宽
        self.range = 1
        self.oscselect = 0
        self.autorange = 1
        # 锁相放大器扫频参数
        self.sweep_state = 0
        self.sweeper = None
        self.sweep_prograss = 1
        self.sweepStart = 30000
        self.sweepStop = 35000
        self.sweepSample = 100
        self.sweepCount = 1
        self.sweepMode = 0
        self.sweepBindwidth = 100
        # 扫频其他参数
        self._sweepPrograss = None
        self._sweepPath = None
        self._sweep_Data = None
        # 扫频结果
        self.sweepMaxr = 0
        self.sweepHfrequency = 0
        self.sweepQvalue = 0
        
    def connect(self):
        # 连接仪器
        try:
            (self.daq,self.labone,self.props) = zhinst.utils.create_api_session(self.device_id,
                self.api_example,server_host=self.server_host,server_port=self.server_port)
            zhinst.utils.api_server_version_check(self.daq)
            # return 1
        except:
            pass
            # return 0

    def para_setting(self,**kwargs):
        # 可以通过函数改变锁相放大器的值
        for key,value in kwargs.items():
            # 改变类中变量值
            setattr(self,key,value)
            # 将类中变量值全部传递到仪器中
            # if (len(key)==4):
            #     exp_setting = [[key,value],]
            # elif(len(key)==5):
            #     exp_setting = [["/%s/%s/%d/%s/%d"%key,value],]
            # self.daq.set(exp_setting)
            self.daq.set(key,value)
            self.daq.sync()

    def sweep(self):
        # 调用扫频模块，返回扫频图像的数组
        self.sweep_state = 1
        # mode是扫频的方式（线性，对数）
        if re.search("线性", self.sweepMode):
            self.sweepMode = 0
        elif re.search("对数",self.sweepMode):
            self.sweepMode = 1
        # 设置扫描参数
        self.sweeper = self.daq.sweep()
        # 仪器号
        self.sweeper.set("device", self.labone)
        # 解调通道
        self.sweeper.set("gridnode", "oscs/%d/freq" % 0)
        # 开始扫频
        self.sweeper.set("start", self.sweepStart)
        # 结束扫频
        self.sweeper.set("stop", self.sweepStop)
        # 扫频点
        self.sweeper.set("samplecount", self.sweepSample)
        # 扫频方式
        self.sweeper.set("xmapping", self.sweepMode)
        # 设置扫频次数
        self.sweeper.set("loopcount", self.sweepCount)
        # 设置带宽控制方式（固定带宽）
        self.sweeper.set("bandwidthcontrol", 1)
        # 设置扫频带宽
        self.sweeper.set("bandwidth", self.sweepBindwidth)
        # 默认设置
        self.sweeper.set("bandwidthoverlap", 0)
        self.sweeper.set("scan", 0)
        self.sweeper.set("settling/time", 0)
        self.sweeper.set("settling/inaccuracy", 0.001)
        # 设置有效计算时间
        self.sweeper.set("averaging/tc", 0)
        # 设置计算样本
        self.sweeper.set("averaging/sample", 10)
        self._sweepPath = "/%s/demods/%d/sample" % (self.labone,0)
        self.sweeper.subscribe(self._sweepPath)
        self.sweeper.set("save/filename", "sweep_with_save")
        self.sweeper.set("save/fileformat", "hdf5")
        self.sweeper.execute()
        # 开始扫频
        start = time.time()
        timeout = 20000  # [s]
        while not self.sweeper.finished():  # Wait until the sweep is complete, with timeout.
            time.sleep(0.05)
            self._sweepPrograss = self.sweeper.progress()
            print(f"Individual sweep progress: {self._sweepPrograss[0]:.2%}.", end="\r")
            # 此处有一个返回值，返回的是sweep函数的进度(可以根据需要选择_掉不需要的返回值)
            yield self._sweepPrograss*100
            """
            此处可加入数据实时展示
            """
            # 三种情况退出：扫频超过时间、手动退出、扫频完成
            if (time.time() - start) > timeout:
                self.sweeper.finish()
            elif(self.sweep_state==0):
                self.sweeper.finish()
        # 扫频结束后数据处理
        return_flat_dict = True
        self._sweep_Data = self.sweeper.read(return_flat_dict)
        self.sweeper.unsubscribe(self._sweepPath)
    
    def sweep_data(self):
        # samples 是一堆原始数据，需要从中根据标签找到想要的值
        samples = self._sweep_Data[self._sweepPath]
        # 只有当进度条为100%的时候执行显示数据
        if (self._sweepPrograss[0]==1):
            for sample in samples:
                # 获取频率
                frequency = sample[0]["frequency"]
                R = np.abs(sample[0]["x"] + 1j * sample[0]["y"])
                r = R
                R = R.tolist()
                frequency = frequency.tolist()
                self.sweepMaxr = max(R)
                self.sweepQvalue = basic.calculate_Q.calculate_data(frequency,R)
            sweep_x = frequency
            sweep_y = r
            self.sweepHfrequency = frequency[R.index(max(R))]
            exp_setting_2 = [["/%s/oscs/%d/freq" % (self.labone, 0), self.sweepHfrequency],]
            self.daq.set(exp_setting_2)
            # 此处还有三个返回值
            yield sweep_x,sweep_y,self.sweepMaxr,self.sweepQvalue,self.sweepHfrequency
            # # 获取当前时间
            # now = datetime.datetime.now()
            # # 将数据和时间拼接成一行文本
            # line = f"{now}: {h_frequency} {Q_value} {max_r}\n"
            # # 打开文件并追加数据
            # with open("basic/data/sweep.txt", "a") as file:
            #     # 写入数据行
            #     file.write(line)
            # ax,canvas,fig = basic.plot.plot_2D(sweep_label)
            # ax.set_title("扫频图像",fontfamily='SimHei')
            # ax.plot(sweep_x,sweep_y)
            # canvas.draw()
            # sweep_label.show()
        else:
            pass

    def sweep_stop(self):
        # 随时关闭sweep扫频
        self.sweep_stop = 0

    def pid_setting(self):
        # pid参数设定
        pass

    def data_getting(self):
        # 数据获取(获取全部数据，前面的函数根据需求选取对应值)
        vol_data = self.daq.getSample("/%s/demods/%d/sample" % (self.labone, 0))
        vol = np.abs(vol_data['x'][0]+1j*vol_data['y'][0])
        vol_data = self.daq.get('/%s/auxouts/%d/value'%(self.labone,0)) # pid auouts
        vol = vol_data["dev4346"]["auxouts"]["0"]["value"]["value"][0]
        aux = self.daq.get('/%s/pids/%d/value'%(self.labone,1))
        aux_out = aux['dev4346']['pids']['1']['value']['value'][0] 
