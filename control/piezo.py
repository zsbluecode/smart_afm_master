import ctypes

class Piezo:
    def __init__(self):
        self.piezo = None
        self.handle = None
        self.piezoHandle = None
        self.piezoZvalue = None
        self.piezoXvalue = None
        self.piezoYvalue = None
        self.piezoXstate = None
        self.piezoYstate = None
        self.piezoZstate = None
    
    def connect(self):
        self.piezo = ctypes.windll.LoadLibrary("smart_afm_master/module/Madlib.dll")
        self.handle = self.piezo.MCL_InitHandle()
        self.piezo.MCL_SingleReadN.restype = ctypes.c_double
        self.piezo.MCL_SingleReadZ.restype = ctypes.c_double

    def xMove(self):
        self.piezo.MCL_SingleWriteN(ctypes.c_double(self.piezoXstate),1,self.handle)

    def yMove(self):
        self.piezo.MCL_SingleWriteN(ctypes.c_double(self.piezoYstate),2,self.handle)

    def zMove(self):
        self.piezo.MCL_SingleWriteZ(ctypes.c_double(self.piezoXstate),self.handle)

    def xValue(self):
        self.piezoXvalue = self.piezo.MCL_SingleReadN(1,self.handle)
        yield self.piezoXvalue

    def yVlaue(self):
        self.piezoYvalue = self.piezo.MCL_SingleReadN(2,self.handle)
        yield self.piezoYvalue
    
    def zValue(self):
        self.piezoZvalue = self.piezo.MCL_SingleReadZ(self.handle)
        yield self.piezoZvalue