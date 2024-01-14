## FLY THE TELLO WITH SIN WAVE ###
from djitellopy import Tello
import time
import math
import cv2

width = 800  # WIDTH OF THE IMAGE
height = 600 # HEIGHT OF THE IMAGE
tello = Tello()
tello.connect()

tello.streamoff()
tello.streamon()
tello.takeoff()   


duration = 15
start_time = time.time()
minx, miny = width, height
maxx, maxy = 0, 0

# print current battery percentage
print(tello.get_battery())
tello.move_up(50)

while time.time() - start_time < duration:
    current_time = time.time() - start_time
    frame = tello.get_frame_read().frame
    img = cv2.resize(frame, (width, height))
    cv2.imshow('frame', img)
    cv2.waitKey(1)
    tello.send_rc_control(0,0,0,50)

"""
while time.time() - start_time < duration:
    current_time = time.time() - start_time
    throttle_value = math.sin((current_time / period) * 2 * math.pi) * amplitude
    tello.send_rc_control(roll_speed, 0, int(throttle_value), 0)
    time.sleep(0.05)
"""

tello.land()
tello.streamoff()
tello.end()
