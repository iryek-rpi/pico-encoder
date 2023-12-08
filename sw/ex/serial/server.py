import os
import sys
import serial
import time

def main(port):
    ser = serial.Serial(port, 9600, timeout=1)
    print("Serial server waiting for connection on " + port)
    while True:
        data=ser.read(100)
        # convert bytestring  to unicode transformation format -8 bit
        #data_read = str(data).encode("utf-8")

        if data:
            response = bytes(f"<<<<< {data.decode('utf-8')}", 'utf-8')
            print(f"Serial server received data: {data.decode('utf-8')} and sending response: {response}")
            ser.write(response)
        time.sleep(0.1)


PORT = '/dev/ttyUSB0'
if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else PORT
    main(port)