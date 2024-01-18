#!/home/pi/MINION/venv/bin/python
# -----------------------------------------------------------------------------
#                                   TEST
#   ce script ne fonctionne que dans l'environnement graphique de la RPI
#
#                                                           Fred J. 01/2024
# -----------------------------------------------------------------------------
import cv2
from picamera2 import Picamera2

import mediapipe as mp

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


# --------------------


print("--GO--")
print("cv2 version : ", cv2.__version__)


while True:


    img = picam2.capture_array()
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    # Mediapipe
    results = pose.process(img)


    if results.pose_landmarks :

        print(results.pose_landmarks)

        mp_drawing.draw_landmarks(
            img,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())





    cv2.imshow("Camera", img)
    cv2.waitKey(1)

    if cv2.waitKey(1) & 0xFF == ord('q'): break

    






