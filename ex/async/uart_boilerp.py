import uasyncio as asyncio
from machine import UART

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
    uart = UART(1)
    asyncio.create_task(uart_receiver(uart))
    asyncio.create_task(uart_sender(uart))
    await asyncio.sleep(10)

asyncio.run(main())