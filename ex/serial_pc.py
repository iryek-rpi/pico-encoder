import os
import serial
import time


def init(port):
    ser = serial.Serial(port, 9600, timeout=1)
    return ser


def main():
    while True:
        # read two bytes of data
        data = ser.read(8)
        #data = ser.readline()
        # convert bytestring  to unicode transformation format -8 bit
        data_read = str(data).encode("utf-8")
        #print("Pico's Core Temperature : " + temperature + " Degree Celcius")
        print(f'data_read: {data_read}')
        time.sleep(0.2)
        ser.write(b'm1234567890')
        time.sleep(0.2)


if __name__ == "__main__":
    main()