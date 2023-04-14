# Importing necessary libraries
import cv2 as cv
import time
import numpy as np
import HandTrackingModule as htm   # Hand tracking module in a separate file
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math

# Setting camera width and height
widthCam, heightCam = 1280, 720

# Starting the video capture from the camera
cap = cv.VideoCapture(0)
cap.set(3, widthCam)
cap.set(4, heightCam)

# Initializing the previous time for calculating FPS
prevTime = 0

# Initializing a hand detector object
detector = htm.HandDetector(detectionConfidence=0.7)

# Getting the current audio devices and activating the endpoint volume interface
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)

# Casting the interface as an IAudioEndpointVolume object
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Getting the range of the volume levels
volRange = volume.GetVolumeRange()

# Setting the minimum and maximum volume levels
minVol = volRange[0]
maxVol = volRange[1]

# Initializing the current volume, volume bar, and volume percentage
vol = 0
volBar = 400
volPer = 0

# Starting an infinite loop for capturing video frames and detecting hand gestures
while True:
    # Capturing a frame from the camera
    success, img = cap.read()

    # Using the hand detector to find hands in the frame and their landmark positions
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    # If landmarks are found, calculate the position of the hand and update the volume accordingly
    if len(lmList) != 0:
        # Finding the positions of the index and middle fingertips and the center of the line connecting them
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2)//2, (y1 + y2)//2

        # Drawing circles at the index and middle fingertip positions and the center point
        cv.circle(img, (x1, y1), 10, (0, 255, 0), -1)
        cv.circle(img, (x2, y2), 10, (0, 255, 0), -1)
        cv.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
        cv.circle(img, (cx, cy), 10, (0, 255, 0), -1)

        # Calculating the length of the line connecting the index and middle fingertips
        length = math.hypot(x2 - x1, y2 - y1)
        print(length)

        # Interpolating the length to get the corresponding volume level, volume bar, and volume percentage
        vol = np.interp(length, [50, 215], [minVol, maxVol])
        volBar = np.interp(length, [50, 215], [400, 150])
        volPer = np.interp(length, [100, 215], [0, 100])
        print(vol)

        # Setting the volume to the calculated level
        volume.SetMasterVolumeLevel(vol, None)

        #If the distance between the tips of the index and middle finger is less than 50, display a purple circle at the center of the two fingers
        if length < 50:
            cv.circle(img, (cx, cy), 10, (255, 0, 255), -1)

        #Draw a green rectangle to represent the maximum volume range and another green rectangle to represent the current volume range, based on the interpolated value
        cv.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
        cv.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), -1)
        #Display the current volume percentage on the screen using OpenCV putText function
        cv.putText(img, f'{int(volPer)}%', (40, 450), cv.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

    #Calculate the FPS and display it on the screen using OpenCV putText function
    currentTime = time.time()
    fps = 1/(currentTime - prevTime)
    prevTime = currentTime
    cv.putText(img, f'FPS: {int(fps)}', (40, 50), cv.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

    #Display the image on the screen using OpenCV imshow function and wait for a key event
    cv.imshow('img', img)
    cv.waitKey(1)