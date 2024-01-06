#!/usr/bin/python3

import sys
import os
import psutil
import threading
import json
import socket

from time import sleep
from time import time
from simple_file_checksum import get_checksum
from numpy import interp

import pigpio

sys.path.append('/home/pi/FRED/Raspberry/LIB')
sys.path.append('/DATA/FRED/DEV/Raspberry/LIB')

from fred_lib       import col

REP_SON = "/home/pi/FRED/Raspberry/0_SON/MINION"


pi = pigpio.pi()

PWM_FREQUENCY = 100         # Servo à 100Hz
PWM_FREQUENCY_CC = 10000    # Moteur Courant Continu à 10kHz
ANGLE_RANGE = (0, 180)
PULSE_RANGE = (500, 2500)

MOTOR_CC_SPEED    = 75
MOTOR_CC_SPEED_2  = 110
MOTOR_CC_SPEED_3  = 150
MOTOR_CC_Acceleration = 5
MOTOR_CC_Deceleration = 10


# -----------------------------------------------------------------------------
class read_config_motor(object):

    def __init__(self, file):

        self.file = file
        self.cheksumfile = 0
        self.motor_list = {}        # liste d'objet de type "motor_class"

        self.head = "["+ col.g + "read config thread"+ col.D +"] "
        self.running = True

    # ----------------------
    def start(self):

        print(self.head+ "starting")
        self.thread = threading.Thread(target=self.loop, args=())
        self.thread.start()

    # ----------------------
    def stop(self):

        print(self.head+ "Stopping")
        self.running = False

    # ----------------------
    def loop(self):

        thread_id = self.thread.ident
        print(self.head + "ID du thread :", thread_id)

        old_checksumfile = self.cheksumfile

        while self.running:

            ERROR = False

            # ----------------------
            # Checksum file 
            self.cheksumfile = get_checksum(self.file)

            if self.cheksumfile != old_checksumfile : 
                print(self.head + col.R + "new config file !"+ col.D)
    
                # ----------------------
                # Read config File
                try:
                    f = open(self.file)
                    data = json.load(f)
                    f.close()
                except Exception as e:
                    print(self.head + col.R + "read File error !!!"+ col.D)
                    print(e)
                    ERROR = True

            
                # ----------------------
                if not ERROR:
 #                   print("----[ motor_list ]----")
 #                   print(self.motor_list)
 #                   print("------------")

                    # parse config
                    for obj in data['motor']:

                        #print( obj )

                        if not obj['name'] in self.motor_list.keys():                    # si l'objet existe pas !!!

                            self.motor_list[obj['name']] = motor_class( name=obj['name'])
                        

                        if 'gpio' in obj.keys() :           self.motor_list[obj['name']].gpio = obj['gpio']
                        if 'gpioList' in obj.keys() :       self.motor_list[obj['name']].gpioList = obj['gpioList']
                        if 'motor_type' in obj.keys() :     self.motor_list[obj['name']].motor_type = obj['motor_type']
                        if 'reverse' in obj.keys() :        self.motor_list[obj['name']].reverse = obj['reverse']
                        if 'pwm_min' in obj.keys() :        self.motor_list[obj['name']].pwm_min = obj['pwm_min']
                        if 'pwm_max' in obj.keys() :        self.motor_list[obj['name']].pwm_max = obj['pwm_max']
                        if 'pwm_home' in obj.keys() :       self.motor_list[obj['name']].pwm_home = obj['pwm_home']
                        if 'pwm_offset' in obj.keys() :     self.motor_list[obj['name']].pwm_offset = obj['pwm_offset']

                        
#                        print("----------------------------------")
#                        self.motor_list[obj['name']].dump()
                        self.motor_list[obj['name']].init()
            
                    old_checksumfile = self.cheksumfile

            sleep(5)

        print(self.head+ "Stopped")

    # ----------------------
    def get_motor_list(self):

        return self.motor_list

# -----------------------------------------------------------------------------
class motor_class(object):

    global pi

    # ----------------------
    def __init__(self, name, 
            motor_type  = "Servo", 
            reverse     = False,  
            pwm_min     = 0, 
            pwm_max     = 1000, 
            pwm_home    = 500, 
            pwm_offset  = 0, 
            gpio        = 0, 
            gpioList    = [] 
            ):
        
        self.name           = name
        self.motor_type     = motor_type 
        self.reverse        = reverse 
        self.pwm_min        = pwm_min
        self.pwm_max        = pwm_max   
        self.pwm_home       = pwm_home 
        self.pwm_offset     = pwm_offset 
        self.gpio           = gpio 
        self.gpioList       = gpioList
        self.current        = None
        self.consigne       = None
        self.pwm_lastChg    = time()
        self.is_stopped     = False

        if self.pwm_max > 1000 :
            print(col.R + "GLOBAL ERROR : pwm_max > 1000")
            exit(1)

        if self.pwm_min < 0 :
            print(col.R + "GLOBAL ERROR : pwm_min < 0")
            exit(1)

    # ----------------------
    def init(self):

        # ----------
        if self.motor_type == "servo" :

            pi.set_mode(self.gpio, pigpio.OUTPUT)
            pi.set_PWM_frequency(self.gpio, PWM_FREQUENCY)

            self.consigne = self.pwm_home

            if not self.reverse: 
                pulse_width = interp(self.consigne, [0,1000], [PULSE_RANGE[0], PULSE_RANGE[1]])
            else:
                pulse_width = interp(self.consigne, [0,1000], [PULSE_RANGE[1], PULSE_RANGE[0]])

            pi.set_servo_pulsewidth(self.gpio, pulse_width)             # send to GPIO

        # ----------
        elif self.motor_type == "CC" :

            #print("INIT")
            for gpio in self.gpioList :

                #print(gpio)
                pi.set_mode(gpio, pigpio.OUTPUT)
                pi.set_PWM_frequency(gpio, PWM_FREQUENCY_CC)

                self.consigne = 0
                self.current = 0
                pi.write(gpio, 0)


    # ----------------------
    def dump(self):

        print ("---["+ self.name +"]---")
        print ("     Type : "+self.motor_type)
        print ("     Reverse : "+ str(self.reverse))
        print ("     Min  : "+ str(self.pwm_min))
        print ("     Max  : "+ str(self.pwm_max))
        print ("     Home : "+ str(self.pwm_home))
        print ("     Gpio : "+ str(self.gpio))
        print ("     GpioList : "+ str(self.gpioList))
        print ("     Current : "+ str(self.current))
        print ("     consigne : "+ str(self.consigne))

    # ----------------------
    def set_pwm_home(self, pwm_home):
        self.pwm_home       = pwm_home 

    # ----------------------
    def set_consigne(self, consigne):

        special_Action = str(consigne)[0:1]             #  + ou -  

        if consigne == "home" :     consigne = self.pwm_home 

        try :
            if special_Action == '+' :          consigne = self.get_current() + int(consigne)
            elif special_Action == '-' :        consigne = self.get_current() + int(consigne)   # !! consigne negative !!
            else :                              consigne = int(consigne)
        except Exception as e:
            print("consigne error : ", e)
            return

        if consigne > self.pwm_max :    consigne = self.pwm_max
        if consigne < self.pwm_min :    consigne = self.pwm_min

        self.consigne      = consigne 

    # ----------------------
    def set_consigne_CC(self, consigne):

        if consigne > 255 :     consigne = 255
        if consigne < -255 :    consigne = -255

        self.consigne       = consigne 
        self.pwm_lastChg    = time() 
        self.is_stopped     = False



    # ----------------------
    def get_current(self):
        return self.current 




# -----------------------------------------------------------------------------
class motor_process(object):

    global pi

    def __init__(self):

        self.data = { } 

        self.head = "["+ col.g + "motor process thread"+ col.D +"] "
        self.DEBUG = False
        self.running = True

    # ----------------------
    def start(self):

        print(self.head+ "starting")
        self.thread = threading.Thread(target=self.loop, args=())
        self.thread.start()

    # ----------------------
    def stop(self):

        print(self.head+ "Stopping")
        self.running = False

    # ----------------------
    def set_data(self, data):

        self.data = data
 
    # ----------------------
    def loop(self):

        thread_id = self.thread.ident
        print(self.head + "ID du thread :", thread_id)

        while self.running:

#            print(self.head+ " ----------")

            if self.DEBUG : print(self.head, end='')

            for i in self.data.keys():

                # au demarrage 
                if self.data[i].current == None :
                    self.data[i].set_consigne(self.data[i].pwm_home)


                if self.DEBUG :
                    print(" " + self.data[i].name 
                        + " " + str(self.data[i].motor_type)
                        + " " + str(self.data[i].consigne)
                        + " " + str(self.data[i].current)
                        + " - ", end='\n' )


                # ---------------------------------------------------
                # traitement de la consigne SERVO
                if self.data[i].motor_type == "servo" :

                    if self.data[i].current != self.data[i].consigne :
                        self.data[i].current = self.data[i].consigne
                    
                        # map la consigne (0->1000) en pulse (500->2500)

                        val = self.data[i].current + self.data[i].pwm_offset
                        if val > 1000 :  val = 1000
                        if val < 0 :     val = 0

                        if not self.data[i].reverse: 
                            pulse_width = interp(val, [0,1000], [PULSE_RANGE[0], PULSE_RANGE[1]])
                        else:
                            pulse_width = interp(val, [0,1000], [PULSE_RANGE[1], PULSE_RANGE[0]])
                        

                        #print(self.data[i].gpio, pulse_width)
                        pi.set_servo_pulsewidth(self.data[i].gpio, pulse_width)         # Send to GPIO
                        self.data[i].pwm_lastChg = time()
        
       
                    if time() > self.data[i].pwm_lastChg + 10 :
                        pi.set_servo_pulsewidth(self.data[i].gpio, 0)                   # Send to GPIO

                # ---------------------------------------------------
                # traitement de la consigne CC
                if self.data[i].motor_type == "CC" :
                        

                    if self.data[i].current != self.data[i].consigne :

                         
                        if self.data[i].consigne > self.data[i].current :       self.data[i].current += MOTOR_CC_Acceleration
                        if self.data[i].consigne < self.data[i].current :       self.data[i].current -= MOTOR_CC_Deceleration

                        #self.data[i].current = self.data[i].consigne


                        #print(" " + self.data[i].name 
                        #        + " " + str(self.data[i].motor_type)
                        #        + " " + str(self.data[i].consigne)
                        #        + " " + str(self.data[i].current)
                        #        + " " + str(self.data[i].gpioList)
                        #        )


                        # Si la consigne est négative
                        if self.data[i].current < 0 :                       reverse = True      
                        else :                                              reverse = False

                        # Si le moteur est en reverse
                        if self.data[i].reverse and reverse == True :       reverse = False   
                        elif self.data[i].reverse and reverse == False :    reverse = True   


                        if reverse :
                            pi.set_PWM_dutycycle(self.data[i].gpioList[0], abs(self.data[i].current))       # Send to GPIO
                            pi.set_PWM_dutycycle(self.data[i].gpioList[1], 0) 
                        
                        else :
                            pi.set_PWM_dutycycle(self.data[i].gpioList[1], abs(self.data[i].current))       # Send to GPIO
                            pi.set_PWM_dutycycle(self.data[i].gpioList[0], 0) 

            


                    # Arret automatique des moteurs
                    #
                    if time() > self.data[i].pwm_lastChg + 0.1 and not self.data[i].is_stopped :
                        self.data[i].consigne = 0
                        self.data[i].is_stopped = True


            if self.DEBUG : print()

            sleep(0.01)

        print(self.head+ "Stopped")

# -----------------------------------------------------------------------------
class receiver_UDP(object):

    def __init__(self, ip, port):

        self.data = { } 
        self.ip = ip
        self.port = port

        self.head = "["+ col.g + "receiver UDP thread"+ col.D +"] "
        self.running = True

    # ----------------------
    def start(self):

        print(self.head+ "starting to UDP:"+ self.ip + ":" + str(self.port))
        self.thread = threading.Thread(target=self.loop, args=())
        self.thread.start()

    # ----------------------
    def stop(self):

        print(self.head+ "Stopping")
        self.running = False

    # ----------------------
    def set_data(self, data):

        self.data = data

    # ----------------------
    def loop(self):

        thread_id = self.thread.ident
        print(self.head + "ID du thread :", thread_id)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Socket
        sock.bind((self.ip, self.port))
        sock.settimeout(5.0)

        while self.running :

            #print(self.head+ " oki ")

            ERROR = False
        
            try :
                data_rx_encoded, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
                #print(self.head+ "received message: %s" % data_rx)
            except:
                continue

            try :
                data_rx_decoded = data_rx_encoded.decode("utf-8")
                data_rx = json.loads(data_rx_decoded)
            except:
                print(self.head+ col.R + "Erreur de decodage JSON" + col.D)
                ERROR = True


            if not ERROR :
                print(self.head+ col.Y + str(data_rx) + col.D)
                
                # traitement
                for key in data_rx.keys():
                    
                    #print(key)
                    if key in self.data:            # dans la liste des moteurs ?

                        self.data[key].set_consigne(data_rx[key])

                    elif key == 'play' :
                        
                        print(self.head+ "Play sound : "+ str(data_rx[key]) + col.D)
                        play_sound(data_rx[key])
        
                    elif key == 'KEY' :

                        V = MOTOR_CC_SPEED
                        M = [ 0, 0 ]        # Tableau des vitesse Droite/Gauche


                        
                        if 'Alt' in data_rx[key] :          V = MOTOR_CC_SPEED_2
                        if 'Shift' in data_rx[key] :        V = MOTOR_CC_SPEED_3

                        if   'ArrowUp' in data_rx[key] and 'ArrowRight' in data_rx[key]:    M = [  0,  V ]
                        elif 'ArrowUp' in data_rx[key] and 'ArrowLeft' in data_rx[key]:     M = [  V,  0 ]
                        elif 'ArrowDown' in data_rx[key] and 'ArrowRight' in data_rx[key]:  M = [  0, -V ]
                        elif 'ArrowDown' in data_rx[key] and 'ArrowLeft' in data_rx[key]:   M = [ -V,  0 ]
                        elif 'ArrowUp' in data_rx[key] :                                    M = [  V,  V ]
                        elif 'ArrowDown' in data_rx[key] :                                  M = [ -V, -V ]
                        elif 'ArrowRight' in data_rx[key] :                                 M = [ -V,  V ]
                        elif 'ArrowLeft' in data_rx[key] :                                  M = [  V, -V ]


                        if ' ' in data_rx[key] :                M = [  0,  0 ]
                        
                        self.data['Moteur_D'].set_consigne_CC(M[0])
                        self.data['Moteur_G'].set_consigne_CC(M[1])




                    else: 
                        print(self.head+ col.R + str(key) +" n'existe  pas !!!"+ col.D)

        print(self.head+ "Stopped")
 

# -----------------------------------------------------------------------------
def play_sound(son):


    CMD = "/usr/bin/omxplayer "+ REP_SON +"/"+ son +"&"

    os.system(CMD)
