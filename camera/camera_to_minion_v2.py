#!/home/pi/MINION/venv/bin/python
# -----------------------------------------------------------------------------
#                                   TEST
#
#                                                           Fred J. 01/2024
# -----------------------------------------------------------------------------
import cv2
from picamera2 import Picamera2

import mediapipe as mp

import threading
import psutil
import socket

from http.server import BaseHTTPRequestHandler, HTTPServer
from os.path import exists
from time import time 

# --------------------
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

# --------------------
# Mediapipe
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(    min_detection_confidence=0.5,
                        min_tracking_confidence=0.5)


# --------------------[ UDP Socket
MY_DST_PORT = 21000
MY_DST_IP   = '127.0.0.1'

addrinfo = socket.getaddrinfo(MY_DST_IP, None)[0]
s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)



# --------------------
PROCESSING_FLAG_FILE = "/tmp/enable_minion_opencv"

processing_freq = 0.1                 # Traitement OpenCV toutes les X secondes
processing_last_result = None
processing_last = 0



# -----------------------------------------------------------------------------
def main():

    global img

    ip_list = get_network_interfaces()
    
    print("\n\n----------------------------------------")
    print("cv2 version : ", cv2.__version__)
    print("\n Go to :")

    for ip in ip_list :
        print("http://"+ ip +":8000/video_feed")

    print("----------------------------------------\n\n")

    
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    while True :

        img_tmp = picam2.capture_array()
        img_tmp = cv2.cvtColor(img_tmp, cv2.COLOR_BGRA2BGR)

        if exists(PROCESSING_FLAG_FILE) :
            img = video_processing(img_tmp)
        else :
            img = img_tmp

# -----------------------------------------------------------------------------
def video_processing(frame):

    global processing_last_result 
    global processing_last 



    if time() > processing_last + processing_freq :

        print(time())
        processing_last_result = pose.process(frame)

        processing_last = time()


    results = processing_last_result


    if results.pose_landmarks :

        mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())


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
            if   p[0].x > 0.6 :       send('{ "Oeil_X":"-5" }')
            #elif p[0].x < 0.3 :       send('{ "Oeil_X":"+100" }') 
            elif p[0].x < 0.4 :       send('{ "Oeil_X":"+5" }')

            #if   p[0].y > 0.7 :       send('{ "Oeil_Y":"+100" }') 
            if p[0].y > 0.6 :       send('{ "Oeil_Y":"+5" }')
            #elif p[0].y < 0.3 :       send('{ "Oeil_Y":"-100" }') 
            elif p[0].y < 0.4 :       send('{ "Oeil_Y":"-5" }')



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


    return frame

# -----------------------------------------------
def send(val):

    DATA_string_encoded = val.encode()
    s.sendto(DATA_string_encoded , (addrinfo[4][0], MY_DST_PORT))


# -----------------------------------------------------------------------------
class VideoStreamHandler(BaseHTTPRequestHandler):

    global img

    def do_GET(self):

        if self.path == '/video_feed':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()

            while True:

                _, jpeg = cv2.imencode('.jpg', img)
                frame = jpeg.tobytes()

                try:
                    self.wfile.write(b'--frame\r\n')
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
                except:
                    print("break")
                    break



        else:
            self.send_response(404)
            self.end_headers()

# -----------------------------------------------------------------------------
def start_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, VideoStreamHandler)
    httpd.serve_forever()


# -----------------------------------------------------------------------------
def get_network_interfaces():

    interfaces = []
    
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
            
        # Stocker les adresses IP de chaque interface
        for address in interface_addresses:

            if str(address.family) == '2':          # AddressFamily.AF_PACKET
                interfaces.append(address.address)

    return interfaces

# -----------------------------------------------------------------------------
if __name__ == "__main__":

    main()

