## FLY THE TELLO 360 VIDEO STREAMING
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

# print current battery percentage
print(tello.get_battery())
print(tello.get_height())

tello.move_up(50)

startYaw = tello.get_yaw()
print(startYaw)

while True:
    frame = tello.get_frame_read().frame
    img = cv2.resize(frame, (width, height))
    cv2.imshow('frame', img)
    cv2.waitKey(1)
    tello.send_rc_control(0,0,0,20)
    print(tello.get_yaw())
    time.waitKey(0.05)
    if tello.get_yaw() == startYaw :
        break

tello.land()
tello.streamoff()
tello.end()
