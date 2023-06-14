import uasyncio as asyncio
import random
from queue import Queue          # Copyright (c) 2018-2020 Peter Hinch

# ANSI colors  
colours = (  
    "\033[0m",  # End of color  
    "\033[31m",  # Red  
    "\033[34m",  # Blue  
#     "\033[32m",  # Green  
#     "\033[36m",  # Cyan  
)

# Coroutine 1: emulates polling the Uart1 port to get data items and putting them into the queue.
# Items received at random intervals between 0 and 10 seconds for first 20 items, then 0 to 30 seconds thereafter.
async def poll_Uart1(q):
    n = 1
    while True:
        upper = 10 if n <= 20 else 30 
        interval = random.randint(0, upper)
        await asyncio.sleep(interval)
        strData = 'Data Item ' + str(n) 
        await q.put(strData)

        items = q.qsize()
        print (colours[1] + f'{strData} received on Uart_1 after {interval} secs interval - items now in queue: {items}' + colours[0])
        n += 1

# Coroutine 2: emulates retrieving items from the queue and sending them to the Uart2 port,
# then emulates the 6 - 10 second delay in the HTTP post response.
async def send_Uart2(q):
    while True:
        delay = random.randint(6, 10)
        await asyncio.sleep(delay)
        strData = await q.get()
        
        items = q.qsize()
        print(colours[2] + f'{strData} sent to Uart_2 after {delay} secs delay - items left in queue: {items}' + colours[0])

# Main entry point for event loop.
async def main():    
    q = Queue()
    asyncio.create_task(poll_Uart1(q))
    asyncio.create_task(send_Uart2(q))
    
    await asyncio.sleep(499999)
    print('Done!')

asyncio.run(main())