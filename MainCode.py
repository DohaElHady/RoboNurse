#==============================Libraries================================== 
from tkinter import *
from PIL import ImageTk,Image
from tkinter import messagebox
from threading import *
from firebase import firebase
from datetime import datetime
import pytz
import board
import adafruit_mlx90614
import busio as io
from heartrate_monitor import HeartRateMonitor
from heartrate_monitor import MAX30102Results
import time
import serial
import argparse
import PatientCapture
from PatientCapture import Patient
import pygame
import speech_recognition as sr
import yagmail
#=======================================================================
tz = pytz.timezone('Africa/Cairo')
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.flush()
firebasecall = firebase.FirebaseApplication('https://firebaseaddress.firebaseio.com/', None)
visitadd= '/patients/UI/schedule/time'
visittime1=firebasecall.get(visitadd,None)
visittime=str(visittime1).split(":",2) #[hr,min]
print(visittime)
pygame.mixer.init()
#intiations for speech recognation
word1 = 'hello'
word2 ='who'
word3='rules'
emailreceiver = "dremail@gmail.com" 
emailbody = "Patient Temprature is higher than normal"
yag = yagmail.SMTP("robonurse6@gmail.com")
#=======================================================================
#======================Main Functions======================================
def search(list, keyword):
 for i in range(len(list)):
   if list[i] == keyword:
     return True
  else:
     return False

def listen(): 
 # obtain audio from the microphone
 r = sr.Recognizer()
 with sr.Microphone() as source:
   print("Say something!")
   audio = r.listen(source)
 # recognize speech using Google Speech Recognition
 try:
   # for testing purposes, we're just using the default API key
   print(r.recognize_google(audio))
   streaming = str(r.recognize_google(audio)).split()
   if search(streaming, word1):
     pygame.mixer.music.load("hellorec.mpeg")
     playrec()
   elif search(streaming, word2):
     pygame.mixer.music.load("Ronainforec.mpeg")
     playrec()
   elif search(streaming, word3):
     pygame.mixer.music.load("Rulesrec.mpeg")
     playrec()
   else:
    print("Not Recognized, Please Repeat")
 except sr.UnknownValueError:
  print("Google Speech Recognition could not understand audio")
 except sr.RequestError as e:
  print("Could not request results from Google Speech Recognition service; {0}".format(e))
  
def playrec():
 pygame.mixer.music.play()
 while pygame.mixer.music.get_busy() == True:
 continue

def detecttime():
 now = datetime.now()
 dt_string = str(now.strftime("%H:%M:%S")).split(":",2)
 if dt_string[0]==visittime[0] and dt_string[1]==visittime[1]:
   visitlabel.config(text='It Is Time To Visit, I am going to room 2')
   visitlabel.place(x=20,y=300)
   return True
 else:
   left="Time Left To The Next Visit: "+str(int(visittime[0])-int(dt_string[0]))+" Hours "+str(int(visittime[1])-int(dt_string[1]))+" Minuits"
   visitlabel.config(text=left)
   return False

def visit():
 ### Arduino Pi Communication ###
 ser.write("M".encode('utf-8'))
 while not ser.in_waiting>0:
   x=1
   visitlabel.config(text='I Reached the Room')
   visitlabel.place(x=150,y=300)
   time.sleep(5)

def visitback():
 ### Arduino Pi Communication ###
 ser.write("P".encode('utf-8'))
 while not ser.in_waiting>0:
  x=1
 
def arm():
 ### Arduino Pi Communication ###
 ser.write("A".encode('utf-8'))
 while not ser.in_waiting>0:
  x=1

def pahrmago():
 ### Arduino Pi Communication ###
 ser.write("S".encode('utf-8'))
 while not ser.in_waiting>0:
  x=1
 
def pahrmaback():
 ### Arduino Pi Communication ###
 ser.write("B".encode('utf-8'))
 while not ser.in_waiting>0:
  x=1

def emergancymail():
 yag.send(
 to=emailreceiver,
 subject="Hospital Emergancy Email From RONA",
 contents=emailbody )
 
def med():
 visitlabel.config(text='Looking For The Patient')
 visitlabel.place(x=20,y=300)
 print('Looking for patient ...')
 PatientName=PatientCapture.Patient()
 print('Patient Name:',PatientName)
 visitlabel.config(text='Hello '+PatientName+'. It is time for Check Up.')
 visitlabel.place(x=20,y=300)
 pygame.mixer.music.load("rec1.mpeg")
 playrec()
 time.sleep(5)
 pygame.mixer.music.load("rec2.mpeg")
 playrec()
 visitlabel.config(text='Please Put Your Hand at the Box as Shown')
 visitlabel.place(x=20,y=200)
 medl.place(x=350,y=250)
 pygame.mixer.music.load("rec3.mpeg")
 playrec()
 print('Measuring Body Temprature')
 time.sleep(5)
 visitlabel.config(text='Stand Still, Measuring Body Temprature')
 visitlabel.place(x=20,y=200)
 i2c=io.I2C(board.SCL,board.SDA,frequency=100000)
 mlx=adafruit_mlx90614.MLX90614(i2c)
 BodyTemp=mlx.object_temperature + 5
 print('Temp',BodyTemp)
 if BodyTemp > 38.5:
  print('Temprature is Higher Than Normal')
  emergancymail()
 print('Measuring SPO2 & BPM')
 pygame.mixer.music.load("rec4.mpeg")
 playrec()
 time.sleep(5)
 visitlabel.config(text='Insure Your Finger is on the Red Light, Measuring SPO2.')
 visitlabel.place(x=20,y=200)
 parser = argparse.ArgumentParser(description="Read and print data from MAX30102")
 parser.add_argument("-r", "--raw", action="store_true",
 help="print raw data instead of calculation result")
 parser.add_argument("-t", "--time", type=int, default=30,
 help="duration in seconds to read from sensor, default 30")
 args = parser.parse_args()
 print('sensor starting...')
 hrm = HeartRateMonitor(print_raw=args.raw, print_result=(not args.raw))
 hrm.start_sensor()
 pygame.mixer.music.load("rec5.mpeg")
 playrec()
 try:
  time.sleep(args.time)
 except KeyboardInterrupt:
  print('keyboard interrupt detected, exiting...')
 hrm.stop_sensor()
 print('sensor stoped!')
 x= MAX30102Results()
 print('SPO2',x[0])
 print('BPM',x[1])
 medl.place_forget()
 visitlabel.config(text='We are Done, Thank You! Hope You Heal Soon.')
 visitlabel.place(x=20,y=200)
 pygame.mixer.music.load("rec6.mpeg")
 playrec()
 FBaddress = '/patients/UI/vital_sign/26-0602021/ChildID'
 firebasecall.put(FBaddress,'oxygen', x[0])
 firebasecall.put(FBaddress,'ppm', x[1])
 firebasecall.put(FBaddress,'temp', BodyTemp)
 time.sleep(5)
#=======================================================================
#=======================Button Functions====================================
def startpage():
 f1B.destroy()
 bgl.place(x=0,y=0)
 auto.place(x=350, y=250)
 pharma.place(x=20, y=500)
 speaking.place(x=750, y=500)
 
def autoBC():
 auto.place_forget()
 visitlabel.place(x=100,y=200)
 autoth.start()

def pharmaBC():
 pharmago()
 arm()
 pharmaback()
 
def speakingBC():
 visitlabel.config(text='Ask RONA Somthing!')
 visitlabel.place(x=200,y=200)
 listen()
 visitlabel.place_forget()
#=======================================================================
#=====================The Thread==========================================
class Demo:
 def autoTF(self):
   arm()
   time.sleep(30)
   x=0
   while x==0:
     if not detecttime():
      time.sleep(30)
      detecttime()
     else:
       x=1
       visit()
       arm()
       med()
       visitback()
       visittime=["11","50"]
       x=0
   while x==0:
     if not detecttime():
       time.sleep(60)
       detecttime()
     else:
      x=1
autoth=Thread(target=Demo().autoTF)
#=======================================================================
#===============Main Loop=================================================
root=Tk()
root.title("Robo-Nurse GUI")
root.geometry('1000x550')
welcomeimg=ImageTk.PhotoImage(Image.open('bgimg.jpeg'))
f1B=Button(image=welcomeimg, command=startpage)
f1B.place(x=0,y=0)#Welcome frame as full screen Button
bgimg=ImageTk.PhotoImage(Image.open('bgimg2.jpeg'))
bgl=Label(image=bgimg)
auto=Button(root,text='Autonomous Nurse', pady=5,padx=5,bd=2,font=('Arial 
bold',25),fg='#25A4C0',bg='white',activebackground='#25A4C0',command=autoBC)
pharma=Button(root,text='Get Medicine Request', pady=5,padx=5,bd=2,font=('Arial 
bold',20),fg='#25A4C0',bg='white',activebackground='#25A4C0',command=pharmaBC)
visitlabel=Label(root,text='Checking Schedule',font=('Arial bold',25),fg='#25A4C0',bg='white')
medimg=ImageTk.PhotoImage(Image.open('guimg1.jpeg'))
medl=Label(image=medimg)
speaking=Button(root,text='Talk with RONA', pady=5,padx=5,bd=2,font=('Arial 
bold',20),fg='#25A4C0',bg='white',activebackground='#25A4C0',command=speakingBC)
root.mainloop()
