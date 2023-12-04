import asyncio
import socket
import os

HOST_IP = os.environ['HOST_IP']
HOST_PORT = os.environ['HOST_PORT']
PEER_IP = os.environ['PEER_IP']
CRYPTO_PORT = 8503
TEXT_PORT = 2004

def encrypt_text(b64, dest):
    print('data received: ', b64, 'of type(b64): ', type(b64))
    
    print(f'dest: {dest}')
    dest[1](b64, dest[0])
    return b64

def decrypt_crypto(b64, dest):
    print('data received: ', b64, 'of type(b64): ', type(b64))

    print(f'dest: {dest}')
    dest[1](b64, dest[0])
    return b64

def send_tcp_data_sync(data, addr):
    sock = socket.socket()
    print(f'Connecting to: {addr}')
    sock.connect(addr)
    print(f'Sending data: {data} to {addr}')
    msg_len = len(data)
    while msg_len>0:
        sent = sock.write(data)
        msg_len -= sent
        data = data[sent:]
    sock.close()

async def process_stream(handler, reader, writer, name, dest):
    print(f'handling {name}..')
    while True:
        b64 = await reader.read(100)
        addr = writer.get_extra_info('peername')
        print(f"Received {b64} from {addr}")

    print(f"Close the connection for handle_{name}()")
    writer.close()
    await writer.wait_closed()
    reader.close()
    await reader.wait_closed()

async def handle_tcp_text(reader, writer):
    print(f"\n### handle TCP TEXT from {reader} {writer}")
    #dest = ((PEER_IP, CRYPTO_PORT), send_tcp_data_sync)
    dest = (PEER_IP, CRYPTO_PORT)
    await process_stream(encrypt_text, reader, writer, 'TEXT', dest)

async def handle_crypto(reader, writer):
    print(f"\n### handle TCP CRYPTO from {reader} {writer}")
    #dest = ((HOST_IP, int(HOST_PORT)), send_tcp_data_sync)
    dest = (HOST_IP, HOST_PORT)
    await process_stream(decrypt_crypto, reader, writer, 'CRYPTO', dest)

def main():
    loop = asyncio.get_event_loop()

    loop.create_task(asyncio.start_server(handle_crypto, '0.0.0.0', CRYPTO_PORT))
    loop.create_task(asyncio.start_server(handle_tcp_text, '0.0.0.0', TEXT_PORT))

    print('run_forever')
    loop.run_forever()

if __name__ == '__main__':
    main()
