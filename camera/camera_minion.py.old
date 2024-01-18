#!/home/pi/MINION/venv/bin/python
#------------------------------------------------------------------------------
#                        Minion Project
#
#                                                               Fred J. 06/2023
#
#	pip3 install opencv-python
#	apt-get install libatlas-base-dev
#------------------------------------------------------------------------------

import sys
import cv2
import mediapipe as mp
from http.server import BaseHTTPRequestHandler, HTTPServer

from time import sleep
from time import time

from os.path import exists

import _thread
import signal

import socket

last_frame = None
a = 0

PROCESSING_TIME = 0.1             # Traitement toute les x secondes

PROCESSING_FLAG_FILE = "/tmp/enable_minion_opencv"


# --------------------
MY_DST_PORT = 21000
MY_DST_IP   = '127.0.0.1'

# --------------------[ UDP Socket
addrinfo = socket.getaddrinfo(MY_DST_IP, None)[0]
s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)


# --------------------
# Mediapipe
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(    min_detection_confidence=0.5,
                        min_tracking_confidence=0.5)


# -----------------------------------------------
# -----------------------------------------------
def main():

    print("\n")
    print("      ---------------------------------------------------------")
    print("                      "+ col.G +"START"+ col.D +"")
    print("      ---------------------------------------------------------")
    print("\n")

    # Gestion de l'arret
    signal.signal(signal.SIGTERM, sigterm_handler)


    _thread.start_new_thread(web_server_thread, () )
    _thread.start_new_thread(capture_video_thread, () )

    while True :

        sleep(3)


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


# -----------------------------------------------
def sigterm_handler(_signo, _stack_frame):

    print("\n")
    print("      =========================================================")
    print("                      "+ col.R +"STOP"+ col.D +"")
    print("      =========================================================")
    sys.exit(0)


# -----------------------------------------------------------------------------
class VideoStreamHandler(BaseHTTPRequestHandler):

    global last_frame

    def do_GET(self):
        if self.path == '/video_feed':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()

            while True:
                
                frame = last_frame

                if frame is not None:
                    _, jpeg = cv2.imencode('.jpg', frame)
                    frame = jpeg.tobytes()

                    self.wfile.write(b'--frame\r\n')
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
                    sleep(0.1)

        else:
            self.send_response(404)
            self.end_headers()

# -----------------------------------------------------------------------------
def web_server_thread():

    global last_frame

    head = "["+ col.g + "Web Server Thread"+ col.D +"] "
    print(head+ "Starting")

    server_address = ('', 8000)
    httpd = HTTPServer(server_address, VideoStreamHandler)
    httpd.serve_forever()


# -----------------------------------------------------------------------------
def capture_video_thread():

    head = "["+ col.g + "Capture Video Thread"+ col.D +"] "
    print(head+ "Starting")

    global last_frame

    cap = cv2.VideoCapture(0)
#    cap.set(3, 640)
#    cap.set(4, 480)

    flag_display_flip = False
    flag_processing = True

    last_processing = 0

    # --------------------
    while True:

        success, img = cap.read()
        if not success:
            break

        # --------------------
        if flag_display_flip :
            img = cv2.flip(img, 1)


        # --------------------
        if exists(PROCESSING_FLAG_FILE) :   flag_processing = True
        else :                              flag_processing = False

        # --------------------
        if flag_processing and time() > last_processing + PROCESSING_TIME :
   
            results = video_processing(img)
            
            last_processing = time() 

        
        if flag_processing :

            mp_drawing.draw_landmarks(
                img,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())





        last_frame = img
        
        sleep(0.01)

# -----------------------------------------------------------------------------
def video_processing(img):
            
    global a
    
    #print(a)
    a += 1
    
    # To improve performance, optionally mark the image as not writeable to pass by reference.
    #img.flags.writeable = False
    #imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
    #results = pose.process(imgRGB)
    results = pose.process(img)
            
    #img.flags.writeable = True



    #for landmark in results.pose_landmarks.landmark :
    #    print(landmark.x, landmark.y, landmark.z, landmark.visibility)

    if results.pose_landmarks :
            
        '''
        0 - nose
        1 - left eye (inner)
        2 - left eye
        3 - left eye (outer)
        4 - right eye (inner)
        5 - right eye
        6 - right eye (outer)
        7 - left ear
        8 - right ear
        9 - mouth (left)
        10 - mouth (right)
        11 - left shoulder
        12 - right shoulder
        13 - left elbow
        14 - right elbow
        15 - left wrist
        16 - right wrist
        17 - left pinky
        18 - right pinky
        19 - left index
        20 - right index
        21 - left thumb
        22 - right thumb
        23 - left hip
        24 - right hip
        25 - left knee
        26 - right knee
        27 - left ankle
        28 - right ankle
        29 - left heel
        30 - right heel
        31 - left foot index
        32 - right foot index
        '''
        
        visibility_limit = 0.5
        p = results.pose_landmarks.landmark

        # --------------------
        # Nez
        if p[0].visibility > visibility_limit:

            #print(p[0].x, p[0].y)

            #if   p[0].x > 0.7 :       send('{ "Oeil_X":"-100" }') 
            if   p[0].x > 0.6 :       send('{ "Oeil_X":"-30" }') 
            #elif p[0].x < 0.3 :       send('{ "Oeil_X":"+100" }') 
            elif p[0].x < 0.4 :       send('{ "Oeil_X":"+30" }') 

            #if   p[0].y > 0.7 :       send('{ "Oeil_Y":"+100" }') 
            if p[0].y > 0.6 :       send('{ "Oeil_Y":"+30" }') 
            #elif p[0].y < 0.3 :       send('{ "Oeil_Y":"-100" }') 
            elif p[0].y < 0.4 :       send('{ "Oeil_Y":"-30" }') 




        # --------------------
        # Bras Droite
        if p[12].visibility > visibility_limit \
            and p[14].visibility > visibility_limit \
            and p[16].visibility > visibility_limit :

            if p[12].y > p[14].y and p[14].y > p[16].y :
            
                #print ("Droit OK --> HAUT")
                send('{ "Bras_G":"800" }')
            
            elif p[12].y < p[14].y and p[14].y < p[16].y :
                
                #print ("Droit OK --> BAS")
                send('{ "Bras_G":"200" }')

        # --------------------
        # Bras Gauche
        if p[11].visibility > visibility_limit \
            and p[13].visibility > visibility_limit \
            and p[15].visibility > visibility_limit :

            if p[11].y > p[13].y and p[13].y > p[15].y :
            
                #print ("Gauche OK --> HAUT")
                send('{ "Bras_D":"800" }')
            
            elif p[11].y < p[13].y and p[13].y < p[15].y :
                
                #print ("Gauche OK --> BAS")
                send('{ "Bras_D":"200" }')

     
     
     
     #           DATA_string_encoded = '{ "play": "1_cri.mp3" }'.encode()



    return results

# -----------------------------------------------
def send(val):

    DATA_string_encoded = val.encode()
    s.sendto(DATA_string_encoded , (addrinfo[4][0], MY_DST_PORT))


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# -----------------------------------------------
if __name__ == "__main__":
    main()

