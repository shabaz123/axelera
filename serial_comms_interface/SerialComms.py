# Python module for sending messages to a serial port
# requirement: pip install pyserial
# rev 1 - shabaz - July 2025

import serial  # Note: this is the pyserial module, NOT the serial module
import sys
import time
import argparse
from serial.tools import list_ports

port_search_term = 'USB0'  # example: USB0 represents /dev/ttyUSB0
baudrate = 115200

class SerialComms:
    def __init__(self):
        self.port = None
        ports = list_ports.comports()
        for port_candidate in ports:
            if port_search_term in port_candidate.description or f'tty{port_search_term}' in port_candidate.device:
                self.port = port_candidate.device
        if not self.port:
            raise RuntimeError(f"No serial port /dev/tty{port_search_term} exists.")


    def send(self, message):
        try:
            with serial.Serial(self.port, baudrate=baudrate, timeout=1) as ser:
                # send message with '\r' at the end
                for char in message:
                    ser.write(char.encode('utf-8'))
                    time.sleep(0.01)
                ser.write(b'\r')
        except serial.SerialException as e:
            raise RuntimeError(f"send error: {e}")

def SerialCommsMain():
    parser = argparse.ArgumentParser(description='Send a message to a serial port.')
    parser.add_argument('message', type=str, help='The message to send')
    args = parser.parse_args()
    serial_comms = SerialComms()
    serial_comms.send(args.message)

if __name__ == '__main__':
    SerialCommsMain()
