# from Communication.link import Link
# from Communication.configuration import SERIAL_PORT, BAUD_RATE
import sys
from pathlib import Path
from typing import Optional
import time

import serial

class STM:

    def __init__(self):
        """
        Constructor for STMLink
        """
        super().__init__()
        self.serial = None
        self.received = []

    def connect(self):
        """Connect to STM32 using serial UART connection, given the serial port and the baud rate"""
        self.serial = serial.Serial(
                "/dev/ttyUSB0",
                baudrate=115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=None,)
        print("Connected to STM32")

    def disconnect(self):
        """Disconnect from STM32 by closing the serial link that was opened during connect()"""
        self.serial.close()
        self.serial = None
        print("Disconnected from STM32")

    def wait_receive(self, ticks=5000) -> Optional[str]:
        """Receive a message from STM32, utf-8 decoded

        Returns:
            Optional[str]: message received
        """
        while True:
            if self.serial.in_waiting > 0:
                return str(self.serial.read_all(), "utf-8")
        
    def encode_to_stm(self, message):
        self.serial.write(message.encode())
        print(f"Attempted to add to STM:{message}")
        print(f"{message.encode()}")
        
        # Wait for an acknowledgment from the STM32
        response = self.serial.read_until('|'.encode('utf-8'))
        print(f"Received from STM: {response}\n")  # Add this line for debugging
        
