import os
import sys
import serial
import time

def main(port):
    ser = serial.Serial(port, 9600, timeout=0.2)
    while True:
        values = input("Enter values to send:")
        print(f"Serial client sending data: {values} len(values): {len(values)}")
        ser.write(bytes(values, 'utf-8'))
        response = ''
        print("Serial client waiting for response")
        while not response:
            response = ser.read(100)
            if response:
                print(f"Serial client received data: response: {response}")

PORT = '/dev/ttyUSB0'
if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else PORT
    main(port)