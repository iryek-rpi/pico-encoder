import machine
import uasyncio as asyncio
import random

# Coroutine 1: emulate the uart port receiving a data signal at random intervals (1 - 10 secs)
async def uart_Data(seq):
    while True:
        rnd = random.randrange(1, 10)
        await asyncio.sleep(rnd)
        return 'id=1&seq=' + str(seq)

# Coroutine 2: emulate an HTTP post (or head) with a response delay of 4 - 6 secs
async def send_HTTP():
    while True:
        await asyncio.sleep(5)
        return 'HTTP return: 200'

# Cooroutine for entry point
async def main():
    x = 1
    y = 1
    while True:       
        # Call coro 1 directly
        uart = await uart_Data(x)
        x += 1
        await asyncio.sleep(0)
        
        if uart != '':
            print(uart)
            # Call coro 2 directly
            http = await send_HTTP()
            await asyncio.sleep(0)
            print(http + ': ' + str(y))
            y += 1
    
# Call the main routine asynchronously
asyncio.run(main())