#!/home/pi/MINION/venv/bin/python
# -----------------------------------------------------------------------------
#                                   TEST
#
#                                                           Fred J. 01/2024
# -----------------------------------------------------------------------------
import cv2
from picamera2 import Picamera2

import mediapipe as mp

from time import sleep

import threading
import psutil
import socket

from http.server import BaseHTTPRequestHandler, HTTPServer
from os.path import exists
from time import time 

import sys
import os
sys.path.append(os.path.dirname(__file__) +'/../lib')

from fred_lib_DEV       import data_filter


# -----------------------------------------------------------------------------
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

# TEST - Lecture video
TEST_MODE   = False
video_path  = '/home/pi/MINION/test/test_2.mjpeg'
cap         = cv2.VideoCapture(video_path)


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

processing_freq = 0.01                 # Traitement OpenCV toutes les X secondes
processing_last_result = None
processing_last = 0


Global_status = {
        "last_detection":  0,
        "last_sleep":      0,
        "current_status":  "sleep"
        }

# --------------------


my_filter = data_filter()


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

        if not TEST_MODE :

            img_tmp = picam2.capture_array()
            img_tmp = cv2.cvtColor(img_tmp, cv2.COLOR_BGRA2BGR)


            if exists(PROCESSING_FLAG_FILE) :
                img = video_processing(img_tmp)
            else :
                img = img_tmp

        else :
            sleep(10)


# -----------------------------------------------------------------------------
def video_processing(frame):

    global processing_last_result 
    global processing_last 

    global Global_status


    if time() > processing_last + processing_freq :

        #print(time())
        processing_last_result = pose.process(frame)
        processing_last = time()


    results = processing_last_result



    print("last_detection :", Global_status["last_detection"],          "   last_sleep :", Global_status["last_sleep"],          "   status :", Global_status["current_status"]          )



    # passage en sommeil 
    if Global_status["current_status"] == "tracking" and time() > Global_status["last_detection"] + 300 :

        Global_status["last_sleep"] = time()
        Global_status["current_status"] = "sleep"
        print("Go to sleep")
        send('{"Bras_D": "home", "Bras_G": "home", "Bouche_D": "home", "Bouche_G": "home", "Oeil_X": "home", "Oeil_Y": "home"}')
        send('{"Bras_D_1": "home", "Bras_D_2": "home", "Bras_G_1": "home", "Bras_G_2": "home"}')
        send('{"play": "1_ha.mp3"}')

    # si le sommeil dure trop longtemps
    if Global_status["current_status"] == "sleep" and time() > Global_status["last_sleep"] + 300:
        Global_status["last_sleep"] = time()
        print("Je dorts !!!")
        send('{"gyro": "1000"}')
        send('{"play": "2_banana.mp3"}')
        sleep(1)
        send('{"gyro": "0"}')



    # Detection de pose
    if results.pose_landmarks :

        # le reveille
        if Global_status["current_status"] == "sleep" :
            Global_status["current_status"] = "tracking"
            send('{"play": "2_hello-2.mp3"}')


        Global_status["last_detection"] = time()


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

        # ----------------------------------------
        #           Suivi du visage
        # ----------------------------------------
        #   0 --> Nez
        #
        if p[0].visibility > visibility_limit and not TEST_MODE:


            x = my_filter.add_and_average("p_0_x", p[0].x)
            y = my_filter.add_and_average("p_0_y", p[0].y)
            
            #print(round(p[0].x, 3), round(p[0].y, 3), round(x, 3), round(y, 3))
            #print(round(x, 3), round(y, 3))

            if   x > 0.75 :       send('{ "Oeil_X":"-30" }')
            elif x > 0.65 :       send('{ "Oeil_X":"-20" }')
            elif x > 0.55 :       send('{ "Oeil_X":"-5" }')
            elif x < 0.25 :       send('{ "Oeil_X":"+30" }')
            elif x < 0.35 :       send('{ "Oeil_X":"+20" }')
            elif x < 0.45 :       send('{ "Oeil_X":"+5" }')

            if   y > 0.75 :       send('{ "Oeil_Y":"+30" }')
            elif y > 0.65 :       send('{ "Oeil_Y":"+20" }')
            elif y > 0.55 :       send('{ "Oeil_Y":"+5" }')
            elif y < 0.25 :       send('{ "Oeil_Y":"-30" }')
            elif y < 0.35 :       send('{ "Oeil_Y":"-20" }')
            elif y < 0.45 :       send('{ "Oeil_Y":"-5" }')

            '''
            p_x = 100 - int(p[0].x *100)
            p_y = int(p[0].y *100)

            send('{ "Oeil_X":"%'+ str(p_x) +'", "Oeil_Y":"%'+ str(p_y) +'" }')
            '''


        # ----------------------------------------
        #           suivi de bras droit
        # ----------------------------------------
        #   12 --> epaule
        #   14 --> coude
        #   16 --> poignet
       
        Bras_Droit = None

        if p[12].visibility > visibility_limit \
            and p[14].visibility > visibility_limit \
            and p[16].visibility > visibility_limit :


            epaule_x    = my_filter.add_and_average("p_12_x", p[12].x)
            epaule_y    = my_filter.add_and_average("p_12_y", p[12].y)
            epaule_z    = my_filter.add_and_average("p_12_z", p[12].z)

            coude_x     = my_filter.add_and_average("p_14_x", p[14].x)
            coude_y     = my_filter.add_and_average("p_14_y", p[14].y)
            coude_z     = my_filter.add_and_average("p_14_z", p[14].z)

            poignet_x   = my_filter.add_and_average("p_16_x", p[16].x)
            poignet_y   = my_filter.add_and_average("p_16_y", p[16].y)
            poignet_z   = my_filter.add_and_average("p_16_z", p[16].z)
        

            y_distance_epaule_coude  = abs(epaule_y - coude_y)
            y_distance_coude_poignet = abs(coude_y - poignet_y)

            z_distance_epaule_poignet  = abs(epaule_z - poignet_z)


            #print(epaule_y, coude_y, poignet_y, y_distance_epaule_coude, y_distance_coude_poignet)
            #print( round(z_distance_epaule_poignet, 3) )

            if   poignet_y < coude_y and coude_y < epaule_y and y_distance_epaule_coude > 0.02 and y_distance_coude_poignet > 0.02 : 
                    print( "[Bras Droit] - vers le haut")
                    send('{ "Bras_G":"800", "Bras_G_1":"home", "Bras_G_2":"home" }')
                    Bras_Droit = "vers_le_haut"

            elif poignet_y > coude_y and coude_y > epaule_y and y_distance_epaule_coude > 0.02 and y_distance_coude_poignet > 0.02 : 
                    print( "[Bras Droit] - vers le bas")
                    send('{ "Bras_G":"200", "Bras_G_1":"home", "Bras_G_2":"home" }')
                    Bras_Droit = "vers_le_bas"

            elif y_distance_epaule_coude < 0.02 and y_distance_coude_poignet < 0.02 and z_distance_epaule_poignet < 0.2:
                    print( "[Bras Droit] - tendu vers la droite")
                    send('{ "Bras_G":"500", "Bras_G_1":"2000", "Bras_G_2":"home" }')
            
            elif y_distance_epaule_coude < 0.02 and y_distance_coude_poignet < 0.02 and z_distance_epaule_poignet > 0.2:
                    print( "[Bras Droit] - tendu vers l'avant")
                    send('{ "Bras_G":"500", "Bras_G_1":"home", "Bras_G_2":"home" }')
                
            elif y_distance_epaule_coude < 0.02 and y_distance_coude_poignet > 0.05 :
                    print( "[Bras Droit] - Popeye")
                    send('{ "Bras_G":"500", "Bras_G_1":"2000", "Bras_G_2":"1000" }')



        # ----------------------------------------
        #           suivi de bras gauche
        # ----------------------------------------
        #   11 --> epaule
        #   13 --> coude
        #   15 --> poignet
        
        Bras_Gauche = None

        if p[11].visibility > visibility_limit \
            and p[13].visibility > visibility_limit \
            and p[15].visibility > visibility_limit :


            epaule_x    = my_filter.add_and_average("p_11_x", p[11].x)
            epaule_y    = my_filter.add_and_average("p_11_y", p[11].y)
            epaule_z    = my_filter.add_and_average("p_11_z", p[11].z)

            coude_x     = my_filter.add_and_average("p_13_x", p[13].x)
            coude_y     = my_filter.add_and_average("p_13_y", p[13].y)
            coude_z     = my_filter.add_and_average("p_13_z", p[13].z)

            poignet_x   = my_filter.add_and_average("p_15_x", p[15].x)
            poignet_y   = my_filter.add_and_average("p_15_y", p[15].y)
            poignet_z   = my_filter.add_and_average("p_15_z", p[15].z)
        

            y_distance_epaule_coude  = abs(epaule_y - coude_y)
            y_distance_coude_poignet = abs(coude_y - poignet_y)

            z_distance_epaule_poignet  = abs(epaule_z - poignet_z)


            #print(epaule_y, coude_y, poignet_y, y_distance_epaule_coude, y_distance_coude_poignet)
            #print( round(z_distance_epaule_poignet, 3) )

            if   poignet_y < coude_y and coude_y < epaule_y and y_distance_epaule_coude > 0.02 and y_distance_coude_poignet > 0.02 : 
                    print( "[Bras Gauche] - vers le haut")
                    send('{ "Bras_D":"800", "Bras_D_1":"home", "Bras_D_2":"home" }')
                    Bras_Gauche = "vers_le_haut"

            elif poignet_y > coude_y and coude_y > epaule_y and y_distance_epaule_coude > 0.02 and y_distance_coude_poignet > 0.02 : 
                    print( "[Bras Gauche] - vers le bas")
                    send('{ "Bras_D":"200", "Bras_D_1":"home", "Bras_D_2":"home" }')
                    Bras_Gauche = "vers_le_bas"

            elif y_distance_epaule_coude < 0.02 and y_distance_coude_poignet < 0.02 and z_distance_epaule_poignet < 0.2:
                    print( "[Bras Gauche] - tendu vers la droite")
                    send('{ "Bras_D":"500", "Bras_D_1":"2000", "Bras_D_2":"home" }')
            
            elif y_distance_epaule_coude < 0.02 and y_distance_coude_poignet < 0.02 and z_distance_epaule_poignet > 0.2:
                    print( "[Bras Gauche] - tendu vers l'avant")
                    send('{ "Bras_D":"500", "Bras_D_1":"home", "Bras_D_2":"home" }')
                
            elif y_distance_epaule_coude < 0.02 and y_distance_coude_poignet > 0.05 :
                    print( "[Bras Gauche] - Popeye")
                    send('{ "Bras_D":"500", "Bras_D_1":"2000", "Bras_D_2":"1000" }')

        
        # ----------------------------------------
        if Bras_Gauche == "vers_le_haut" and Bras_Droit == "vers_le_haut":

            send('{ "Bouche_D": "0", "Bouche_G": "0" }')

        elif Bras_Gauche == "vers_le_bas" and Bras_Droit == "vers_le_bas":
            
            send('{ "Bouche_D": "home", "Bouche_G": "home" }')


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

                if TEST_MODE :
                    ret, local_img = cap.read()
            
                    if exists(PROCESSING_FLAG_FILE) :
                        local_img = video_processing(local_img)
                    
                    _, jpeg = cv2.imencode('.jpg', local_img)

                else :
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


                #sleep(1/30)

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

