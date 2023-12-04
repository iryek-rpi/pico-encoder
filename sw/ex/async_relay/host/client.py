import os
import asyncio
import socket

HOSTNAME = socket.gethostname()

async def tcp_echo_client(ip, port):
    reader, writer = await asyncio.open_connection(ip, int(port))
    print(f'# CLIENT({HOSTNAME}): Connected to {ip}:{port}')
    while True:
        message = input(f"# CLIENT({HOSTNAME}): Enter message: ")
        if message == "exit":
            break

        writer.write(message.encode())
        await writer.drain()

        data = await reader.read(100)
        print(f'# CLIENT({HOSTNAME}): Received: {data.decode()!r}')

    print('# CLIENT({HOSTNAME}): Close the connection')
    writer.close()
    await writer.wait_closed()

asyncio.run(tcp_echo_client(os.environ['TEXT_SERVER_IP'], os.environ['TEXT_SERVER_PORT']))