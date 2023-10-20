from machine import Pin, UART
import uasyncio as asyncio

uart = UART(0, tx=Pin(0), rx=Pin(1))  # w5500-evb-pico
uart.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=10)
    
async def receiver():
    sreader = asyncio.StreamReader(uart)
    while True:
        data = await sreader.readline()
        print(data)

async def main():
    asyncio.create_task(receiver())
    count=0
    while True:    
        await asyncio.sleep_ms(5000)
        count += 1
        print('waiting...', count)

if __name__ == '__main__':    
    try:
        asyncio.run(main())
    finally:
        asyncio.new_event_loop()