#!/usr/bin/python3
#------------------------------------------------------------------------------
#
#
#	pip3 install opencv-python
#	apt-get install libatlas-base-dev
#------------------------------------------------------------------------------

import cv2
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer




class VideoStreamHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        A = 0

        if self.path == '/video_feed':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()

            cap = cv2.VideoCapture(0)
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                _, jpeg = cv2.imencode('.jpg', frame)
                frame = jpeg.tobytes()

                self.wfile.write(b'--frame\r\n')
                self.send_header('Content-type', 'image/jpeg')
                self.send_header('Content-length', len(frame))
                self.end_headers()
                self.wfile.write(frame)
                self.wfile.write(b'\r\n')

                print(A)
                A += 1

            cap.release()

        else:
            self.send_response(404)
            self.end_headers()

def start_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, VideoStreamHandler)
    httpd.serve_forever()


print("http://localhost:8000/video_feed")

# D?marrer le serveur dans un thread s?par?
server_thread = threading.Thread(target=start_server)
server_thread.start()

