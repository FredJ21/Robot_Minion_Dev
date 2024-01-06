
import sys
import os
import _thread

from time import sleep

import pigpio

TIMEOUT_BUTTON = 5

PLAYER     = "/usr/bin/mpg321"
SOUNDS_REP = os.path.dirname(__file__) +"/../sounds/"
BYBY       = PLAYER +" "+ SOUNDS_REP+ "bye-bye.mp3"

# -----------------------------------------------------------------------------
#                           COLOR

class col:
    R = '\033[1;31m' # Red
    g = '\033[0;32m' # Green
    G = '\033[1;32m' # Green
    Y = '\033[1;33m' # Yellow
    B = '\033[1;34m' # Blue
    W = '\033[1;37m' # Write
    D = '\033[0;39m' # Default

# -----------------------------------------------------------------------------
#                       LOG stdout & stderr

class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "a",1)

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.write("")
        self.log.write("")

# -----------------------------------------------------------------------------
#
def sigterm_handler(_signo, _stack_frame):

    print("\n")
    print("      =========================================================")
    print("                "+ col.R +"------ STOP ------"+ col.D )
    print("      =========================================================")
    sys.exit(0)




# -----------------------------------------------------------------------------
#                           LED & Button Raspberry

class Led_control(object):

    def __init__(self, led_gpio):

        self.led_gpio       = led_gpio

        self.led = LED(self.led_gpio)

        self.head = "["+ col.g + "Led control Thread"+ col.D +"] "
        self.running = True


    def start(self):

        print(self.head+ "Starting")
        self.thread_id = _thread.start_new_thread(self.loop,() )

    def stop(self):

        print(self.head+ "Stoping")
        self.running = False

    def loop(self): 

        while self.running:

            self.led.on()
            sleep(0.1)
            self.led.off()
            sleep(0.1)


class Led_and_button_control(object):


    def __init__(self, led_gpio, button_gpio):

        self.led_gpio       = led_gpio
        self.button_gpio    = button_gpio

        self.button_timeout = TIMEOUT_BUTTON

        self.head = "["+ col.g + "Led and Button control Thread"+ col.D +"] "
        self.running = True


    def start(self):

        print(self.head+ "Starting")
        self.thread_id = _thread.start_new_thread(self.loop,() )

    def stop(self):

        print(self.head+ "Stopping")
        self.running = False

    def loop(self): 

        pi = pigpio.pi()

        # LED
        pi.set_mode(self.led_gpio, pigpio.OUTPUT)
        # Bouton
        pi.set_mode(self.button_gpio, pigpio.INPUT)
        pi.set_pull_up_down(self.button_gpio, pigpio.PUD_UP)

        while self.running:

            pi.write(self.led_gpio, pigpio.HIGH)
            sleep(0.5)
            pi.write(self.led_gpio, pigpio.LOW)
            sleep(0.5)


            button_state = pi.read(self.button_gpio)

            if not button_state:
                self.button_timeout -= 1
                print(self.head+"Button Gpio "+ str(self.button_gpio) +" is pressed, shutdown in "+ str(self.button_timeout) +"s")

                if self.button_timeout <= 0 :
                    os.system(BYBY)
                    os.system('sudo shutdown -h now')

            else :
                self.button_timeout = TIMEOUT_BUTTON

        pi.stop()
        print(self.head+ "Stopped")


