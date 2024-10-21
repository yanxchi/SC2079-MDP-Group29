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
from rpi_to_image_rec_server_task2 import capture_image

class main2:
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
        #self.process_receive_stm = Process(target=self.receive_stm)

        self.process_android_receive.start()  # Receive from android
        #self.process_receive_stm.start()  # Receive from stm
          
    def android_receive(self) -> None:
        while True:
            message_rcv: Optional[str] = None
            try:
                message_start = self.android.receive()
                while message_start == 'START/PATH':
                    picam = PiCamera()
                    result = capture_image(picam, "http://192.168.29.15:5002/distance_one")
                    distance1 = 0
                    while(result["path"]==[]):
                        distance1 += 1
                        self.stm.encode_to_stm("FW10")
                        result = capture_image(picam, "http://192.168.29.15:5002/distance_one")
        
                    result, distance, dir1 = result["path"], result["dist"], result["dir1"]
                    data = {"distance": distance + distance1, "dir1": dir1}
                    print(result)
                    result_ls = result.split()
                    for m_comm in result_ls:
                        self.stm.encode_to_stm(m_comm)
                            
                    result = capture_image(picam, "http://192.168.29.15:5002/distance_three", data=data)
                    
    
                    while("Invalid" in result["error"]):
                        data["distance"] += 1
                        self.stm.encode_to_stm("FW10")
                        result = capture_image(picam, "http://192.168.29.15:5002/distance_three", data=data)
                    result = result["path"]
                    print(result)
                    for i in range(len(result)):
                        mov_comm = result[i]
                        print(mov_comm)
                        list_mov_comm = mov_comm.split()
                        for m_comm in list_mov_comm:
                            self.stm.encode_to_stm(m_comm)
                    self.stm.encode_to_stm("FW10")
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
    main_2 = main2()  # init
    main_2.start()