#!/home/pi/MINION/venv/bin/python
# -----------------------------------------------------------------------------
#                        Minion Project
#
#                                                               Fred J. 06/2023
# -----------------------------------------------------------------------------
import sys
import os
import signal
import socket
from  time import sleep

import re

# -----------------------------------------------
#               CONFIG

MY_DST_PORT      = 21000
#MY_DST_IP   = '10.1.23.18'     
MY_DST_IP   = '127.0.0.1'     

DEBUG = True
#DEBUG = False

#DATA = { "X":33, "Y":77, "Z":127 }
#DATA_FILE = "DATA_to_send.txt"

REP = os.path.dirname(__file__)
DATA_FILE =  REP +"/" + sys.argv[1] 


A = 0

# -----------------------------------------------
#               COLOR

class col:

    R = '\033[1;31m' # Red
    g = '\033[0;32m' # Green
    G = '\033[1;32m' # Green
    Y = '\033[1;33m' # Yellow
    B = '\033[1;34m' # Blue
    W = '\033[1;37m' # Write
    D = '\033[0;39m' # Default



# --------------------[ UDP Socket
addrinfo = socket.getaddrinfo(MY_DST_IP, None)[0]
s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)

# -----------------------------------------------
# -----------------------------------------------
def main():

    head = "["+ col.g + "Play Sequence"+ col.D +"] "
    print(head+ "Starting")

    f = open(DATA_FILE, 'r')
    lines = f.readlines()
    f.close()



    for line in lines:

            line = line.strip()

            m = re.search( "sleep[ \t]+(\d+)", line )
            if m :
                val = m.group(1)
                print("sleep "+ str(val))
                sleep(int(val))

                continue

            m = re.search( "play[ \t]+([\w\.]+)", line )
            if m :
                val = m.group(1)
                print("play : "+ str(val))

                continue


            print("Send : "+ line)
            DATA_string_encoded = line.encode()
            s.sendto(DATA_string_encoded , (addrinfo[4][0], MY_DST_PORT))
            



# -----------------------------------------------------------------------------
if __name__ == "__main__":

    main()

