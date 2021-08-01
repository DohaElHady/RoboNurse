from max30102 import MAX30102
import hrcalc
import threading
import time
import numpy as np
from collections import Counter
Fbpm=[]
Fspo2=[]

class HeartRateMonitor(object):
    """
    A class that encapsulates the max30102 device into a thread
    """

    LOOP_TIME = 0.01

    def __init__(self, print_raw=False, print_result=False):
        self.bpm = 0
        if print_raw is True:
            print('IR, Red')
        self.print_raw = print_raw
        self.print_result = print_result

    def run_sensor(self):
        sensor = MAX30102()
        ir_data = []
        red_data = []
        bpms = []

        # run until told to stop
        while not self._thread.stopped:
            # check if any data is available
            num_bytes = sensor.get_data_present()
            if num_bytes > 0:
                # grab all the data and stash it into arrays
                while num_bytes > 0:
                    red, ir = sensor.read_fifo()
                    num_bytes -= 1
                    ir_data.append(ir)
                    red_data.append(red)
                    if self.print_raw:
                        print("{0}, {1}".format(ir, red))

                while len(ir_data) > 100:
                    ir_data.pop(0)
                    red_data.pop(0)

                if len(ir_data) == 100:
                    bpm, valid_bpm, spo2, valid_spo2 = hrcalc.calc_hr_and_spo2(ir_data, red_data)
                    if valid_bpm:
                        bpms.append(bpm)
                        while len(bpms) > 4:
                            bpms.pop(0)
                        self.bpm = np.mean(bpms)
                        if (np.mean(ir_data) < 50000 and np.mean(red_data) < 50000):
                            self.bpm = 0
                            if self.print_result:
                                print("Finger not detected")
                        if self.print_result:
                            #print("BPM: {0}, SpO2: {1}".format(self.bpm, spo2))
                            bmp11=self.bpm
                            #print ('test1')
                            if int(bmp11) in range(60,110):
                                #print ('test2')
                                if int(spo2) in range(95,100):
                                    #print ('test3')
                                    Fbpm.append(int(bmp11))
                                    Fspo2.append(int(spo2))
                                    

            time.sleep(self.LOOP_TIME)

        sensor.shutdown()

    def start_sensor(self):
        self._thread = threading.Thread(target=self.run_sensor)
        self._thread.stopped = False
        self._thread.start()

    def stop_sensor(self, timeout=2.0):
        self._thread.stopped = True
        self.bpm = 0
        self._thread.join(timeout)
        
def MAX30102Results():
    s = Counter(Fspo2)
    b = Counter(Fbpm)
    SPO2Read=s.most_common(1)[0][0]
    BPMRead= b.most_common(1)[0][0]
    return [SPO2Read,BPMRead]
