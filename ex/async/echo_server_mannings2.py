import asyncio
import logging
from asyncio import StreamReader, StreamWriter

task = None

async def echo(reader: StreamReader, writer: StreamWriter): #C
    global task

    try:
        while (data := await reader.readline()) != b'':
            writer.write(data)
            await writer.drain()

            print('Received: ', data)
            if data == b'quit\n':
                print('canceling task')
                task.cancel()
                break

    except Exception as e:
        logging.exception('Error reading from client.', exc_info=e)
    
    print('Closing the client socket')
    writer.close()

async def client_connected(reader: StreamReader, writer: StreamWriter) -> None: #E
    global task

    print(f'New client added: {writer.get_extra_info("peername")}')
    #writer.write('Welcome!!\n'.encode())
    #await writer.drain()
    #task = asyncio.create_task(echo(reader, writer))

    try:
        while (data := await reader.readline()) != b'':
            print('Received: ', data)
            if data == b'quit\n':
                break

            writer.write(data)
            await writer.drain()


    except Exception as e:
        logging.exception('Error reading from client.', exc_info=e)
    
    print('Closing the client socket')
    writer.close()

async def main():
    server = await asyncio.start_server(client_connected, '127.0.0.1', 8000) #F

    async with server:
        await server.serve_forever()


asyncio.run(main())