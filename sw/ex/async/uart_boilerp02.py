async def main():    
    q = Queue()
    task1 = asyncio.create_task(poll_Uart1(q))
    task2 = asyncio.create_task(send_Uart2(q))
    
    await asyncio.gather(task1, task2)
    print('Done!')