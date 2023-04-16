import os
import serial
import time


def init(port):
    ser = serial.Serial(port, 9600, timeout=1)
    return ser


def main():
    # read two bytes of data
    ser = init('/dev/ttyUSB0')
    while True:
        print("Sending data to Pico: 1234567890")
        ser.write(b'1234567890')
        #data = ser.read(8)
        #data = ser.readline()
        # convert bytestring  to unicode transformation format -8 bit
        #data_read = str(data).encode("utf-8")
        #print("Pico's Core Temperature : " + temperature + " Degree Celcius")
        #print(f'data_read: {data_read}')
        #time.sleep(0.2)
        #:w
        #ser.write(b'm1234567890')
        data=ser.read(10)
        print(f'data: {data}')
        time.sleep(0.8)


if __name__ == "__main__":
    main()