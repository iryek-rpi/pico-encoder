import asyncio
loop = asyncio.get_event_loop()
async def task():
    # wait for server is ready and open connection
    while True:
        try:
            r, w = await asyncio.open_connection('localhost', 7505)
            print(f'{r} {w}')
            break
        except ConnectionRefusedError:
            print('ConnectionRefusedError')
            await asyncio.sleep(3)

    while True:
        await asyncio.sleep(5)
        w.write(b'abc')
        await w.drain()
        response = await r.read(100)
        print(f'response:{response}')
 
loop.create_task(task())
loop.run_forever()