import ctypes
import time
import matplotlib.pyplot as plt
import numpy as np
import datetime


# def scan(width,height,unit,delaytime,mode):
#     dll = ctypes.windll.LoadLibrary("module/Madlib.dll")
#     handle = dll.MCL_InitHandle()
#     dll.MCL_SingleReadN.restype = ctypes.c_double
#     dll.MCL_SingleReadZ.restype = ctypes.c_double
#     point_x = int(width/unit)
#     point_y = int(height/unit)
#     print(dll.MCL_SingleReadZ(handle))
#     unit = unit/1000
#     scan_data = [[0 for j in range(0,point_y)]for i in range(0,point_x)]
#     count = 0
#     if mode == 1:
#         for i in range(0,point_x):
#             for j in range(0,point_y):
#                 # 平移
#                 count += 1
#                 time.sleep(delaytime)
#                 scan_data[i][j] = dll.MCL_SingleReadZ(handle) # 读取地形
#                 print(dll.MCL_SingleReadZ(handle))
#                 if(i%2==0):
#                     scan_data[i][j] = dll.MCL_SingleReadZ(handle) # 读取地形
#                 else:
#                     scan_data[i][point_y-j-1] = dll.MCL_SingleReadZ(handle)
#                 if (j < point_y - 1 and i%2==0):
#                     dll.MCL_SingleWriteN(ctypes.c_double((j+1)*unit),1,handle) # x轴移动
#                 elif(j < point_y - 1 and i%2==1):
#                     dll.MCL_SingleWriteN(ctypes.c_double((point_y-j-2)*unit),1,handle)
#                 else:
#                     dll.MCL_SingleWriteN(ctypes.c_double((i+1)*unit),2,handle)
#                 print("z运动",dll.MCL_SingleReadZ(handle),"x运动",dll.MCL_SingleReadN(1,handle),"y运动",dll.MCL_SingleReadN(2,handle)
#                         ,"x位置",i,"y位置",j)
#     else :
#         for i in range(0,point_x):
#             for j in range(0,point_y):
#                 # 平移
#                 count += 1
#                 time.sleep(delaytime)
#                 if(i%2==0):
#                     scan_data[i][j] = dll.MCL_SingleReadZ(handle) # 读取地形
#                 else:
#                     scan_data[i][point_y-j-1] = dll.MCL_SingleReadZ(handle)
#                 if (j < point_y-1 and i%2==0):
#                     dll.MCL_SingleWriteN(ctypes.c_double((j+1)*unit),2,handle) # y轴移动
#                 elif(j < point_y-1 and i%2==1):
#                     dll.MCL_SingleWriteN(ctypes.c_double((point_y-j-2)*unit),2,handle)
#                 else:
#                     dll.MCL_SingleWriteN(ctypes.c_double((i+1)*unit),1,handle)
#                 print("z运动",dll.MCL_SingleReadZ(handle),"x运动",dll.MCL_SingleReadN(1,handle),"y运动",dll.MCL_SingleReadN(2,handle)
#                         ,"x位置",i,"y位置",j)
#     # 使用imshow函数绘制数组
#     plt.imshow(scan_data, cmap='gray')
#     # 显示图像
#     plt.show()
#     # 生成当前时间戳
#     now = datetime.datetime.now()
#     date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
#     # 将数组保存到文件中，文件名以时间命名
#     filename = f'my_array_{date_time}.npy'
#     # 将数组保存在文件中
#     np.save(filename, scan_data)



# # 扫描
# scan(1000,1000,100,0.01,2)

# # 加载包含数组数据的 .npy 文件
# loaded_arr = np.load("my_array_2023-03-21_21-08-34.npy")

# # 使用imshow函数绘制数组
# plt.imshow(loaded_arr, cmap='gray')
# # 显示图像
# plt.show()