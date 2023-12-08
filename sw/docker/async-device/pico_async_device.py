import asyncio
import socket
import os

HOST_IP = os.environ['HOST_IP']
HOST_PORT = os.environ['HOST_PORT']
PEER_IP = os.environ['PEER_IP']
CRYPTO_PORT = 8503
CRYPTO_PORT2 = 8504
TEXT_PORT = 2004

def encrypt_text(b64, dest):
    print('encrypt_text(): data received: ', b64, 'of type(b64): ', type(b64))
    print(f'encrypt_text(): dest: {dest}')
    #dest[1](b64, dest[0])
    return b64

def decrypt_crypto(b64, dest):
    print('decrypt_text(): data received: ', b64, 'of type(b64): ', type(b64))
    print(f'decrypt_text(): dest: {dest}')
    #dest[1](b64, dest[0])
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

async def process_serial_msg():
    dest = (PEER_IP, CRYPTO_PORT2)
    print(f'\n\nprocess_serial_msg() waiting 10sec.. before open_connection to {dest}')
    await asyncio.sleep(10)
    dest_reader, dest_writer = await asyncio.open_connection(*dest)
    print(f'@@@@@ process_serial_msg() open connection to {dest}')

    try:
        while True:
            await asyncio.sleep(5)
            b64 = b'SERIAL_MSG'
            if b64:
                sm = b64.decode('utf-8').strip()
                print(f'\n\n@@@@@ Simulate Received b64: {b64} sm: {sm}')
                print(f'@@@@@ Sending {b64} to {dest}')
                dest_writer.write(b64)
                await dest_writer.drain()
                response = await dest_reader.read(100)
                print(f"@@@@@ Received {response} from {dest}")
                if response == b'':
                    break
    except Exception as e:
        print(e)
        
    print(f"Close the connection for {dest}()")
    dest_writer.close()
    await dest_writer.wait_closed()
    dest_reader.close()
    await dest_reader.wait_closed()

    print('.', end='')
    return

async def process_stream(handler, reader, writer, name, dest):
    print(f'\n\nprocess_stream() Handling {name}.. dest: {dest}')
    dest_reader, dest_writer = await asyncio.open_connection(*dest)
    print(f"Connected to dest:{dest}")
    while True:
        b64 = await reader.read(100)
        addr = writer.get_extra_info('peername')
        print(f"Received {b64} from {addr} and relay it to {dest}")
        if b64 == b'':
            break
        dest_writer.write(handler(b64, dest))
        await dest_writer.drain()
        response = await dest_reader.read(100)
        print(f"Received {response} from {dest}")
        if response == b'':
            break
        writer.write(handler(response, addr))
        await writer.drain()

    print(f"Close the connection for {dest}()")
    dest_writer.close()
    await dest_writer.wait_closed()
    dest_reader.close()
    await dest_reader.wait_closed()

    print(f"Close the connection for handle_{name}()")
    writer.close()
    await writer.wait_closed()
    reader.close()
    await reader.wait_closed()

async def handle_tcp_text(reader, writer):
    print(f"\n### handle TCP TEXT from {reader} {writer}")
    dest = (PEER_IP, CRYPTO_PORT)
    await process_stream(encrypt_text, reader, writer, 'TEXT', dest)

async def handle_crypto(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"\n### handle TCP CRYPTO from {addr} at port {CRYPTO_PORT}")
    dest = (HOST_IP, HOST_PORT)
    print(f"\n### Relay to {dest}")
    await process_stream(decrypt_crypto, reader, writer, 'CRYPTO', dest)

async def handle_crypto2(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"\n### handle TCP CRYPTO 2 from {addr} at port {CRYPTO_PORT2}")
    dest = (HOST_IP, HOST_PORT)
    print(f"\n### Relay to {dest}")
    await process_stream(decrypt_crypto, reader, writer, 'CRYPTO2', dest)

def main():
    loop = asyncio.get_event_loop()

    loop.create_task(process_serial_msg())
    loop.create_task(asyncio.start_server(handle_tcp_text, '0.0.0.0', TEXT_PORT))
    loop.create_task(asyncio.start_server(handle_crypto, '0.0.0.0', CRYPTO_PORT))
    loop.create_task(asyncio.start_server(handle_crypto2, '0.0.0.0', CRYPTO_PORT2))

    print('run_forever')
    loop.run_forever()

if __name__ == '__main__':
    main()
