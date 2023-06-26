import matplotlib.pyplot as plt
import numpy as np

class bresenham_circle:
    def __init__(self):
        self.point = []
    def judge_quadrantcv(self,x0,y0,x1,y1,ox,oy):    #将圆心（或椭圆中心）平移到原点后，判断起始点、终点所在象限（圆弧、椭圆类型）
        x_0=x0-ox;y_0=y0-oy;x_1=x1-ox;y_1=y1-oy    #坐标变换
        if(x_0 > 0) and (y_0 >= 0):  # 第一象限
            if (x_1 > 0) and (y_1 >= 0):
                quadrant1=1
                quadrant2=1
            elif (x_1 <= 0) and (y_1 > 0):
                quadrant1=1
                quadrant2=2
            elif (x_1 < 0) and (y_1 <= 0):
                quadrant1=1
                quadrant2=3
            elif(x_1 >= 0) and (y_1 < 0):
                quadrant1=1
                quadrant2=4        
        elif(x_0 <= 0) and (y_0 > 0):  # 第二象限
            if (x_1 > 0) and (y_1 >= 0):
                quadrant1=2
                quadrant2=1
            elif (x_1 <= 0) and (y_1 > 0):
                quadrant1=2
                quadrant2=2
            elif (x_1 < 0) and (y_1 <= 0):
                quadrant1=2
                quadrant2=3
            elif(x_1 >= 0) and (y_1 < 0):
                quadrant1=2
                quadrant2=4
        elif(x_0 < 0) and (y_0 <= 0):  # 第三象限
            if (x_1 > 0) and (y_1 >= 0):
                quadrant1=3
                quadrant2=1
            elif (x_1 <= 0) and (y_1 > 0):
                quadrant1=3
                quadrant2=2
            elif (x_1 < 0) and (y_1 <= 0):
                quadrant1=3
                quadrant2=3
            elif(x_1 >= 0) and (y_1 < 0):
                quadrant1=3
                quadrant2=4
        elif(x_0 >= 0) and (y_0 < 0):  # 第四象限
            if (x_1 > 0) and (y_1 >= 0):
                quadrant1=4
                quadrant2=1
            elif (x_1 <= 0) and (y_1 > 0):
                quadrant1=4
                quadrant2=2
            elif (x_1 < 0) and (y_1 <= 0):
                quadrant1=4
                quadrant2=3
            elif(x_1 >= 0) and (y_1 < 0):
                quadrant1=4
                quadrant2=4
        return quadrant1,quadrant2
        fm = 0;x2 = abs(x1 - x0);y2 = abs(y1 - y0);total = x2 + y2;count = 0
        while count < total:
            if quadrant < 5:
                if fm >= 0:
                    if quadrant == 1 or quadrant == 4:
                        x0 += 1
                    elif quadrant == 2 or quadrant == 3:
                        x0 -= 1
                    fm = fm - y2
                elif fm <0:
                    if quadrant == 1 or quadrant == 2:
                        y0 += 1
                    elif quadrant == 3 or quadrant == 4:
                        y0 -= 1
                    fm = fm + x2
            else:
                if quadrant == 5:
                    x0 += 1
                elif quadrant == 6:
                    x0 -=1
                elif quadrant == 7:
                    y0 += 1
                elif quadrant == 8:
                    y0 -=1
            p = (2*x0,2*y0) #此处为了便于观察插补过程，坐标扩大了2倍，读者可自行修调，下同，不再赘述！
            self.point.append(p)
            count += 1
    def quadrantcv_1(self,direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,stepsize):   #获取由第一象限插补点组成的数组（圆弧、椭圆类型）
        while totalsteps >= 0:
            if direction == 2:   #2 逆时针圆（椭圆）
                if fm >= 0:
                    if mode==1:   
                        fm=fm-2*(x0)+1
                        x0-=1
                    elif mode==2:
                        x0-=1
                        fm=((x0-j1x)**2+(y0-j1y)**2)**0.5+((x0-j2x)**2+(y0-j2y)**2)**0.5-l   
                else:
                    if mode==1:
                        fm=fm +2*(y0)+1
                        y0+=1
                    elif mode==2:
                        y0+=1
                        fm=((x0-j1x)**2+(y0-j1y)**2)**0.5+((x0-j2x)**2+(y0-j2y)**2)**0.5-l
                        
            else:   #1 顺时针圆（椭圆）
                if fm >= 0:
                    if mode==1:
                        fm = fm -2*(y0) +1
                        y0 -= 1
                    elif mode==2:
                        y0 -= 1
                        fm=((x0-j1x)**2+(y0-j1y)**2)**0.5+((x0-j2x)**2+(y0-j2y)**2)**0.5-l  
                else:
                    if mode==1:
                        fm = fm +2*(x0) +1
                        x0 += 1
                    elif mode==2:
                        x0 += 1
                        fm=((x0-j1x)**2+(y0-j1y)**2)**0.5+((x0-j2x)**2+(y0-j2y)**2)**0.5-l 
            self.point.append((stepsize*x0+stepsize*ox, stepsize*y0+stepsize*oy))
            totalsteps=totalsteps-1
            if (x0<0) or (y0<0):    #超出第一象限，则第一象限函数终止，转至下一象限，下同，不再赘述！
                break
        return x0,y0,totalsteps,fm
    def quadrantcv_2(self,direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,stepsize):   #获取由第二象限插补点组成的数组（圆弧、椭圆类型）
        fm=((x0-j1x)**2+(y0-j1y)**2)**0.5+((x0-j2x)**2+(y0-j2y)**2)**0.5-l
        while totalsteps >= 0:
            if direction == 2:   #2 逆时针圆（椭圆）
                if fm >= 0:
                    if mode==1:
                        fm = fm -2*(y0) +1
                        y0 -= 1
                    elif mode==2:
                        y0 -= 1
                        fm=((x0-j1x)**2+(y0-j1y)**2)**0.5+((x0-j2x)**2+(y0-j2y)**2)**0.5-l
                else:
                    if mode==1:
                        fm = fm -2*(x0) +1
                        x0 -= 1
                    elif mode==2:
                        x0-=1
                        fm=((x0-j1x)**2+(y0-j1y)**2)**0.5+((x0-j2x)**2+(y0-j2y)**2)**0.5-l
            else:   #1 顺时针圆（椭圆）
                if fm >= 0:
                    if mode==1:
                        fm = fm +2*(x0) +1
                        x0 += 1
                    elif mode==2:
                        x0+=1
                        fm=((x0-j1x)**2+(y0-j1y)**2)**0.5+((x0-j2x)**2+(y0-j2y)**2)**0.5-l
                else:
                    if mode==1:
                        fm = fm +2*(y0) +1
                        y0 += 1
                    elif mode==2:
                        y0+=1
                        fm=((x0-j1x)**2+(y0-j1y)**2)**0.5+((x0-j2x)**2+(y0-j2y)**2)**0.5-l
            self.point.append((stepsize*x0+stepsize*ox, stepsize*y0+stepsize*oy))
            totalsteps=totalsteps-1
            if (x0>0) or(y0<0):
                break
        return x0,y0,totalsteps,fm
    def quadrantcv_3(self,direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,stepsize):   #获取由第三象限插补点组成的数组（圆弧、椭圆类型）
        fm=((x0-j1x)**2+(y0-j1y)**2)**0.5+((x0-j2x)**2+(y0-j2y)**2)**0.5-l
        while totalsteps >= 0:
            if direction == 2:   #2 逆时针圆
                if fm >= 0:
                    if mode==1:
                        fm = fm +2*(x0) +1
                        x0 += 1
                    elif mode==2:
                        x0+=1
                        fm=((x0-j1x)**2+(y0-j1y)**2)**0.5+((x0-j2x)**2+(y0-j2y)**2)**0.5-l
                else:
                    if mode==1:
                        fm = fm -2*(y0) +1
                        y0 -= 1
                    elif mode==2:
                        y0-=1
                        fm=((x0-j1x)**2+(y0-j1y)**2)**0.5+((x0-j2x)**2+(y0-j2y)**2)**0.5-l
            else:   #1 顺时针圆
                if fm >= 0:
                    if mode==1:
                        fm = fm +2*(y0) +1
                        y0 += 1
                    elif mode==2:
                        y0+=1
                        fm=((x0-j1x)**2+(y0-j1y)**2)**0.5+((x0-j2x)**2+(y0-j2y)**2)**0.5-l
                else:
                    if mode==1:
                        fm = fm -2*(x0) +1
                        x0 -= 1
                    elif mode==2:
                        x0-=1
                        fm=((x0-j1x)**2+(y0-j1y)**2)**0.5+((x0-j2x)**2+(y0-j2y)**2)**0.5-l
            self.point.append((stepsize*x0+stepsize*ox, stepsize*y0+stepsize*oy))
            totalsteps=totalsteps-1
            if (x0>0) or (y0>0):
                break
        return x0,y0,totalsteps,fm
    def quadrantcv_4(self,direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,stepsize):   #获取由第四象限插补点组成的数组（圆弧、椭圆类型）
        fm = 0
        while totalsteps >= 0:
            if direction == 2:   #2 逆时针圆
                if fm >= 0:
                    if mode==1:
                        fm = fm +2*(y0) +1
                        y0 += 1
                else:
                    if mode==1:
                        fm = fm +2*(x0) +1
                        x0 += 1
                    elif mode==2:
                        x0+=1
                        fm=((x0-j1x)**2+(y0-j1y)**2)**0.5+((x0-j2x)**2+(y0-j2y)**2)**0.5-l
            else:   #1 顺时针圆
                if fm >= 0:
                    if mode==1:
                        fm = fm -2*(x0) +1
                        x0 -= 1
                    elif mode==2:
                        x0-=1
                        fm=((x0-j1x)**2+(y0-j1y)**2)**0.5+((x0-j2x)**2+(y0-j2y)**2)**0.5-l
                else:
                    if mode==1:
                        fm = fm -2*(y0) +1
                        y0 -= 1
                    elif mode==2:
                        y0-=1
                        fm=((x0-j1x)**2+(y0-j1y)**2)**0.5+((x0-j2x)**2+(y0-j2y)**2)**0.5-l
            self.point.append((stepsize*x0+stepsize*ox, stepsize*y0+stepsize*oy))
            totalsteps=totalsteps-1
            if (x0<0) or (y0>0):
                break
        return x0,y0,totalsteps,fm
    def quadrant_all(self,direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize): #将以上获取四个象限插补点数组的函数合为一个，方便后面简化程序。（圆弧、椭圆类型）
        if i==1:
            x0,y0,totalsteps,fm=self.quadrantcv_1(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,stepsize)
        elif i==2:
            x0,y0,totalsteps,fm=self.quadrantcv_2(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,stepsize)
        elif i==3:
            x0,y0,totalsteps,fm=self.quadrantcv_3(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,stepsize)
        elif i==4:
            x0,y0,totalsteps,fm=self.quadrantcv_4(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,stepsize)
        return x0,y0,totalsteps,fm
    def interpolationcv(self,direction,l,quadrant1,quadrant2,x0,y0,x1,y1,ox,oy,j1x,j1y,j2x,j2y,mode,stepsize):    #获取由插补点组成的数组（圆弧、椭圆类型）
        r=int(((x0-ox)**2+(y0-oy)**2)**0.5)
        a=(((x0-j1x)**2+(y0-j1y)**2)**0.5+((x0-j2x)**2+(y0-j2y)**2)**0.5)/2    #椭圆长半轴
        b=(a**2-(abs(j2x-ox))**2)**0.5  #椭圆短半轴
        self.point.append((2*x0,2*y0))   #此处系数2是为了与上述步骤中坐标放大倍数保持一致。
        x0=x0-ox;y0=y0-oy;x1=x1-ox;y1=y1-oy;j1x=j1x-ox;j1y=j1y-oy;j2x=j2x-ox;j2y=j2y-oy;fm=0#坐标变换
        if (quadrant1==1) and (quadrant2==1):
            if direction==1:#顺时针圆弧
                totalsteps=abs(x0-x1)+abs(y0-y1)#总步数totalsteps计算公式，为作者通过分类讨论得出（圆弧：顺时针16类，逆时针16类。椭圆：顺时针16类，逆时针16类。）以下63类不再赘述。
                for i in [1,4,3,2,1]:#列表中数字，为从起始点顺时针走到终点所需经过的象限顺序，以下31类不再赘述。
                    if totalsteps!=0:
                        x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
                    else:
                        break          
            else:   #逆时针圆弧
                if mode==1:
                    totalsteps=8*r-(abs(x0-x1)+abs(y0-y1))
                elif mode==2:
                    totalsteps=4*a+4*b-(abs(x0-x1)+abs(y0-y1))
                for i in [1,2,3,4,1]:
                    if totalsteps!=0:
                        x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
                    else:
                        break
        elif (quadrant1==1) and (quadrant2==2):
            if direction==1:    #顺时针圆弧
                if mode==1:
                    totalsteps=6*r-x0+x1+y0+y1
                elif mode==2:
                    totalsteps=4*a+2*b-x0+x1+y0+y1
                for i in [1,4,3,2]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
            else:   #逆时针圆弧
                if mode==1:
                    totalsteps=8*r-(6*r-x0+x1+y0+y1)
                elif mode==2:
                    totalsteps=4*a+4*b-(4*a+2*b-x0+x1+y0+y1)
                for i in [1,2]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
        elif (quadrant1==1) and (quadrant2==3):
            if direction==1:    #顺时针圆弧
                if mode==1:
                    totalsteps=4*r-x0-x1+y0+y1
                elif mode==2:
                    totalsteps=2*a+2*b-x0-x1+y0+y1
                for i in [1,4,3]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
            else:   #逆时针圆弧
                if mode==1:
                    totalsteps=8*r-(4*r-x0-x1+y0+y1)
                elif mode==2:
                    totalsteps=4*a+4*b-(2*a+2*b-x0-x1+y0+y1)
                for i in [1,2,3]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
        elif (quadrant1==1) and (quadrant2==4):
            if direction==1:    #顺时针圆弧
                if mode==1:
                    totalsteps=2*r-x0-x1+y0-y1
                elif mode==2:
                    totalsteps=2*a-x0-x1+y0-y1
                for i in [1,4]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
            else:   #逆时针圆弧
                if mode==1:
                    totalsteps=8*r-(2*r-x0-x1+y0-y1)
                elif mode==2:
                    totalsteps=4*a+4*b-(2*a-x0-x1+y0-y1)
                for i in [1,2,3,4]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
        elif (quadrant1==2) and (quadrant2==1):
            if direction==1:    #顺时针圆弧
                if mode==1:
                    totalsteps=2*r-x0+x1-y0-y1
                elif mode==2:
                    totalsteps=2*b-x0+x1-y0-y1
                for i in [2,1]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
            else:   #逆时针圆弧
                if mode==1:
                    totalsteps=8*r-(2*r-x0+x1-y0-y1)
                elif mode==2:
                    totalsteps=4*a+4*b-(2*b-x0+x1-y0-y1)
                for i in [2,3,4,1]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
        elif (quadrant1==2) and (quadrant2==2):
            if direction==1:    #顺时针圆弧
                totalsteps=abs(x0-x1)+abs(y0-y1)
                for i in [2,1,4,3,2]:
                    if totalsteps!=0:
                        x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
                    else:
                        break
            else:   #逆时针圆弧
                if mode==1:
                    totalsteps=8*r-(abs(x0-x1)+abs(y0-y1))
                elif mode==2:
                    totalsteps=4*a+4*b-(abs(x0-x1)+abs(y0-y1))
                for i in [2,3,4,1,2]:
                    if totalsteps!=0:
                        x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
                    else:
                        break
        elif (quadrant1==2) and (quadrant2==3):
            if direction==1:    #顺时针圆弧
                if mode==1:
                    totalsteps=6*r-x0-x1-y0+y1
                elif mode==2:
                    totalsteps=2*a+4*b-x0-x1-y0+y1
                for i in [2,1,4,3]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
            else:   #逆时针圆弧
                if mode==1:
                    totalsteps=8*r-(6*r-x0-x1-y0+y1)
                elif mode==2:
                    totalsteps=4*a+4*b-(2*a+4*b-x0-x1-y0+y1)
                for i in [2,3]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
        elif (quadrant1==2) and (quadrant2==4):
            if direction==1:    #顺时针圆弧
                if mode==1:
                    totalsteps=4*r-x0-x1-y0-y1
                elif mode==2:
                    totalsteps=2*a+2*b-x0-x1-y0-y1
                for i in [2,1,4]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
            else:   #逆时针圆弧
                if mode==1:
                    totalsteps=8*r-(4*r-x0-x1-y0-y1)
                elif mode==2:
                    totalsteps=4*a+4*b-(2*a+2*b-x0-x1-y0-y1)
                for i in [2,3,4]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
        elif (quadrant1==3) and (quadrant2==1):
            if direction==1:    #顺时针圆弧
                if mode==1:
                    totalsteps=4*r+x0+x1-y0-y1
                elif mode==2:
                    totalsteps=2*a+2*b+x0+x1-y0-y1
                for i in [3,2,1]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
            else:   #逆时针圆弧
                if mode==1:
                    totalsteps=8*r-(4*r+x0+x1-y0-y1)
                elif mode==2:
                    totalsteps=4*a+4*b-(2*a+2*b+x0+x1-y0-y1)
                for i in [3,4,1]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
        elif (quadrant1==3) and (quadrant2==2):
            if direction==1:    #顺时针圆弧
                if mode==1:
                    totalsteps=2*r+x0+x1-y0+y1
                elif mode==2:
                    totalsteps=2*a+x0+x1-y0+y1
                for i in [3,2]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
            else:   #逆时针圆弧
                if mode==1:
                    totalsteps=8*r-(2*r+x0+x1-y0+y1)
                elif mode==2:
                    totalsteps=4*a+4*b-(2*a+x0+x1-y0+y1)
                for i in [3,4,1,2]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
        elif (quadrant1==3) and (quadrant2==3):
            if direction==1:    #顺时针圆弧
                totalsteps=abs(x0-x1)+abs(y0-y1)
                for i in [3,2,1,4,3]:
                    if totalsteps!=0:
                        x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
                    else:
                        break           
            else:   #逆时针圆弧
                if mode==1:
                    totalsteps=8*r-(abs(x0-x1)+abs(y0-y1))
                elif mode==2:
                    totalsteps=4*a+4*b-(abs(x0-x1)+abs(y0-y1))
                for i in [3,4,1,2,3]:
                    if totalsteps!=0:
                        x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
                    else:
                        break            
        elif (quadrant1==3) and (quadrant2==4):
            if direction==1:    #顺时针圆弧
                if mode==1:
                    totalsteps=6*r+x0-x1-y0-y1
                elif mode==2:
                    totalstsps=4*a+2*b+x0-x1-y0-y1
                for i in [3,2,1,4]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
            else:   #逆时针圆弧
                if mode==1:
                    totalsteps=8*r-(6*r+x0-x1-y0-y1)
                elif mode==2:
                    totalsteps=4*a+4*b-(4*a+2*b+x0-x1-y0-y1)
                for i in [3,4]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
        elif (quadrant1==4) and (quadrant2==1):
            if direction==1:    #顺时针圆弧
                if mode==1:
                    totalsteps=2*r-x0-x1-y0+y1
                elif mode==2:
                    totalsteps=2*a-x0-x1-y0+y1
                for i in [4,3,2,1]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
            else:   #逆时针圆弧
                if mode==1:
                    totalsteps=8*r-(2*r-x0-x1-y0+y1)
                elif mode==2:
                    totalsteps=4*a+4*b-(2*a-x0-x1-y0+y1)
                for i in [4,1]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
        elif (quadrant1==4) and (quadrant2==2):
            if direction==1:    #顺时针圆弧
                if mode==1:
                    totalsteps=4*r+x0+x1+y0+y1
                elif mode==2:
                    totalsteps=2*a+2*b+x0+x1+y0+y1
                for i in [4,3,2]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
            else:   #逆时针圆弧
                if mode==1:
                    totalsteps=8*r-(4*r+x0+x1+y0+y1)
                elif mode==2:
                    totalsteps=4*a+4*b-(2*a+2*b+x0+x1+y0+y1)
                for i in [4,1,2]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
        elif (quadrant1==4) and (quadrant2==3):
            if direction==1:    #顺时针圆弧
                if mode==1:
                    totalsteps=2*r+x0-x1+y0+y1
                elif mode==2:
                    totalsteps=2*a+x0-x1+y0+y1
                for i in [4,3]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
            else:   #逆时针圆弧
                if mode==1:
                    totalsteps=8*r-(2*r+x0-x1+y0+y1)
                elif mode==2:
                    totalsteps=4*a+4*b-(2*a+x0-x1+y0+y1)
                for i in [4,1,2,3]:
                    x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
        elif (quadrant1==4) and (quadrant2==4):
            if direction==1:    #顺时针圆弧
                totalsteps=abs(x0-x1)+abs(y0-y1)
                for i in [4,3,2,1,4]:
                    if totalsteps!=0:
                        x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
                    else:
                        break               
            else:   #逆时针圆弧
                if mode==1:
                    totalsteps=8*r-(abs(x0-x1)+abs(y0-y1))
                elif mode==2:
                    totalsteps=4*a+4*b-(abs(x0-x1)+abs(y0-y1))
                for i in [4,1,2,3,4]:
                    if totalsteps!=0:
                        x0,y0,totalsteps,fm=self.quadrant_all(direction,totalsteps,l,fm,x0,y0,ox,oy,j1x,j1y,j2x,j2y,mode,i,stepsize)
                    else:
                        break
    def get_pointsc(self,x0,y0,x1,y1,ox,oy,stepsize,direction):  #从输入端获取起始点、终点、圆心的函数（圆弧类型）
        if (round((x0-ox)**2+(y0-oy)**2,5)!=round((x1-ox)**2+(y1-oy)**2,5)):    #判断起点、终点到圆心坐标是否相等，考虑到二进制存储存在的误差，使用round函数截取5位小数进行比较。
            return self.point
        else:
            quadrant1,quadrant2=self.judge_quadrantcv(x0,y0,x1,y1,ox,oy)
            l=0;j1x=0;j1y=0;j2x=0;j2y=0;mode=1
            self.interpolationcv(direction,l,quadrant1,quadrant2,x0,y0,x1,y1,ox,oy,j1x,j1y,j2x,j2y,mode,stepsize) #将插补函数mode设为1，即选择圆弧插补类型,因为圆没有焦点和弦长，故令l=0,j1x=0,j1y=0,j2x=0,j2y=0。
            return self.point    
    def get_pointsv(self,j1x,j1y,j2x,j2y,x0,y0,x1,y1,stepsize,direction):  #从输入端获取焦点、弦长的函数（椭圆类型）
        if (j1y!=j2y):
            return self.point
        elif (round((((x0-j1x)**2+(y0-j1y)**2)**0.5+((x0-j2x)**2+(y0-j2y)**2)**0.5),5)!=round((((x0-j1x)**2+(y0-j1y)**2)**0.5+((x0-j2x)**2+(y0-j2y)**2)**0.5),5)):#判断起点、终点到两焦点距离之和是否相等,处理同上。
            return self.point
        else:
            ox=(j1x+j2x)/2;oy=(j1y+j2y)/2    #椭圆中心横、纵坐标
            l=((x0-j1x)**2+(y0-j1y)**2)**0.5+((x0-j2x)**2+(y0-j2y)**2)**0.5
            quadrant1,quadrant2=self.judge_quadrantcv(x0,y0,x1,y1,ox,oy)
            mode=2    #将插补函数mode设为2，即选择椭圆插补类型。
            self.interpolationcv(direction,l,quadrant1,quadrant2,x0,y0,x1,y1,ox,oy,j1x,j1y,j2x,j2y,mode)
            return self.point
    def circle(self,x0,y0,x1,y1,ox,oy,stepsize,direction):   #画圆弧
        print(stepsize)
        if (stepsize<1):
            m = int(1/stepsize)
            s_m = self.get_pointsc(x0,y0,m*x1,m*y1,m*ox,m*oy,1,direction)
            s = [(x/m,y/m) for x,y in s_m]
        else:
            s = self.get_pointsc(x0,y0,x1,y1,ox,oy,stepsize,direction)
        return s
    def oval(self,j1x,j1y,j2x,j2y,x0,y0,x1,y1,stepsize,direction): #画椭圆
        v = self.get_pointsv(j1x,j1y,j2x,j2y,x0,y0,x1,y1,stepsize,direction)
        return v
   

class Gcode(object):
    # 目的：输入一个gcode文件，运行gcode文件
    # 输入方式有两种：加载gcode文件和手动输入gcode代码，若手动输入gcode代码，那么需要将其格式化
    # 初始化
    def __init__(self,output_digits=6,output_matrix = None):
        self.output_digits = output_digits # 输出有效数字保留6位
        self.output_matrix = output_matrix # 输出的矩阵
    # 格式化gcode代码
    def _format_args(self, x=None, y=None, z=None, i=None, j=None, k=None, **kwargs):
        d = self.output_digits
        args = []
        if x is not None:
            args.append('{0}{1:.{digits}f}'.format(self.x_axis, x, digits=d))
        if y is not None:
            args.append('{0}{1:.{digits}f}'.format(self.y_axis, y, digits=d))
        if z is not None:
            args.append('{0}{1:.{digits}f}'.format(self.z_axis, z, digits=d))
        if i is not None:
            args.append('{0}{1:.{digits}f}'.format(self.i_axis, i, digits=d))
        if j is not None:
            args.append('{0}{1:.{digits}f}'.format(self.j_axis, j, digits=d))
        if k is not None:
            args.append('{0}{1:.{digits}f}'.format(self.k_axis, k, digits=d))
        args += ['{0}{1:.{digits}f}'.format(k, kwargs[k], digits=d) for k in sorted(kwargs)]
        args = ' '.join(args)
        return args
    
    # gcode命令部分
    # 返回当前位置
    @property
    def current_position(self):
        pass
        # 直接通过位移台获得
    
    # 快速定位
    def gcodeG00(self,x,y,point_x=[],point_y=[]):
        point_x.append(x)
        point_y.append(y)
        return point_x,point_y

    # 直线插补，模拟返回数组，打印只需要执行
    def gcodeG01(self,point_x,point_y,x,y,stepsize):
    # stepsize:最小步长
    # point_x,point_y是当前数组
    # x,y为下一步的目标位置

    # 确定当前位置x0，y0
        # x0 = moveFunction.getXPosition(mode)
        # y0 = moveFunction.getYPosition(mode)
        # 从（0，0）或者当前位置开始移动
        x_last = x
        y_last = y
        if len(point_x) == 0 :
            x0 = 0
            y0 = 0
            point_x.append(x0)
            point_y.append(y0)
        else:
            x0 = point_x[-1]
            y0 = point_y[-1]
        # 若没有长度，则不移动
        if (x0 == x) and (y0 == y):
            pass
        dx = abs(x - x0)
        dy = abs(y - y0)
        # 根据直线的走势方向，设置变化的单位是正是负
        s1 = 1 if ((x - x0) > 0) else -1
        s2 = 1 if ((y - y0) > 0) else -1
        # 根据斜率的大小，交换dx和dy，可以理解为变化x轴和y轴使得斜率的绝对值为[0,1]
        boolInterChange = False
        if dy > dx:
            # np.swapaxes(dx, dy)
            dx,dy = dy,dx
            boolInterChange = True
        # 初始误差
        e = 2 * dy - dx
        x = x0
        y = y0
        stepsize = 0.01
        for i in range(0, int((dx)/stepsize)):
            point_x.append(x)
            point_y.append(y)
            if e >= 0:
                # 此时要选择横纵坐标都不同的点，根据斜率的不同，让变化小的一边变化一个单位
                if boolInterChange:
                    x += s1*stepsize
                else:
                    y += s2*stepsize
                e -= 2 * dx
            # 根据斜率的不同，让变化大的方向改变一单位，保证两边的变化小于等于1单位，让直线更加均匀
            if boolInterChange:
                y += s2*stepsize
            else:
                x += s1*stepsize
            e += 2 * dy
        point_x.append(x_last)
        point_y.append(y_last)
        return point_x,point_y

    def gcodeG02(self,point_x,point_y,xe,ye,x_c,y_c,stepsize,direction):
        if len(point_x) == 0 :
            x0 = 0
            y0 = 0
            point_x.append(x0)
            point_y.append(y0)
        else:
            x0 = point_x[-1]
            y0 = point_y[-1]
        print(x0,y0,"这是x0y0")
        s_circle = bresenham_circle()
        s = s_circle.circle(0,0,xe-x0,ye-y0,x_c-x0,y_c-y0,stepsize,direction)
        x = [x + x0 for x,y in s]
        y = [y + y0 for x,y in s]
        point_x = point_x + x
        point_y = point_y + y
        point_x.append(xe)
        point_y.append(ye)
        return point_x,point_y

# a = Gcode()
# x_list,y_list = a.gcodeG02([2],[2],6,6,4,4,0.001,1) 
# # 创建图形对象和子图对象
# fig, ax = plt.subplots()

# # 绘制数据点
# ax.plot(x_list, y_list)

# # 设置 x 和 y 轴范围
# ax.axis('equal')  # 设置 x 和 y 轴的单位比例相同
# plt.show()

# a = bresenham_circle()
# s = a.circle(0,0,-6,-6,-3,-3,0.001,1)

# x_list = [x for x, y in s]
# y_list = [y for x, y in s]
# # 创建图形对象和子图对象
# fig, ax = plt.subplots()

# # 绘制数据点
# ax.plot(x_list, y_list)

# # 设置 x 和 y 轴范围
# ax.axis('equal')  # 设置 x 和 y 轴的单位比例相同
# plt.show()