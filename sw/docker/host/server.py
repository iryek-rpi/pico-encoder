import os
import asyncio
import socket

HOSTNAME = socket.gethostname()

async def handle_client(reader, writer):
    print(f'#### SERVER({HOSTNAME}): New connection')
    while True:
        data = await reader.read(255)
        if data:
            response = bytes(f'<<<<< {data.decode("utf-8")}', 'utf-8')
            print(f'#### SERVER({HOSTNAME}): sending response: {response}')
            writer.write(response)
            await writer.drain()

async def run_server():
    server = await asyncio.start_server(handle_client, '0.0.0.0', os.environ['TEXT_SERVER_PORT'])
    async with server:
        await server.serve_forever()

asyncio.run(run_server())