# 压电位移台库
import ctypes
# 其他库
import time
import numpy as np
from PyQt5.QtWidgets import QApplication,QMessageBox,QFileDialog
import datetime
import reveal.plot
import re
import zhinst

def scan(dll,handle,prograss_2,widget,scan_width,scan_height,scan_unit,scan_delay_time,mode,mcl_state,widget_double,widget_voltage):
    hf2 = False
    apilevel_example = 1 if hf2 else 6
    (daq, labone, props) = zhinst.utils.create_api_session("dev4346", apilevel_example, server_host="localhost", server_port=8004)
    zhinst.utils.api_server_version_check(daq)
    if(handle==0):
        handle = dll.MCL_InitHandle()
        if(handle==1):
            mcl_state.setText("已连接")
            dll.MCL_SingleReadN.restype = ctypes.c_double
            dll.MCL_SingleReadZ.restype = ctypes.c_double
        else:
            mcl_state.setText("未连接")
    global scan_state,scan_data,scan_data_2,scan_voltage_data
    scan_state = 1
    point_x = int(scan_width/scan_unit)
    point_y = int(scan_height/scan_unit)
    print(dll.MCL_SingleReadZ(handle))
    dll.MCL_SingleWriteN(ctypes.c_double(0),1,handle) # x轴移动
    time.sleep(1)
    dll.MCL_SingleWriteN(ctypes.c_double(0),2,handle) # y轴移动
    time.sleep(1)
    scan_unit = scan_unit/1000
    scan_0 = dll.MCL_SingleReadZ(handle) # 读取地形
    scan_data = [[scan_0 for j in range(0,point_y)]for i in range(0,point_x)]
    scan_data_2 = [[scan_0 for j in range(0,point_y)]for i in range(0,point_x)]
    scan_voltage = daq.getSample("/%s/demods/%d/sample" % (labone, 0))
    scan_voltage = np.abs(scan_voltage['x'][0]+1j*scan_voltage['y'][0])
    print(scan_voltage)
    scan_voltage_data = [[scan_voltage for j in range(0,point_y)]for i in range(0,point_x)]
    widget.show()
    widget_voltage.show()
    widget_double.show()
    count = 0
    if re.search("左侧横向扫描",mode):
        for i in range(0,point_x):
            # 第一部分前进
            for j in range(0,point_y):
                # 平移
                if(scan_state==1):
                    count += 1
                    time.sleep(scan_delay_time)
                    ax,canvas,fig = reveal.plot.plot_2D(widget)
                    ax_2,canvas_2,fig_2 = reveal.plot.plot_2D(widget_voltage)
                    scan_data[i][j] = dll.MCL_SingleReadZ(handle) # 读取地形
                    sum = 0
                    for z in range(0,5):
                        scan_voltage_1 = daq.getSample("/%s/demods/%d/sample" % (labone, 0))
                        n = np.abs(scan_voltage_1['x'][0]+1j*scan_voltage_1['y'][0])
                        sum = sum + n 
                    ave = sum/5
                    scan_voltage_data[i][j] = ave
                    print(scan_voltage_data[i][j])
                    heatmap = ax.imshow(scan_data, cmap='hot', interpolation='nearest')
                    heatmap_2 = ax_2.imshow(scan_voltage_data,cmap='hot',interpolation='nearest')
                    fig.colorbar(heatmap,extend='neither')
                    fig_2.colorbar(heatmap_2,extend="neither")
                    canvas.draw()
                    canvas_2.draw()
                    QApplication.processEvents()  # 强制刷新窗口
                    prograss_2.setValue(2*count/(point_x*point_y)*100)
                    dll.MCL_SingleWriteN(ctypes.c_double(j*scan_unit),1,handle) # x轴移动
                    print("z运动",dll.MCL_SingleReadZ(handle),"x运动",dll.MCL_SingleReadN(1,handle),"y运动",dll.MCL_SingleReadN(2,handle)
                        ,"x位置",i,"y位置",j)
                else:
                    pass
            for j in range(0,point_y):
                if(scan_state==1):
                    count += 1
                    time.sleep(scan_delay_time)
                    ax_3,canvas_3,fig_3 = reveal.plot.plot_2D(widget_double)
                    scan_data_2[i][j] = dll.MCL_SingleReadZ(handle) # 读取地形
                    heatmap_3 = ax_3.imshow(scan_data_2, cmap='hot', interpolation='nearest')
                    fig_3.colorbar(heatmap_3,extend='neither')
                    canvas_3.draw()
                    QApplication.processEvents()  # 强制刷新窗口
                    prograss_2.setValue(2*count/(point_x*point_y)*100)
                    dll.MCL_SingleWriteN(ctypes.c_double((point_y-1-j)*scan_unit),1,handle) # x轴移动
                    print("z运动",dll.MCL_SingleReadZ(handle),"x运动",dll.MCL_SingleReadN(1,handle),"y运动",dll.MCL_SingleReadN(2,handle)
                        ,"x位置",i,"y位置",j)
                else:
                    pass
            # 第三部分：y轴移动
            if(scan_state==1):
                dll.MCL_SingleWriteN(ctypes.c_double((i+1)*scan_unit),2,handle)
                time.sleep(scan_delay_time)
            else:
                pass
        prograss_2.setValue(100)
    elif re.search("右侧横向扫描",mode):
        for i in range(0,point_x):
            for j in range(0,point_y):
                # 平移
                if(scan_state==1):
                    count += 1
                    time.sleep(scan_delay_time)
                    ax,canvas,fig = reveal.plot.plot_2D(widget)
                    scan_data[i][point_y-j-1] = dll.MCL_SingleReadZ(handle) # 读取地形
                    heatmap = ax.imshow(scan_data, cmap='hot', interpolation='nearest')
                    fig.colorbar(heatmap,extend='neither')
                    canvas.draw()
                    QApplication.processEvents()  # 强制刷新窗口
                    prograss_2.setValue(count/(point_x*point_y)*100)
                    if (j < point_y - 1):
                        dll.MCL_SingleWriteN(ctypes.c_double((point_y-j-2)*scan_unit),1,handle) # x轴移动
                    else:
                        dll.MCL_SingleWriteN(ctypes.c_double((i+1)*scan_unit),2,handle)
                        dll.MCL_SingleWriteN(ctypes.c_double((point_y-1)*scan_unit),1,handle) # x轴移动
                        time.sleep(scan_delay_time*10)
                    print("z运动",dll.MCL_SingleReadZ(handle),"x运动",dll.MCL_SingleReadN(1,handle),"y运动",dll.MCL_SingleReadN(2,handle)
                          ,"x位置",i,"y位置",j)
                else:
                    pass
    elif re.search("上方纵向扫描",mode):
        for i in range(0,point_x):
            # 第一部分前进
            for j in range(0,point_y):
                # 平移
                if(scan_state==1):
                    count += 1
                    time.sleep(scan_delay_time)
                    ax,canvas,fig = reveal.plot.plot_2D(widget)
                    ax_2,canvas_2,fig_2 = reveal.plot.plot_2D(widget_voltage)
                    scan_data[i][j] = dll.MCL_SingleReadZ(handle) # 读取地形
                    sum = 0
                    for z in range(0,5):
                        scan_voltage_1 = daq.getSample("/%s/demods/%d/sample" % (labone, 0))
                        n = np.abs(scan_voltage_1['x'][0]+1j*scan_voltage_1['y'][0])
                        sum = sum + n 
                    ave = sum/5
                    scan_voltage_data[i][j] = ave
                    print(scan_voltage_data[i][j])
                    heatmap = ax.imshow(scan_data, cmap='hot', interpolation='nearest')
                    heatmap_2 = ax_2.imshow(scan_voltage_data,cmap='hot',interpolation='nearest')
                    fig.colorbar(heatmap,extend='neither')
                    fig_2.colorbar(heatmap_2,extend="neither")
                    canvas.draw()
                    canvas_2.draw()
                    QApplication.processEvents()  # 强制刷新窗口
                    prograss_2.setValue(2*count/(point_x*point_y)*100)
                    dll.MCL_SingleWriteN(ctypes.c_double(j*scan_unit),2,handle) # x轴移动
                    print("z运动",dll.MCL_SingleReadZ(handle),"x运动",dll.MCL_SingleReadN(1,handle),"y运动",dll.MCL_SingleReadN(2,handle)
                        ,"x位置",i,"y位置",j)
                else:
                    pass
            for j in range(0,point_y):
                if(scan_state==1):
                    count += 1
                    time.sleep(scan_delay_time)
                    ax_3,canvas_3,fig_3 = reveal.plot.plot_2D(widget_double)
                    scan_data_2[i][j] = dll.MCL_SingleReadZ(handle) # 读取地形
                    heatmap_3 = ax_3.imshow(scan_data_2, cmap='hot', interpolation='nearest')
                    fig_3.colorbar(heatmap_3,extend='neither')
                    canvas_3.draw()
                    QApplication.processEvents()  # 强制刷新窗口
                    prograss_2.setValue(2*count/(point_x*point_y)*100)
                    dll.MCL_SingleWriteN(ctypes.c_double((point_y-1-j)*scan_unit),2,handle) # x轴移动
                    print("z运动",dll.MCL_SingleReadZ(handle),"x运动",dll.MCL_SingleReadN(1,handle),"y运动",dll.MCL_SingleReadN(2,handle)
                        ,"x位置",i,"y位置",j)
                else:
                    pass
            # 第三部分：y轴移动
            if(scan_state==1):
                dll.MCL_SingleWriteN(ctypes.c_double((i+1)*scan_unit),1,handle)
                time.sleep(scan_delay_time)
            else:
                pass
        prograss_2.setValue(100)
    elif re.search("下方纵向扫描",mode):
        for i in range(0,point_x):
            for j in range(0,point_y):
                # 平移
                if(scan_state==1):
                    count += 1
                    time.sleep(scan_delay_time)
                    ax,canvas,fig = reveal.plot.plot_2D(widget)
                    scan_data[point_y-j-1][i] = dll.MCL_SingleReadZ(handle) # 读取地形
                    heatmap = ax.imshow(scan_data, cmap='hot', interpolation='nearest')
                    fig.colorbar(heatmap,extend='neither')
                    canvas.draw()
                    QApplication.processEvents()  # 强制刷新窗口
                    prograss_2.setValue(count/(point_x*point_y)*100)
                    if (j < point_y - 1):
                        dll.MCL_SingleWriteN(ctypes.c_double((point_x-j-2)*scan_unit),2,handle) # y轴移动
                    else:
                        dll.MCL_SingleWriteN(ctypes.c_double((i+1)*scan_unit),1,handle)
                        dll.MCL_SingleWriteN(ctypes.c_double((point_x-1)*scan_unit),2,handle) # y轴移动
                        time.sleep(scan_delay_time*10)
                    print("z运动",dll.MCL_SingleReadZ(handle),"x运动",dll.MCL_SingleReadN(1,handle),"y运动",dll.MCL_SingleReadN(2,handle)
                          ,"x位置",i,"y位置",j)
                else:
                    pass
        prograss_2.setValue(100)

def scan_stop():
    global scan_state
    scan_state = 0

def scan_save(widget,point):
    global scan_data,scan_data_2,scan_voltage_data
    # 打开文件对话框
    arr = np.array(scan_data)
    arr_2 = np.array(scan_data_2)
    arr_3 = np.array(scan_voltage_data)
    # 获取当前时间
    now = datetime.datetime.now()
    # 格式化日期时间
    date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
    # 生成文件名并保存数组
    file_name = f"my_array_{date_time}.npy"
    file_name_double_1 = f"my_array_double_{date_time}.npy"
    file_name_voltage_1 = f"my_array_voltage_{date_time}.npy"
    file_name_3 = f"my_array_3D_{date_time}.xyz"
    file_name_double = f"my_array_3D_double_{date_time}.xyz"
    file_name_voltage = f"my_array_3D_voltage_{date_time}.xyz"
    np.save(file_name, arr)
    np.save(file_name_double_1,arr_2)
    np.save(file_name_voltage_1,arr_3)
    # 将数组保存到本地
    filename, _ = QFileDialog.getSaveFileName(widget, "Save Image", "", "PNG(*.png);;JPEG(*.jpg *.jpeg)")
    if filename:
        # 保存图像
        pixmap = widget.grab()
        size = widget.size()
        pixmap_scaled = pixmap.scaled(size)
        pixmap_scaled.save(filename)
        # 显示保存成功的消息框
        QMessageBox.information(widget, "Saved", "The image has been saved.", QMessageBox.Ok)
        nd_y = [j for j in range(0,point)] # 列数
        nd_x = [i for i in range(0,point)] # 行数
        input_data = np.load(file_name)
        input_data_2 = np.load(file_name_double_1)
        input_data_3 = np.load(file_name_voltage_1)
        data = []
        data_2 = []
        data_3 = []
        for i in range(0,point):
            for j in range(0,point):
                scan = [nd_y[j],nd_x[i],input_data[i][j]]
                scan_2 = [nd_y[j],nd_x[i],input_data_2[i][j]]
                scan_3 = [nd_y[j],nd_x[i],input_data_3[i][j]]
                data.append(scan)
                data_2.append(scan_2)
                data_3.append(scan_3)
        np.savetxt(file_name_3,data,delimiter=',')
        np.savetxt(file_name_double,data_2,delimiter=',')
        np.savetxt(file_name_voltage,data_3,delimiter=',')
