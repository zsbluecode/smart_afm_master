import control.lockin as lockin
import control.motor as motor
import control.piezo as piezo

class test_lock_in:
    pass

class test_motor:
    pass

class test_piezo:
    def __init__(self):
        self.connect_piezo()
    def connect_piezo():
        piezo_now = piezo()
        piezo_now.connect()
        if (piezo_now.handle == 1):
            pass

a = test_piezo()
a.__init__()
