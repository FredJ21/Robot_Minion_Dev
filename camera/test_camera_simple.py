#!/usr/bin/python3
# -----------------------------------------------------------------------------
#                                   TEST
#
#                                                           Fred J. 01/2024
# -----------------------------------------------------------------------------
import cv2
from picamera2 import Picamera2


picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()




print("--GO--")
a=0


while True:

    print(a)


    im = picam2.capture_array()

    cv2.imshow("Camera", im)
    cv2.waitKey(1)

    if cv2.waitKey(1) & 0xFF == ord('q'): break

    
    a += 1






