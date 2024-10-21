import json
import os
import queue
import sys
import time
from multiprocessing import Manager, Process
from pathlib import Path
from typing import Optional
from picamera import PiCamera
import requests


sys.path.insert(1, "/home/pi/Desktop")


from Communication.android import Android, AndroidMessage
from Communication.stm import STM
from rpi_to_image_rec_server_task2 import capture_image


class Task2:
    def __init__(self):
        self.android = Android()
        self.stm = STM()

        self.speed = 10    #TODO 10cm/s



    def start(self):
        self.android.connect()
        print("Android processes successfully started")

        self.stm.connect()
        print("STM processes successfully started")
        picam = PiCamera()

        while True:
            message_rcv = self.android.receive()
            print("Message received:", message_rcv)
            if message_rcv == "START/PATH":                     #TODO START STRING HERE
                break
        distance1 = 0
        result = capture_image(picam, "http://192.168.29.15:5002/distance_one")
        while(result["path"]==[]):
            distance1 += 1
            self.stm.encode_to_stm("FW10")
            result = capture_image(picam, "http://192.168.29.15:5002/distance_one")
        print("First OBS", result)
        path = result["path"]
        distance1 += result["dist"]
        dir1 = result["dir1"]
        pathls = path.split()
        data = {"distance": distance1 , "dir1": dir1}

        for path in pathls:
            self.stm.encode_to_stm(path)
            
        distance2 = 0
        result = capture_image(picam, "http://192.168.29.15:5002/distance_three", data=data)
        while("Invalid" in result["error"]):
            distance2 += 1
            self.stm.encode_to_stm("FW10")
            result = capture_image(picam, "http://192.168.29.15:5002/distance_three", data=data)
        print("Second OBS", result)
        distance2 += result["length/dist"][0][1] / 100
        dir2 = result["dir2"]
        dist = result["length/dist"][0][1] / 100 - 2.4 - 0.5
        self.move_straight(dist)
        
        if dir2 == "L":                                #TODO TURN LEFT OR RIGHT, Should be in front of obstacle                                                          
            self.stm.encode_to_stm("FL90")
        else:
            self.stm.encode_to_stm("FR90")

        time1 = time.time()
        if dir1 == dir2: self.stm.encode_to_stm("BW49")                   #TODO IR SENSOR HERE, IF possible to get distance from stm would be btr
        time2 = time.time()
        
        duration = time2 - time1
        distance3 = duration * self.speed
        if dir2 != dir1:
            distance3 += 2.4 - 2.5                                 #This is the offset distance for first obstacle and radius of turn
        else:
            distance3 += 2.4 + 2.5
        
        self.stm.encode_to_stm("FW01")
        self.stm.encode_to_stm("WX01")
        
        if dir2 == "L":
            self.stm.encode_to_stm("FR90")
            self.stm.encode_to_stm("FR90")
        else:
            self.stm.encode_to_stm("FL90")
            self.stm.encode_to_stm("FL90")
            
        self.stm.encode_to_stm("FW01")
        self.stm.encode_to_stm("WX01")
        
        if dir2 == "L":
            self.stm.encode_to_stm("FR90")
            #self.stm.encode_to_stm("FR90")
        else:
            self.stm.encode_to_stm("FL90")
            #self.stm.encode_to_stm("FL90")
                                                            
        #TODO USE Dubins path here for slight optimization

        dist = distance2+1                #Should be at y axis above the carpark
        self.move_straight(dist)

        if dir2 == "L": self.stm.encode_to_stm("FR90")
        else: self.stm.encode_to_stm("FL90")
        
        self.stm.encode_to_stm("FW01")
        self.stm.encode_to_stm("WN01")
        self.stm.encode_to_stm("BW12")
        if dir2 == "L": self.stm.encode_to_stm("FL90")
        else: self.stm.encode_to_stm("FR90")
        dist = distance1 - 2.4 - 1
        self.move_straight(dist)

        #TODO edit this value or use ultrasonic to move into carpark
        requests.get("http://192.168.29.15:5002/stitch")
        status_msg = "FINISH|"
        self.android.send(status_msg)
        self.android.disconnect()

    def move_straight(self, dist: float) -> bool:
        mov_comm = ""
        if dist>0:
            while dist > 9:
                mov_comm += f"FW{round(9*10):0>2}\n"
                dist -= 9
            mov_comm += f'FW{round(dist*10):0>2}\n'
        else:
            dist = abs(dist)
            while dist > 9:
                mov_comm += f"BW{round(9*10):0>2}\n"
                dist -= 9
            mov_comm += f"BW{round(dist*10):0>2}\n"
        mov_comm = mov_comm.split()
        for comm in mov_comm:
            self.stm.encode_to_stm(comm)
        return True
    
if __name__ == "__main__":
    task2 = Task2()  # init
    task2.start()