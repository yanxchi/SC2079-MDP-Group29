import json
import os
import queue
import sys
import time
from pathlib import Path
from typing import Optional
import time

sys.path.insert(1, "/home/pi/Desktop")

from Communication.stm import STM

class STMConnectionTest:

    def __init__(self):
        self.stm = STM()
        
    def stm_main(self):
        try:
            self.stm.connect()
            print("STM processes successfully started")
             
            user_input = 0

            while user_input < 3:
                user_input = int(input("1: Send a message, 2: Exit"))
                if user_input == 1:
                    try:
                        action_type = input("Type of action:")
                        
                        print("Message received:", action_type)

                        if action_type == "f":
                            self.stm.encode_to_stm('FW90')
                        elif action_type == "b":
                            self.stm.encode_to_stm('BW90')
                        elif action_type == "fr":
                            self.stm.encode_to_stm('FR90')
                        elif action_type == "fl":
                            self.stm.encode_to_stm('FL90')                            
                        elif action_type == "bl":
                            self.stm.encode_to_stm('BL90')
                        elif action_type == "br":
                            self.stm.encode_to_stm('BR90')
                        elif action_type == "us":
                            self.stm.encode_to_stm('DT15')
                        elif action_type == "ir":
                            self.stm.encode_to_stm('WX01')
                        elif action_type == "iir":
                            self.stm.encode_to_stm('WN01')
                        elif action_type is None:
                            continue
                        else:
                            self.stm.encode_to_stm(action_type)
                    except OSError:
                        print("Connection Dropped")
                else:
                    break
        except:
            # End the connection
            print("DISCONNECTION HAPPENED")
            
    def receive_stm(self) -> None:
        while True:
            message_rcv = self.stm.wait_receive()
            print(message_rcv)
            if message_rcv[0] == "f":
                print("message received:", message_rcv)
                # Finished command, send to android
                message_split = message_rcv[1:].split(
                    "|"
                )  # Ignore the 'f' at the start

                for m in message_split:
                    print(m)

                cmd_speed = message_split[0]
                turning_degree = message_split[1]
                distance = message_split[2].strip()

                cmd = cmd_speed[0]  # Command (t/T)
                speed = cmd_speed[1:]

                print("Cmd = " + cmd)
                print("Turning degree = " + turning_degree)
                print("Distance = " + distance)

                if turning_degree == "-25":
                    # Turn left
                    if "t" in cmd:
                        # Backward left
                        msg = "TURN,BACKWARD_LEFT,0"
                    elif "T" in cmd:
                        # Forward left
                        msg = "TURN,FORWARD_LEFT,0"
                elif turning_degree == "25":
                    # Turn right
                    if "t" in cmd:
                        # Backward right
                        msg = "TURN,BACKWARD_RIGHT,0"
                    elif "T" in cmd:
                        # Forward right
                        msg = "TURN,FORWARD_RIGHT,0"
                elif turning_degree == "0":
                    if "t" in cmd:
                        # Backward
                        msg = "MOVE,BACKWARD," + distance
                    elif "T" in cmd:
                        # Forward
                        msg = "MOVE,FORWARD," + distance
                else:
                    # Unknown turning degree
                    print("Unknown turning degree")
                    msg = "No instruction"

                print("Msg: ", msg)
            
if __name__ == "__main__":
    testingSTM = STMConnectionTest()  # init
    testingSTM.stm_main()