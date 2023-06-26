from PyQt5.QtWidgets import QApplication, QFileDialog, QWidget
import os
import re
from PyQt5 import QtGui
import arithmetic.bresenham
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5 import sip
import io

cal = arithmetic.bresenham.Gcode()

def plot_point(gcodePointx,gcodePointy):
    """
    画图
    :return:
    """
    figsize = 7,7
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(gcodePointx, gcodePointy)  # 绘制曲线 y1
    ax.set(xlabel='Distance_X (mm)', ylabel='Distance_Y (mm)',title='Gcode 2D')
    ax.grid()
    # Move the left and bottom spines to x = 0 and y = 0, respectively.
    ax.spines["left"].set_position(("data", 0))
    ax.spines["bottom"].set_position(("data", 0))
    # Hide the top and right spines.
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    # 坐标轴上加箭头
    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)
    ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False)
    canvas = plt.gcf()
    f = io.BytesIO()
    canvas.savefig(f)
    return f
    

class Gcode:
    def __init__(self,gcodeList=[],gcodeFault=[],
                 simulation_x=[],simulation_y=[],
                 simulation_z=[]):
        self.gcodeList = gcodeList
        self.gcodeFault = gcodeFault
        self.textGcode = None
        self.errorGcode = None
        self.simulationPictureGcode_2D = None
        self.simulationPictureGcode_3D = None
        self.simulation_x = simulation_x
        self.simulation_y = simulation_y
        self.simulation_z = simulation_z
        self.stepsize = 0.01
    
    # 目的是导入Gcode
    def lead_Gcode(self):
        # 需要使用textGcode，输出一个引文
        filename, _ = QFileDialog.getOpenFileName(self.textGcode, 'Open file', '.', 'Text files (*.txt);;GCode files (*.gcode)')
        # 导入文件内容
        if filename:
            with open(filename, 'r') as file:
                content = file.read()
                # 在这里添加你的其他操作
            print(filename,"打印：filename")
            print(content,"打印：content")
            if os.path.exists(filename):
                print(os.path.isfile(filename),"打印：os")
                # 导入Gcode文件
            # 这里不需要检测lines类属性，如果后面没有读取到lines，再输出为空
                with open(filename) as f:
                    self.lines = [line.strip() for line in f]
                print(self.lines,"打印：lines")    
            # 按格式输出gcode
            # 读取文件Gcode命令，并按照字母分割为不同的部分
                # gcodeList元素清除
                self.gcodeList.clear()
                # gcodeFault元素清除
                self.gcodeFault.clear()
                # # gcode显示清除
                self.textGcode.clear()
                # # 错误清除
                self.errorGcode.clear()
                # 这里先检测self.lines是否存在
                if self.lines is not None:
                    for line in self.lines:
                        self.textGcode.append(line)
                else:
                    self.errorGcode.clear()
                    self.errorGcode.setText("代码为空")
            else:
                # 查找失败，无法找到文件
                self.errorGcode.clear()
                self.errorGcode.setText("无法找到文件")
        else:
            pass  # 或者执行其他操作

    # 编译Gcode
    # 能用的是最新的textGcode，原来的gcodeList一点用都没了
    def editGcode(self):
        # 由目前的G代码文字生成G代码列表
        self.lines = self.textGcode.toPlainText().splitlines()
        if self.lines:
            # gcodeList元素清除
            self.gcodeList.clear()
            # gcodeFault元素清除
            self.gcodeFault.clear()
            # # gcode显示清除
            self.textGcode.clear()
            # # 错误清除
            self.errorGcode.clear()
            # 在G代码列表中查找需要的值
            test_list = ["G00","G01","G02","G03","G04","G05","G06","G07","G0","G1","G2","G3","G4","G5","G6","G7","G28","G92","M01","M1"]
            for i in range(len(self.lines)):
                line = self.lines[i]
                G = re.findall(r"G[0-9]\d*\.?\d*", line)
                M = re.findall(r"M[0-9]\d*\.?\d*", line)
                X = re.findall(r"X[0-9]\d*\.?\d*|X0\.\d*[1-9]", line)
                Y = re.findall(r"Y[0-9]\d*\.?\d*|Y0\.\d*[1-9]", line)
                E = re.findall(r"E[0-9]\d*\.?\d*|J0\.\d*[1-9]", line)
                I = re.findall(r"I[0-9]\d*\.?\d*|I0\.\d*[1-9]", line)
                J = re.findall(r"J[0-9]\d*\.?\d*|J0\.\d*[1-9]", line)
                # 生成单个语句列表
                result = [G,M,X,Y,E,I,J]
                # 将单个语句列表加入大列表中(通过下面gcodeList这个大列表，可以检查每一行的Gcode是否存在问题)
                self.gcodeList.append(result)
                # Gcode可能存在的几种编译问题
                # 1、G代码指令不存在（G、M代码均缺失、G代码符号不符合、M代码符号不符合、一行中同时出现G、M代码）
                # 2、G代码具体某个指令编写错误（如G02圆弧插补代码末位置与圆心距离和初位置与圆心距离不同）
                # 下面暂且只检查第1类错误
                if (len(G) == 0 and len(M) == 0):
                    self.errorGcode.append("第%d行G、M代码缺失"%(i))
                    self.textGcode.setTextColor(QtGui.QColor(0,0,255,255))
                    self.textGcode.append(line)
                    self.textGcode.setTextColor(QtGui.QColor(0,0,0,255))
                elif(len(G) != 0 and len(M) !=0):
                    self.errorGcode.append("第%d行同时存在G、M代码"%(i))
                    self.textGcode.setTextColor(QtGui.QColor(0,0,255,255))
                    self.textGcode.append(line)
                    self.textGcode.setTextColor(QtGui.QColor(0,0,0,255))
                elif(len(G)!=0 and G[0] not in test_list):
                    self.errorGcode.append("第%d行G代码使用错误"%(i))
                    self.textGcode.setTextColor(QtGui.QColor(0,0,255,255))
                    self.textGcode.append(line)
                    self.textGcode.setTextColor(QtGui.QColor(0,0,0,255))
                elif(len(M)!=0 and M[0] not in test_list):
                    self.errorGcode.append("第%d行M代码使用错误"%(i))
                    self.textGcode.setTextColor(QtGui.QColor(0,0,255,255))
                    self.textGcode.append(line)
                    self.textGcode.setTextColor(QtGui.QColor(0,0,0,255))
                else:
                    self.textGcode.append(line)
        else:
            pass

    # 模拟Gcode
    def simulateGcode(self):
        self.simulation_x.clear()
        self.simulation_y.clear()
        self.simulation_z.clear()
        self.simulationPictureGcode_2D.clear()
        if (len(self.errorGcode.toPlainText())==0):
            self.lines = self.textGcode.toPlainText().splitlines()
            # 通过添加三个一维数组坐标的方式，获得模拟图像
            for i in range(len(self.lines)):
                line = self.lines[i]
                G = re.findall(r"G[0-9]\d*\.?\d*", line)
                M = re.findall(r"M[0-9]\d*\.?\d*", line)
                X = re.findall(r"X[0-9]\d*\.?\d*|X0\.\d*[1-9]", line)
                Y = re.findall(r"Y[0-9]\d*\.?\d*|Y0\.\d*[1-9]", line)
                E = re.findall(r"E[0-9]\d*\.?\d*|J0\.\d*[1-9]", line)
                I = re.findall(r"I[0-9]\d*\.?\d*|I0\.\d*[1-9]", line)
                J = re.findall(r"J[0-9]\d*\.?\d*|J0\.\d*[1-9]", line)
                # 生成单个语句列表
                if (len(G)!=0):
                    if (G[0]=="G00" or G[0]=="G0"):
                        x = round(float(X[0][1:]),3)
                        y = round(float(Y[0][1:]),3)
                        self.simulation_x,self.simulation_y = cal.gcodeG00(x,y,point_x=self.simulation_x,point_y=self.simulation_y)
                    if (G[0]=="G01" or G[0]=="G1"):
                        x = round(float(X[0][1:]),3)
                        y = round(float(Y[0][1:]),3)
                        self.simulation_x,self.simulation_y = cal.gcodeG01(x=x,y=y,stepsize=self.stepsize,point_x=self.simulation_x,point_y=self.simulation_y)
                    if (G[0]=="G02" or G[0]=="G2"):
                        # 1 为顺时针
                        x = round(float(X[0][1:]),3)
                        y = round(float(Y[0][1:]),3)
                        x_i = round(float(I[0][1:]),3)
                        y_j = round(float(J[0][1:]),3)
                        self.simulation_x,self.simulation_y = cal.gcodeG02(point_x=self.simulation_x,point_y=self.simulation_y,xe=x,ye=y,x_c=x_i,y_c=y_j,stepsize=self.stepsize,direction=1)
                    if (G[0]=="G03" or G[0]=="G3"):
                        # 2 为逆时针
                        x = round(float(X[0][1:]),3)
                        y = round(float(Y[0][1:]),3)
                        x_i = round(float(I[0][1:]),3)
                        y_j = round(float(J[0][1:]),3)
                        self.simulation_x,self.simulation_y = cal.gcodeG02(point_x=self.simulation_x,point_y=self.simulation_y,xe=x,ye=y,x_c=x_i,y_c=y_j,stepsize=self.stepsize,direction=2)
                    if (G[0]=="G04" or G[0]=="G4"):
                        pass
                    if (G[0]=="G05" or G[0]=="G5"):
                        pass
                    if (G[0]=="G06" or G[0]=="G6"):
                        pass
                    if (G[0]=="G07" or G[0]=="G7"):
                        pass
                if (len(M)!=0):
                    if (M[0]=="M01" or M[0]=="M1"):
                        pass
                    if (M[0]=="M02" or M[0]=="M2"):
                        pass
            # 打印二维数组
            print(self.simulation_x,self.simulation_y,"这是x、y的值")
            print(len(self.simulation_x),len(self.simulation_y))
            # 画图像
            canvas = plot_point(self.simulation_x,self.simulation_y)
            # 将图像安置在label中
            # hboxlayout = QtWidgets.QHBoxLayout(gcodePictureLabel)
            # hboxlayout.addWidget(canvas)
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(canvas.getvalue())
            self.simulationPictureGcode_2D.setPixmap(pixmap)
            # 打印三维数组
    # 运行Gcode
    def runGcode(self):
        pass
