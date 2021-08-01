from firebase import firebase
from datetime import datetime
import pytz
import board
import adafruit_mlx90614
import busio as io
from heartrate_monitor import HeartRateMonitor
from heartrate_monitor import MAX30102Results
import time
import argparse
import PatientCapture
from PatientCapture import Patient
#=======================================================================================
tz = pytz.timezone('Africa/Cairo')
now = datetime.now()
dt_string = now.strftime("%B %d, %Y %H:%M:%S")
print("date and time =", dt_string)

#========================================================================================

PatientName=PatientCapture.Patient()
print('Patient Name:',PatientName)

#=========================================================================================
print('Measuring Body Temprature')
time.sleep(5)
i2c=io.I2C(board.SCL,board.SDA,frequency=100000)
mlx=adafruit_mlx90614.MLX90614(i2c)
BodyTemp=mlx.object_temperature + 6
print('Temp',BodyTemp)
#ambtemp=mlx.ambient_temperature

#=========================================================================================
print('Measuring SPO2 & BPM')
time.sleep(5)
parser = argparse.ArgumentParser(description="Read and print data from MAX30102")
parser.add_argument("-r", "--raw", action="store_true",
                    help="print raw data instead of calculation result")
parser.add_argument("-t", "--time", type=int, default=30,
                    help="duration in seconds to read from sensor, default 30")
args = parser.parse_args()

print('sensor starting...')
hrm = HeartRateMonitor(print_raw=args.raw, print_result=(not args.raw))
hrm.start_sensor()
try:
    time.sleep(args.time)
except KeyboardInterrupt:
    print('keyboard interrupt detected, exiting...')

hrm.stop_sensor()
print('sensor stoped!')
x= MAX30102Results()
print('SPO2',x[0])
print('BPM',x[1])

#=====================================================================
firebasecall = firebase.FirebaseApplication('https://graduation1-7004a-default-rtdb.firebaseio.com/', None)
datenow=str(now.strftime("%B %d, %Y"))
timenow=str(now.strftime("%H:%M:%S"))
bpmadd = '/'+str(PatientName)+'/BPM'+'/'+datenow
spo2add = '/'+str(PatientName)+'/SPO2'+'/'+datenow
tempadd = '/'+str(PatientName)+'/Temp'+'/'+datenow
firebasecall.put(spo2add,timenow, x[0])
firebasecall.put(bpmadd,timenow, x[1])
firebasecall.put(tempadd,timenow, BodyTemp)
