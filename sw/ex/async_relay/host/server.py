import os
import asyncio
import socket

HOSTNAME = socket.gethostname()

async def handle_client(reader, writer):
    print(f'#### SERVER({HOSTNAME}): New connection')
    request = None
    while request != 'quit':
        request = (await reader.read(255)).decode('utf8')
        print(f'#### SERVER({HOSTNAME}): Received: {request!r}')

        response = f'<<<<< {request}'
        print(f'#### SERVER({HOSTNAME}): Written: {response}')
        writer.write(response.encode('utf8'))
        await writer.drain()
    writer.close()

async def run_server():
    server = await asyncio.start_server(handle_client, '0.0.0.0', os.environ['TEXT_SERVER_PORT'])
    async with server:
        await server.serve_forever()

asyncio.run(run_server())