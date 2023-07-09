from machine import Pin, UART
import uasyncio as asyncio

uart = UART(0, tx=Pin(0), rx=Pin(1))  # w5500-evb-pico
uart.init(baudrate=9600, bits=8, parity=None, stop=1, timeout=10)

async def uart_sender(uart):
    writer = asyncio.StreamWriter(uart, {})
    while True:
        writer.write('sender here, how are you receiver?\n')
        await writer.drain()
        await asyncio.sleep(1)

async def uart_receiver(uart):
    reader = asyncio.StreamReader(uart)
    while True:
        message = await reader.readline()
        print('uart_receiver recieved:', message)

async def main():
    asyncio.create_task(uart_receiver(uart))
    asyncio.create_task(uart_sender(uart))
    await asyncio.sleep(10)

asyncio.run(main())