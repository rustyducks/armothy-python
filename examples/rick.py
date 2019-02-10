import time

WAIT_TIME = 0.2
MAX_DEPOSE_HEIGHT = 100

class Rick:
    def __init__(self, arm):
        self.arm = arm
    
    def catch(self, timeout=2):
        t0 = time.time()
        self.arm.close_valve()
        time.sleep(WAIT_TIME)
        self.arm.start_pump()
        time.sleep(WAIT_TIME)
        while self.arm.pressure > 30:
            time.sleep(WAIT_TIME)
            if time.time() - t0 > timeout:
                self.arm.stop_pump()
                raise Exception("Catch Timeout")

    
    def drop(self, timeout=2):
        t0 = time.time()
        self.arm.open_valve()
        time.sleep(WAIT_TIME)
        self.arm.stop_pump()
        time.sleep(WAIT_TIME)
        while self.arm.pressure < 40:
            time.sleep(WAIT_TIME)
            if time.time() - t0 > timeout:
                raise Exception("Drop Timeout")
        self.arm.close_valve()
        return 0
        
    def translate(self, h, error=5):
        self.arm.translate_z_axis(h)
        time.sleep(0.1)
        while abs(h-self.arm.get_dof(0)) > error:
            time.sleep(0.1)

    def take(self, h0, h1, h3):
        self.translate(h0)
        try:
            catch(self.arm)
        except:
            self.drop()
            return False
        self.translate(h1)
        self.arm.rotate_z_axis(-340)
        time.sleep(0.8)
        self.translate(h3)
        self.drop()
        self.translate(h1)
        self.arm.rotate_z_axis(0)
        
    def take_blind(self, hmax, h1, h3):
        h_pos = self.arm.get_dof(0)
        time.sleep(WAIT_TIME)
        self.arm.close_valve()
        time.sleep(WAIT_TIME)
        self.arm.start_pump()
        time.sleep(WAIT_TIME)
        for h in range(int(h_pos), hmax, 10):
            self.translate(h)
            if self.arm.pressure < 30:
                break
        else:
            self.translate(hmax, 1)
            time.sleep(0.5)
            if self.arm.pressure < 30:
                time.sleep(WAIT_TIME)
            else:
                print("raté ! ")
                self.arm.stop_pump()
                time.sleep(WAIT_TIME)
                self.arm.home()
                raise Exception("Amonbophis")
        print("yes !")
        time.sleep(WAIT_TIME)
        safe_height = max(0,min(h1, self.arm.get_dof(0)-10))
        self.translate(safe_height)
        self.arm.rotate_z_axis(-340)
        time.sleep(0.8)
        self.translate(h3)
        self.drop()
        self.translate(safe_height)
        self.arm.rotate_z_axis(0)
        time.sleep(WAIT_TIME)

    def pile(self, z0):
        z=z0
        while True:
            self.take_blind(155, z, z)
            z-=25
            time.sleep(WAIT_TIME)


