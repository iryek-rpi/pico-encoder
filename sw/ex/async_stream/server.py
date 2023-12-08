import asyncio

async def handler(r,w):
    print(f'{r} {w}')
    while True:
        req = await r.read(100)
        req = req.decode('utf-8')
        print(f'request: {req}')
        w.write(bytes(f'<<< {req}', 'utf-8'))
        await w.drain()

loop = asyncio.get_event_loop()
loop.create_task(asyncio.start_server(handler, '0.0.0.0', 7505))
loop.run_forever()