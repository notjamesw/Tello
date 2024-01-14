## FLY THE TELLO WITH SIN WAVE ###
from djitellopy import Tello
import time
import math

tello = Tello()
tello.connect()

tello.streamoff()
tello.streamon()
tello.takeoff()

roll_speed = 15  
amplitude = 60  
period = 5     
duration = 15   

start_time = time.time()

while time.time() - start_time < duration:
    current_time = time.time() - start_time
    throttle_value = math.sin((current_time / period) * 2 * math.pi) * amplitude
    tello.send_rc_control(roll_speed, 0, int(throttle_value), 0)
    time.sleep(0.05)

tello.land()
tello.end()