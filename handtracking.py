import cv2
import mediapipe as mp
from djitellopy import Tello
import threading
from time import sleep
import time
import numpy as np
import logging

range = [7000, 9000]
pLrError = 0
pFbError = 0
pUdError = 0
pSpeedError = 0

pidSpeed = [0.4, 0.4, 0]
pid = [0.1, 0.1, 0]
width = 800  # WIDTH OF THE IMAGE
height = 600 # HEIGHT OF THE IMAGE
last_action_time = time.time()
flip_interval = 3
gesture_mode = ""

def handle_input(tello):
    while True:
        command = input("Enter command: ")
        if command == "take off":
            tello.takeoff()
        elif command.startswith("forward"):
            distance = int(command.split()[1])
            tello.move_forward(distance)
        elif command.startswith("back"):
            distance = int(command.split()[1])
            tello.move_back(distance)
        elif command.startswith("left"):
            distance = int(command.split()[1])
            tello.move_left(distance)
        elif command.startswith("right"):
            distance = int(command.split()[1])
            tello.move_right(distance)
        elif command.startswith("up"):
            distance = int(command.split()[1])
            tello.move_up(distance)
        elif command.startswith("down"):
            distance = int(command.split()[1])
            tello.move_down(distance)
        elif command.startswith("cw"):
            angle = int(command.split()[1])
            tello.rotate_clockwise(angle)
        elif command.startswith("ccw"):
            angle = int(command.split()[1])
            tello.rotate_counter_clockwise(angle)
        elif command == "flip forward":
            tello.flip_forward()
        elif command == "flip back":
            tello.flip_back()
        elif command == "flip left":
            tello.flip_left()
        elif command == "flip right":
            tello.flip_right()
        elif command == "stop":
            tello.stop()
        elif command == "circle":
            start_height = tello.get_height()
            circle(tello, start_height)
        elif command == "land":
            tello.land()
            break
        else:
            print("Invalid command")
        print(tello.get_battery())

def circle(tello, start_height):
    tello.send_rc_control(0,0,0,0)
    sleep(0.1)
    
    v_up = 0
    for _ in range(4):
        tello.send_rc_control(40, -5, v_up, -35)
        sleep(13)
        height = tello.get_height() - start_height
        if height > 0:
            tello.move_down(height)
        elif height < 0:
            tello.move_up(-height)
        tello.send_rc_control(0,0,0,0)
        sleep(1)
    return 0

def trackHand(test, handsMidPoint, handsListArea, pid, pidSpeed):
    global pSpeedError, pFbError, pUdError
    maxArea = max(handsListArea)
    x, y = handsMidPoint[0]
    speedError = x - width // 2
    udError = y - height//2
    fbError = maxArea - (range[0] + range[1]) // 2
    fb, ud, speed = 0, 0, 0
    
    if speedError != 0:
        speed = pidSpeed[0] * speedError + pidSpeed[1] * (speedError - pSpeedError)
        speed = int(np.clip(speed, -30, 30))
    else:
        speed = 0

    if udError != 0:
        ud = pid[0] * udError + pid[1] * (udError - pUdError)
        ud = int(np.clip(ud, -30, 30))
    else:
        ud = 0
        
    if maxArea > range[0] and maxArea < range[1]:
        fb = 0
    elif maxArea > range[1]:
        fb = pid[0] * pid[0] * pidSpeed[0] * fbError + pid[1] * pid[1] * pidSpeed[1] * (fbError - pFbError)
        fb = int(np.clip(fb, -30, 30))
    elif maxArea < range[0] and maxArea != 0:
        fb = pid[0] * pid[0] * pidSpeed[0] * fbError + pid[1] * pid[1] * pidSpeed[1] * (fbError - pFbError)
        fb = int(np.clip(fb, -30, 30))
    else:
        fb = 0

    test.send_rc_control(0, -fb, -ud, speed)
    
    return pSpeedError, pFbError, pUdError

def gestureDirection(hand_landmarks):
    thumb_tip = hand_landmarks[4]
    thumb_mcp = hand_landmarks[2]
    wrist = hand_landmarks[0]
    index_tip = hand_landmarks[8]
    index_pip = hand_landmarks[6]
    middle_tip = hand_landmarks[12]
    middle_pip = hand_landmarks[10]

    if thumb_tip.y < thumb_mcp.y and thumb_mcp.y < middle_tip.y:
        if index_tip.x > index_pip.x and middle_tip.x > middle_pip.x:
            return "ThumbUp"
        elif index_tip.x < index_pip.x and middle_tip.x < middle_pip.x:
            return "ThumbUp"
    elif thumb_tip.y > thumb_mcp.y and thumb_mcp.y > middle_tip.y:
        if index_tip.x < index_pip.x and middle_tip.x < middle_pip.x:
            return "ThumbDown"
        elif index_tip.x > index_pip.x and middle_tip.x > middle_pip.x:
            return "ThumbDown"
    elif index_tip.y < index_pip.y and middle_tip.y > middle_pip.y:
        return "Top"
    elif index_tip.y > index_pip.y and middle_tip.y < middle_pip.y:
        return "Bottom"
    elif index_tip.x < index_pip.x and middle_tip.x > middle_pip.x:
        return "Left"
    elif index_tip.x > index_pip.x and middle_tip.x < middle_pip.x:
        return "Right"
    else:
        return "None"
    
def main():
    global last_action_time
    global gesture_mode
    test = Tello()
    test.connect()
    test.for_back_velocity = 0
    test.left_right_velocity = 0
    test.up_down_velocity = 0
    test.yaw_velocity = 0
    test.speed = 0
    print(test.get_battery())

    test.streamoff()
    test.streamon()
    test.takeoff()

    mpHands = mp.solutions.hands
    hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.6)
    mpDraw = mp.solutions.drawing_utils
    
    while True:
        if test.get_battery() < 20:
            print("Battery low, Battery level: " + str(test.get_battery()))
        frame_read = test.get_frame_read()
        myFrame = frame_read.frame
        img = cv2.resize(myFrame, (width, height))
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)
        imgHeight, imgWidth, imgChannels = img.shape
        minx, miny = width, height
        maxx, maxy = 0, 0
        if results.multi_hand_landmarks:
            handsListArea = []
            handsMidPoint = []
            lrPoints = []
            gesture = ""
            for handLms in results.multi_hand_landmarks:
                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
                gesture = gestureDirection(handLms.landmark)
                for id, lm in enumerate(handLms.landmark):
                    xPos = int(lm.x * imgWidth)
                    yPos = int(lm.y * imgHeight)
                    minx = min(minx, xPos)
                    miny = min(miny, yPos)
                    maxx = max(maxx, xPos)
                    maxy = max(maxy, yPos)
                    if id == 9:
                        handsMidPoint.append((xPos, yPos))
            cv2.rectangle(img, (minx, miny), (maxx, maxy), (0, 0, 255), 2)
            handsListArea.append((maxx - minx) * (maxy - miny))
            if len(handsListArea) > 0:
                current_time = time.time()
                if gesture_mode == "Flip" and current_time - last_action_time > flip_interval:
                    if gesture == "Top":
                        test.flip_forward()
                    elif gesture == "Bottom":
                        test.flip_back()
                    elif gesture == "Left":
                        test.flip_left()
                    elif gesture == "Right":
                        test.flip_right()
                    last_action_time = current_time
                elif gesture_mode == "Track":
                    trackHand(test, handsMidPoint, handsListArea, pid, pidSpeed)
                else:
                    test.send_rc_control(0,0,0,0)
                
                if gesture == "ThumbUp":
                    print("Track Start")
                    gesture_mode = "Track"
                elif gesture == "ThumbDown":
                    print("Flip Start")
                    gesture_mode = "Flip"
            else:
                test.send_rc_control(0,0,0,0)
        else:
            test.send_rc_control(0,0,0,0)
        cv2.imshow("Image", img)

        if cv2.waitKey(1) == ord('q'):
            test.land()
            break


if __name__ == "__main__":
    main()