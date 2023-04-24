import time
import numpy as np
import basic.calculate_Q,basic.plot
from PyQt5.QtWidgets import QApplication,QMessageBox,QFileDialog
import zhinst
import re
import datetime

def sweep(device_id,progress_bar,frequency_text,Q_text,amplitude_text,sweep_label,start_sweep,stop_sweep,sample_sweep,count_sweep,mode_sweeep,bindwidth_sweep):
    hf2 = None
    apilevel_example = 1 if hf2 else 6
    (daq, labone, props) = zhinst.utils.create_api_session(device_id,apilevel_example, server_host="localhost", server_port=8004)
    zhinst.utils.api_server_version_check(daq)
    # state让sweep可以随时停止
    global state
    state = 1
    # mode是扫频的方式（线性，对数）
    if re.search("线性", mode_sweeep):
        mode = 0
    elif re.search("对数",mode_sweeep):
        mode = 1
    sweeper = daq.sweep()
    # 仪器号
    sweeper.set("device", labone)
    # 解调通道
    sweeper.set("gridnode", "oscs/%d/freq" % 0)
    # 开始扫频
    sweeper.set("start", start_sweep)
    # 结束扫频
    sweeper.set("stop", stop_sweep)
    # 扫频点
    sweeper.set("samplecount", sample_sweep)
    # 扫频方式
    sweeper.set("xmapping", mode)
    # 设置扫频次数
    sweeper.set("loopcount", count_sweep)
    # 设置带宽控制方式（固定带宽）
    sweeper.set("bandwidthcontrol", 1)
    # 设置扫频带宽
    sweeper.set("bandwidth", bindwidth_sweep)
    # 默认设置
    sweeper.set("bandwidthoverlap", 0)
    sweeper.set("scan", 0)
    sweeper.set("settling/time", 0)
    sweeper.set("settling/inaccuracy", 0.001)
    # 设置有效计算时间
    sweeper.set("averaging/tc", 0)
    # 设置计算样本
    sweeper.set("averaging/sample", 10)
    path = "/%s/demods/%d/sample" % (labone,0)
    sweeper.subscribe(path)
    sweeper.set("save/filename", "sweep_with_save")
    sweeper.set("save/fileformat", "hdf5")
    sweeper.execute()
    print("扫频参数设置完成")
    start = time.time()
    timeout = 20000  # [s]
    print("Will perform", count_sweep, "sweeps...")
    while not sweeper.finished():  # Wait until the sweep is complete, with timeout.
        time.sleep(0.05)
        progress = sweeper.progress()
        print(f"Individual sweep progress: {progress[0]:.2%}.", end="\r")
        progress_bar.setValue(progress*100)
        if (time.time() - start) > timeout:
            print("\nSweep still not finished, forcing finish...")
            sweeper.finish()
        elif(state==0):
            sweeper.finish()
        QApplication.processEvents()  # 强制刷新窗口
    return_flat_dict = True
    data = sweeper.read(return_flat_dict)
    sweeper.unsubscribe(path)
    samples = data[path]
    print("Returned sweeper data contains", len(samples), "sweeps.")
    if (progress[0]==1):
        for sample in samples:
            frequency = sample[0]["frequency"]
            R = np.abs(sample[0]["x"] + 1j * sample[0]["y"])
            r = R
            R=R.tolist()
            frequency=frequency.tolist()
            max_r = max(R)
            Q_value = basic.calculate_Q.calculate_data(frequency,R)
        sweep_x = frequency
        sweep_y = r
        h_frequency = frequency[R.index(max(R))]
        amplitude_text.setText(str(round(max_r,8)))
        Q_text.setText(str(round(Q_value,5)))
        frequency_text.setText(str(round(h_frequency,5)))
        # 获取当前时间
        now = datetime.datetime.now()
        # 将数据和时间拼接成一行文本
        line = f"{now}: {h_frequency} {Q_value} {max_r}\n"
        # 打开文件并追加数据
        with open("basic/data/sweep.txt", "a") as file:
            # 写入数据行
            file.write(line)
        ax,canvas,fig = basic.plot.plot_2D(sweep_label)
        ax.set_title("扫频图像",fontfamily='SimHei')
        ax.plot(sweep_x,sweep_y)
        canvas.draw()
        sweep_label.show()
        exp_setting_2 = [
            ["/%s/oscs/%d/freq" % (labone, 0), h_frequency],]
        daq.set(exp_setting_2)
    else:
        pass
def sweep_stop():
    global state
    state = 0

def sweep_save(label_sweep):
    filename, _ = QFileDialog.getSaveFileName(label_sweep, "Save Image", "", "PNG(*.png);;JPEG(*.jpg *.jpeg)")
    if filename:
        # 保存图像
        pixmap = label_sweep.grab()
        size = label_sweep.size()
        pixmap_scaled = pixmap.scaled(size)
        pixmap_scaled.save(filename)
        # 显示保存成功的消息框
        QMessageBox.information(label_sweep, "Saved", "The image has been saved.", QMessageBox.Ok)
