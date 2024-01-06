#!/home/pi/MINION/venv/bin/python
# -----------------------------------------------------------------------------
#                        Minion Project
#
#                                                               Fred J. 06/2023
# -----------------------------------------------------------------------------
import sys
import os
import signal
import json

from time import sleep
from time import time

from adafruit_servokit import ServoKit              #pip3 install adafruit-circuitpython-servokit

sys.path.append(os.path.dirname(__file__) +'/../lib')

from fred_lib       import col
from fred_lib       import Logger
from fred_lib       import Led_and_button_control

from fred_motor     import read_config_motor
from fred_motor     import motor_process
from fred_motor     import receiver_UDP


# -----------------------------------------------
#               CONFIG
#
MY_LOCAL_IP = "0.0.0.0"
MY_LOCAL_PORT = 21000

my_led_gpio     = 21
my_button_gpio  = 20

CONFIG = os.path.dirname(__file__) +"/data.json"

LOG = "/tmp/minion.log"
sys.stdout = Logger(LOG)
sys.stderr = Logger(LOG)


PLAYER = "/usr/bin/mpg321"
SOUNDS_REP = os.path.dirname(__file__) +"/../sounds/"

start_action = PLAYER +" "+ SOUNDS_REP+ "2_hello9.mp3"
stop_action  = PLAYER +" "+ SOUNDS_REP+ "1_ta-da-29.mp3"



my_config = None
my_motor_process = None
my_receiver_UDP = None


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def main():

    global my_config
    global my_motor_process
    global my_receiver_UDP

    a = 0
    fps_count = 0
    t = time()


    print("\n")
    print("      ---------------------------------------------------------")
    print("                    "+ col.G +"MINION"+ col.D +"")
    print("      ---------------------------------------------------------")
    print("\n")



    # Gestion de l'arret
    signal.signal(signal.SIGTERM, sigterm_handler)


    # Gestion de la LED                                                         TODO : Corriger lib
    my_thread_Led = Led_and_button_control( my_led_gpio, my_button_gpio )
    my_thread_Led.start()
    sleep(0.1)

    # Gestion des changements de conf
    my_config = read_config_motor(CONFIG)
    my_config.start() 
    sleep(1)
    my_motor_list = my_config.get_motor_list()      # liste d'objet de type "motor_class"
    sleep(1)

    # Gestion des moteurs
    my_motor_process = motor_process()
    my_motor_process.start()
    my_motor_process.set_data(my_motor_list)        # pointeur vers my_motor_list

    # Gestion UDP
    my_receiver_UDP = receiver_UDP(MY_LOCAL_IP, MY_LOCAL_PORT) 
    my_receiver_UDP.start()
    my_receiver_UDP.set_data(my_motor_list)         # pointeur vers my_motor_list


    DEBUG = False
    
    os.system(start_action)

    # ----------[ Loop ]----------
    while True:

        if DEBUG :

            print("------------------------------------------------------------")
            
            for i in my_motor_list.keys() :

#                print(  my_motor_list[i].name 
#                    +":"+ str(my_motor_list[i].consigne) 
#                    +":"+ str(my_motor_list[i].current) 
#                    + " - ", end='' )

                my_motor_list[i].dump()

            print()

        sleep(10)

        #print("dump test")
        #my_motor_list["Bras_D"].dump()

        #my_motor_list["Bras_D"].set_consigne(333)




    # -------------------------
    #       THE END

    print("STOP")
    my_receiver_UDP.stop()
    my_motor_process.stop()
    my_config.stop()
    my_thread_Led.stop()

    print("---[ END ]---")




# -----------------------------------------------------------------------------
#               Fonctions
def sigterm_handler(_signo, _stack_frame):

    global my_config
    global my_motor_process
    global my_receiver_UDP

    # son a l'arret
    os.system(stop_action)

    my_config.stop() 
    my_motor_process.stop()
    my_receiver_UDP.stop()

    print("\n")
    print("      =========================================================")
    print("                "+ col.R +"------ STOP ------"+ col.D )
    print("      =========================================================")


    sys.exit(0)




# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    main()








