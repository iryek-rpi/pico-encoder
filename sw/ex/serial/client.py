import os
import sys
import serial
import time

def main(port):
    ser = serial.Serial(port, 9600, timeout=1)
    while True:
        values = input("Enter values to send:")
        ser.write(bytes(values, 'utf-8'))
        response = ser.readline()
        print("Serial client received data: " + response.decode('utf-8'))

PORT = '/dev/ttyUSB0'
if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else PORT
    main(port)