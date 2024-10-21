import json
import os
import queue
import sys
import time
import requests
from multiprocessing import Manager, Process
from pathlib import Path
from typing import Optional
from picamera import PiCamera
import io

sys.path.insert(1, "/home/pi/Desktop")

from Communication.android import Android, AndroidMessage
from Communication.stm import STM
from rpi_to_image_rec_server_task1 import capture_image

class Task_1:
    def __init__(self):
        self.android = Android()
        self.stm = STM()
        self.manager = Manager()

        self.android_dropped = self.manager.Event()
        self.unpause = self.manager.Event()

        self.movement_lock = self.manager.Lock()

        self.process_android_receive = None
        
    def start(self):
        self.android.connect()
        print("Android processes successfully started")

        self.stm.connect()
        print("STM processes successfully started")
        
        self.process_android_receive = Process(target=self.android_receive)

        self.process_android_receive.start()  # Receive from android
        
        
    def android_receive(self) -> None:
        while True:
            message_rcv: Optional[str] = None
            try:
                message_rcv = self.android.receive()
                print("Message received:", message_rcv)
                list1 = eval(message_rcv)
                body = {}
                body['targets'] = list1
                out = requests.get("http://192.168.29.15:5002/path", json = body)
                print (out.json())
                print ('Checking Status')
                status_msg = 'STATUS/READY|'
                self.android.send(status_msg)
                message_start = self.android.receive()
                while message_start == 'START/PATH':
                    picam = PiCamera()
                    for i in range(len(out.json()["paths"])):
                        mov_comm = out.json()["paths"][i]['stm']
                        print(mov_comm)
                        android_loc = out.json()["paths"][i]['android']
                        obstacle_id = out.json()["paths"][i]['target']
                        android_msg = 'PATH/' + android_loc + '|'
                        msg = 'TOWARDS/' + str(obstacle_id) + '|'
                        self.android.send(msg)
                        self.android.send(android_msg)
                        list_mov_comm = mov_comm.split()
                        for j in range(len(list_mov_comm)):
                            self.stm.encode_to_stm(list_mov_comm[j])
                        time.sleep(1)
                        self.android.send('STATUS/RECOGNIZING|')
                        result = capture_image(picam)
                        image_id = result.split(':')[0]
                        result_msg = 'TARGET/' + str(obstacle_id) + '/' + str(image_id)+'|'
                        self.android.send(result_msg)
                        print (result)
                    break
                requests.get("http://192.168.29.15:5002/stitch")
                self.android.send('FINISH|')
                self.android.disconnect()

            except OSError:
                self.android_dropped.set()
                print("Event set: Bluetooth connection dropped")

            if message_rcv is None:
                continue
        return message_rcv

if __name__ == "__main__":
    Task1 = Task_1()  # init
    Task1.start()