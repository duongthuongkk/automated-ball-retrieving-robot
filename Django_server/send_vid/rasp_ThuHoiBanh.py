import cv2
import imutils
import RPi.GPIO as GPIO
import time
import asyncio

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
#Khai bao chan L298
GPIO.setup(5,GPIO.OUT)
GPIO.setup(6,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)

GPIO.setup(16,GPIO.OUT)
GPIO.setup(26,GPIO.OUT)
GPIO.setup(12,GPIO.OUT)

pwm_left=GPIO.PWM(13,1000)
pwm_right=GPIO.PWM(12,1000)
pwm_left.start(0)
pwm_right.start(0)
#Khai bao chan cam bien hong ngoai
GPIO.setup(17,GPIO.IN)

#khai bao chan servo
servoPIN = 22
GPIO.setup(servoPIN, GPIO.OUT)
p = GPIO.PWM(servoPIN, 50) # GPIO 22 for PWM with 50Hz
p.start(4.5)

greenLower = (30, 130, 100)
greenUpper = (180, 255, 255)
demtime = 0
enableFind = 1
def forward(speed):
    pwm_left.ChangeDutyCycle(speed)
    GPIO.output(5,GPIO.HIGH)
    GPIO.output(6,GPIO.LOW)
    
    pwm_right.ChangeDutyCycle(speed)
    GPIO.output(26,GPIO.HIGH)
    GPIO.output(16,GPIO.LOW)
    print("forward")

def backward(speed):
    pwm_left.ChangeDutyCycle(speed)
    GPIO.output(5,GPIO.LOW)
    GPIO.output(6,GPIO.HIGH)
    
    pwm_right.ChangeDutyCycle(speed)
    GPIO.output(26,GPIO.LOW)
    GPIO.output(16,GPIO.HIGH)
    print("backward")

def left(speed):
    pwm_left.ChangeDutyCycle(speed)
    GPIO.output(5,GPIO.HIGH)
    GPIO.output(6,GPIO.LOW)
    
    pwm_right.ChangeDutyCycle(speed)
    GPIO.output(26,GPIO.LOW)
    GPIO.output(16,GPIO.HIGH)
    print("left")
def right(speed):
    pwm_left.ChangeDutyCycle(speed)
    GPIO.output(5,GPIO.LOW)
    GPIO.output(6,GPIO.HIGH)
    
    pwm_right.ChangeDutyCycle(speed)
    GPIO.output(26,GPIO.HIGH)
    GPIO.output(16,GPIO.LOW)
    print("right")
def stop():
    pwm_left.ChangeDutyCycle(0)
    GPIO.output(5,GPIO.LOW)
    GPIO.output(6,GPIO.LOW)
    
    pwm_right.ChangeDutyCycle(0)
    GPIO.output(16,GPIO.LOW)
    GPIO.output(26,GPIO.LOW)

async def pickball():
    stop()
    print("Pick ball")
    p.ChangeDutyCycle(11.5)
    await asyncio.sleep(0.5)
    p.ChangeDutyCycle(4.5)
    await asyncio.sleep(0.5)

async def pick_ball(frame,prev_demtime):
    ball_count = 0
    global enableFind
    demtime = prev_demtime
    frame = imutils.resize(frame, width=300)
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
    if GPIO.input(17) == 0:
        ball_count += 1
        await pickball()
        enableFind = 1
    print("Demtime: ",demtime, enableFind)
    if enableFind == 1:
        demtime += 1
    return frame, ball_count, demtime, enableFind
