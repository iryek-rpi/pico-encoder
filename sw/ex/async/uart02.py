import machine
import uasyncio as asyncio
import random
import time

# Coroutine 1: emulate the uart port receiving a data signal at random intervals (1 - 10 secs)
async def uart_Data(seq):
    while True:
        if (seq == 1):
            rnd = 0
        else:
            rnd = random.randrange(1, 10)
        strData = 'Data item ' + str(seq) + ' received on UART after ' + str(rnd) + ' secs'
        await asyncio.sleep(rnd)
        return strData

# Coroutine 2: emulate an HTTP post (or head) with a response delay of 5 secs
async def send_HTTP(seq):
    while True:
        await asyncio.sleep(0)
        time.sleep(5)
        strHTTP = 'Data item ' + str(seq) + ' HTTP return: 200 after 5 secs'
        return strHTTP

# Cooroutine for entry point
async def main():
    start = time.ticks_ms()
    seq = 1
    while True:       
        # Call coro 1 directly
        uart = await uart_Data(seq)
        await asyncio.sleep(0)
        print(uart)
        
        if uart != '':
            # Call coro 2 directly
            http = await send_HTTP(seq)
            print(http + ' - elapsed ' + str(time.ticks_diff(time.ticks_ms(), start) / 1000))

        seq += 1
    
# Call the main routine asynchronously
asyncio.run(main())