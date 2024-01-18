#!/usr/bin/python3
# -----------------------------------------------------------------------------
#                                   TEST
#
#                                                           Fred J. 01/2024
# -----------------------------------------------------------------------------
import cv2
from picamera2 import Picamera2

import threading
import psutil
from http.server import BaseHTTPRequestHandler, HTTPServer

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()



# -----------------------------------------------------------------------------
def main():

    ip_list = get_network_interfaces()
    
    print("\n\n----------------------------------------")
    print(" Go to :")

    for ip in ip_list :
        print("http://"+ ip +":8000/video_feed")

    print("----------------------------------------\n\n")

    
    server_thread = threading.Thread(target=start_server)
    server_thread.start()


# -----------------------------------------------------------------------------
class VideoStreamHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == '/video_feed':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()

            while True:

                frame = picam2.capture_array()

                _, jpeg = cv2.imencode('.jpg', frame)
                frame = jpeg.tobytes()

                self.wfile.write(b'--frame\r\n')
                self.send_header('Content-type', 'image/jpeg')
                self.send_header('Content-length', len(frame))
                self.end_headers()
                self.wfile.write(frame)
                self.wfile.write(b'\r\n')


            cap.release()

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

