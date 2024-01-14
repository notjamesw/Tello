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

r = 55

## x-z circle

# x1, y1, z1, x2, y2, z2 = 0, r, r, 0, 2*r, 0

print(tello.get_height())

# tello.curve_xyz_speed(x1, y1, z1, x2, y2, z2, 20)
tello.curve_xyz_speed(0, 11, 33, 0, 110, 0, 20)


"""   
tello.curve_xyz_speed(0, 20, 60, 0, 180, 60, 20)
tello.curve_xyz_speed(0, -20, -60, 0, -180, -60, 20)
"""
print(tello.get_height())
tello.land()
tello.end()