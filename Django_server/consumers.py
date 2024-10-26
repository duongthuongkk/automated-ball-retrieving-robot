import cv2, os
import asyncio
import RPi.GPIO as GPIO
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import base64
from send_vid import rasp_ThuHoiBanh
import random
import time


class VideoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.cap = cv2.VideoCapture(0)
        self.send_video_task = None
        self.prev_frame_time = time.time()
        self.fps = 0
        self.balls_count = 0
        self.frame_count = 0
        self.demtime = 0
        self.enableFind = None
        self.status = 'idle'
        data = {
                'frame': '',
                'fps': self.fps,
                'balls_count': self.balls_count,
                'status': self.status
                }
        await self.send(text_data=json.dumps(data))
    async def disconnect(self, close_code):
        if self.send_video_task:
            self.send_video_task.cancel()
            try:
                await self.send_video_task
            except asyncio.CancelledError:
                pass
        self.cap.release()
        GPIO.cleanup()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')

        if message == 'start':
            if not self.send_video_task:
                if self.status == 'idle':
                    if message== 'hand':
                        self.status = 'manual'
                    elif message!= 'hand':
                        self.status = 'automatic'
                elif self.status == 'stop':
                    if message== 'hand':
                        self.status = 'manual'
                    else:
                        self.status = 'automatic'
                self.send_video_task = asyncio.create_task(self.send_video_frame())
                
        elif message == 'stop':
            # Kill the process
            if self.status == 'stop':
                if message == 'stop':
                    os.system("kill -9 $(ps -aux | grep start_server | awk '{print $2}')")
            else:
                self.status = 'stop'
                data = {
                        'frame': '',
                        'fps': self.fps,
                        'balls_count': self.balls_count,
                        'status': self.status
                    }
                await self.send(text_data=json.dumps(data))
                if self.send_video_task:
                    self.send_video_task.cancel()
                    try:
                        await self.send_video_task
                    except asyncio.CancelledError:
                        pass
                    self.send_video_task = None


        elif message == 'forward':
            rasp_ThuHoiBanh.forward(100)
            print("The system is forward")
            await asyncio.sleep(0.1)
            rasp_ThuHoiBanh.stop()
        elif message == 'backward':
            rasp_ThuHoiBanh.backward(100)
            print("The system is backward")
            await asyncio.sleep(0.1)
            rasp_ThuHoiBanh.stop()
        elif message == 'turnleft':
            rasp_ThuHoiBanh.left(20)
            print("The system is turn left")
            await asyncio.sleep(0.15)
            rasp_ThuHoiBanh.stop()
        elif message == 'turnright':
            rasp_ThuHoiBanh.right(20)
            print("The system is turn right")
            await asyncio.sleep(0.1)
            rasp_ThuHoiBanh.stop()
        elif message == 'pickball':
            await rasp_ThuHoiBanh.pickball()
            print("The system is picking ball")
            self.balls_count += 1
            await asyncio.sleep(0.15)
            rasp_ThuHoiBanh.stop()
        elif message == 'hand':
            self.status = 'manual'
        elif message == 'auto':
            self.status = 'automatic'
            self.enableFind = 1
            self.demtime = 0
    async def send_video_frame(self):
        try:
            while True:
                ball_count = 0
                ret, frame = self.cap.read()
                if not ret:
                    print("Frame failed")
                    break
                if self.status == 'automatic':
                    frame, ball_count, self.demtime, self.enableFind  = await rasp_ThuHoiBanh.pick_ball(frame,self.demtime)
                    print("Task cho banh", self.demtime,self.enableFind, self.status)
                    if self.enableFind == 1:
                        if self.demtime >= 100:
                            print("Start rotate")
                            print(self.demtime)
                            rasp_ThuHoiBanh.right(5)
                            if self.demtime >= 300:
                                rasp_ThuHoiBanh.stop()
                                self.demtime = 0
                                self.enableFind = 0
                                self.status = "idle"
                                continue
                        else:
                            rasp_ThuHoiBanh.stop()
                # Tính toán fps
                new_frame_time = time.time()
                self.fps = 1 / (new_frame_time - self.prev_frame_time)
                self.prev_frame_time = new_frame_time

                # Tính số lượng bóng
                self.balls_count = self.balls_count + ball_count
                # Mã hóa khung hình thành JPEG
                _, buffer = cv2.imencode('.jpg', frame)
                frame_base64 = base64.b64encode(buffer).decode('utf-8')

                # Tạo một dictionary chứa dữ liệu
                data = {
                    'frame': frame_base64,
                    'fps': self.fps,
                    'balls_count': self.balls_count,
                    'status': self.status
                }
                await self.send(text_data=json.dumps(data))
                await asyncio.sleep(1.0 / 25)  # Điều chỉnh tốc độ khung hình
        except KeyboardInterrupt:
            GPIO.cleanup()
            self.cap.release()

    
