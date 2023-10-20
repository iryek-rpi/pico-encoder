# PyMOTW-3 example for asyncio
# asyncio_echo_client_coroutine.py
# https://pymotw.com/3/asyncio/io_coroutine.html

import asyncio
import logging
import sys

MESSAGES = [
    b'This is the message.\n',
    b'It will be sent ',
    b'in parts.',
]

IP = 'localhost'
PORT = 8000
SERVER_ADDRESS = (IP, PORT)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s: %(message)s',
    stream=sys.stderr,
)
log = logging.getLogger('main')

async def echo_client(address, messages):
    log = logging.getLogger('echo_client')

    log.debug('connecting to {} port {}'.format(*address))
    reader, writer = await asyncio.open_connection(*address)

    # This could be writer.writelines() except that
    # would make it harder to show each part of the message
    # being sent.
    #for msg in messages:
    #    writer.write(msg)
    #    log.debug('sending {!r}'.format(msg))
    #if writer.can_write_eof():
    #    writer.write_eof()
    #await writer.drain()

    writer.write(messages[0])
    writer.drain()

    log.debug('waiting for response')

    while True:
        #data = await reader.read(128)
        data = await reader.readline()
        if data:
            log.debug('received {!r}'.format(data))
            writer.close()
            return
        else:
            log.debug('closing')
            writer.close()
            return
        
event_loop = asyncio.get_event_loop()

try:
    event_loop.run_until_complete(
        echo_client(SERVER_ADDRESS, MESSAGES)
    )
finally:
    log.debug('closing event loop')
    event_loop.close()        