import numpy as np

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