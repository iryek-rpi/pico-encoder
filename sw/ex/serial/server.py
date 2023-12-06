import os
import sys
import serial
import time

def main(port):
    ser = serial.Serial(port, 9600, timeout=1)
    while True:
        print("Serial server waiting for connection on " + PORT)
        data=ser.readline()
        print("Serial server received data: " + data)
        # convert bytestring  to unicode transformation format -8 bit
        #data_read = str(data).encode("utf-8")

        ser.write(bytes(f"<<<<< {data}", 'utf-8'))
        time.sleep(0.1)


PORT = '/dev/ttyUSB0'
if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else PORT
    main(port)