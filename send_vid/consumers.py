import cv2
import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import base64
from send_vid import rasp_ThuHoiBanh
import random
import time

class VideoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.cap = cv2.VideoCapture("C:\\Users\\ADMIN\\Desktop\\robot_server\\webserver\\video_test.mp4")
        self.send_video_task = None
        self.prev_frame_time = time.time()
        self.fps = 0
        self.balls_count = 0
        self.frame_count = 0
        self.status = 'idle'
        self.appflag = None
        data = {
                'frame': "",
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
        self.appflag = False

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        print(message)
        if message == 'app':
            self.appflag = True
            print("App connects successfully!")
            print (self.appflag)
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
            if self.appflag == True:
                self.send_video_task = asyncio.create_task(self.send_video_frame())
        elif message == 'stop':
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
        elif message == 'backward':
            rasp_ThuHoiBanh.backward(100)
            print("The system is backward")
        elif message == 'turnleft':
            rasp_ThuHoiBanh.left(5)
            print("The system is turn left")
        elif message == 'turnright':
            rasp_ThuHoiBanh.right(5)
            print("The system is turn right")
        elif message == 'pickball':
            print("The system is picking ball")
        elif message == 'hand':
            self.status = 'manual'
        elif message == 'auto':
            self.status = 'automatic'

    async def send_video_frame(self):
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                frame = rasp_ThuHoiBanh.pick_ball(frame)

                # Tính toán fps
                new_frame_time = time.time()
                self.fps = 1 / (new_frame_time - self.prev_frame_time)
                self.prev_frame_time = new_frame_time

                # Tính số lượng bóng
                self.balls_count = random.randint(0, 10)
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
                await asyncio.sleep(1.0 / 30)  # Điều chỉnh tốc độ khung hình
        except asyncio.CancelledError:
            pass
