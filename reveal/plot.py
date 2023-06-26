from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5 import sip


def plot_2D(widget):
    fig = Figure(figsize=(5,4),dpi=100)
    canvas = FigureCanvas(fig)
    if(widget.layout() is None):
    # 如果没有布局，创建一个新的水平布局并将其设置为QWidget的布局
        layout = QVBoxLayout(widget)
    else:
        layout = widget.layout()
    if (layout.count()):
        sip.delete(layout.takeAt(0).widget())
    layout.addWidget(canvas)
    print(layout.count())
    # 绘制图像
    ax = fig.add_subplot(111)
    return ax,canvas,fig
    
def gcode():
    pass