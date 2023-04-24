# 压电位移台库
import ctypes
# 其他库
import time
import numpy as np
from PyQt5.QtWidgets import QApplication,QMessageBox,QFileDialog
import datetime
import basic.plot

def scan(dll,handle,prograss_2,widget,scan_width,scan_height,scan_unit,scan_delay_time,mode,mcl_state):
    if(handle==0):
        handle = dll.MCL_InitHandle()
        if(handle==1):
            mcl_state.setText("已连接")
            dll.MCL_SingleReadN.restype = ctypes.c_double
            dll.MCL_SingleReadZ.restype = ctypes.c_double
        else:
            mcl_state.setText("未连接")
    global scan_state,scan_data
    scan_state = 1
    point_x = int(scan_width/scan_unit)
    point_y = int(scan_height/scan_unit)
    print(dll.MCL_SingleReadZ(handle))
    scan_unit = scan_unit/1000
    scan_data = [[0 for j in range(0,point_y)]for i in range(0,point_x)]
    widget.show()
    count = 0
    if mode == "横扫":
        for i in range(0,point_x):
            for j in range(0,point_y):
                # 平移
                if(scan_state==1):
                    count += 1
                    time.sleep(scan_delay_time)
                    ax,canvas,fig = basic.plot.plot_2D(widget)
                    scan_data[i][j] = dll.MCL_SingleReadZ(handle) # 读取地形
                    heatmap = ax.imshow(scan_data, cmap='hot', interpolation='nearest')
                    fig.colorbar(heatmap,extend='neither')
                    canvas.draw()
                    QApplication.processEvents()  # 强制刷新窗口
                    prograss_2.setValue(count/(point_x*point_y)*100)
                    if (j < point_y - 1):
                        dll.MCL_SingleWriteN(ctypes.c_double((j+1)*scan_unit),1,handle) # x轴移动
                    else:
                        dll.MCL_SingleWriteN(ctypes.c_double((i+1)*scan_unit),2,handle)
                        dll.MCL_SingleWriteN(ctypes.c_double(0),1,handle) # x轴移动
                        time.sleep(scan_delay_time*10)
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
                    ax,canvas,fig = basic.plot.plot_2D(widget)
                    scan_data[i][j] = dll.MCL_SingleReadZ(handle) # 读取地形
                    print(dll.MCL_SingleReadZ(handle))
                    heatmap = ax.imshow(scan_data, cmap='hot', interpolation='nearest')
                    fig.colorbar(heatmap,extend='neither')
                    canvas.draw()
                    QApplication.processEvents()  # 强制刷新窗口
                    prograss_2.setValue(count/(point_x*point_y)*100)
                    if (j < point_y-1):
                        dll.MCL_SingleWriteN(ctypes.c_double((j+1)*scan_unit),2,handle) # y轴移动
                    else:
                        dll.MCL_SingleWriteN(ctypes.c_double((i+1)*scan_unit),1,handle)
                        dll.MCL_SingleWriteN(ctypes.c_double(0),2,handle) # y轴移动
                        time.sleep(scan_delay_time*10)
                    print("z运动",dll.MCL_SingleReadZ(handle),"x运动",dll.MCL_SingleReadN(1,handle),"y运动",dll.MCL_SingleReadN(2,handle)
                          ,"x位置",i,"y位置",j)
                else:
                    pass
        prograss_2.setValue(100)

def scan_stop():
    global scan_state
    scan_state = 0

def scan_save(widget):
    global scan_data
    # 打开文件对话框
    arr = np.array(scan_data)
    # 获取当前时间
    now = datetime.datetime.now()
    # 格式化日期时间
    date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
    # 生成文件名并保存数组
    file_name = f"my_array_{date_time}.npy"
    file_name_2 = f"my_array_{date_time}.txt"
    np.save(file_name, arr)
    # 将数组保存到本地
    np.savetxt(file_name_2,arr)
    filename, _ = QFileDialog.getSaveFileName(widget, "Save Image", "", "PNG(*.png);;JPEG(*.jpg *.jpeg)")
    if filename:
        # 保存图像
        pixmap = widget.grab()
        size = widget.size()
        pixmap_scaled = pixmap.scaled(size)
        pixmap_scaled.save(filename)
        # 显示保存成功的消息框
        QMessageBox.information(widget, "Saved", "The image has been saved.", QMessageBox.Ok)
