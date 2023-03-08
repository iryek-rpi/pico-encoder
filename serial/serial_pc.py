import os
import serial
import time

ser = serial.Serial('/dev/ttyUSB0', 9600)

time.sleep(1)

while True:
    # read two bytes of data
    data = ser.read(8)
    #data = ser.readline()
    # convert bytestring  to unicode transformation format -8 bit
    data_read = str(data).encode("utf-8")
    #print("Pico's Core Temperature : " + temperature + " Degree Celcius")
    print(f'data_read: {data_read}')
    time.sleep(0.2)
    ser.write(b'm')
    time.sleep(0.2)