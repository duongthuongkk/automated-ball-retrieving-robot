import cv2
import imutils

#Khai bao chan cam bien hong ngoai

#khai bao chan servo
servoPIN = 22

greenLower = (30, 130, 100)
greenUpper = (180, 255, 255)
demtime = 0
enableFind = 1
def forward(speed):
    print("forward")
def backward(speed):
    print("backward")
def left(speed):
    print("left")
def right(speed):
    
    print("right")
def stop():
    print("stop")
  
def pick_ball(frame):
    frame = imutils.resize(frame, width=500)

    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
    for c in cnts: 
        if cv2.contourArea(c) > 300:
            enableFind = 0
            demtime = 0
            print(cv2.contourArea(c))
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            
            if y>140:
                forward(100)
                break
            if x <= 200 and x >= 100:
                forward(50)
            elif x > 200:
                right(5)
            else:
                left(5)
            
            cv2.putText(frame,"x:{}  y:{} ".format(int(x),int(y)), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.putText(frame,"R:{} ".format(int(radius)), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
        else:
            stop()
            enableFind = 1
    return frame