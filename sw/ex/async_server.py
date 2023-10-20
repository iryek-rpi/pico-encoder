import usocket as socket
import uasyncio as asyncio
import uselect as select
import ujson
from led import *

def heartbeat(interval):
    blink_led(red, 1/interbal)

class Server:

    def __init__(self, host='0.0.0.0', port=80, backlog=5, timeout=10):
        self.host = host
        self.port = port
        self.backlog = backlog
        self.timeout = timeout

    async def run(self):
        print('Awaiting client connection.')
        self.cid = 0
        print("run1")
        #asyncio.create_task(heartbeat(100))
        print("run2")
        self.server = await asyncio.start_server(self.run_client, self.host, self.port, self.backlog)
        print("server: ", self.server)
        while True:
            await asyncio.sleep(100)

    async def run_client(self, sreader, swriter):
        self.cid += 1
        print('Got connection from client', self.cid)
        try:
            while True:
                try:
                    res = await asyncio.wait_for(sreader.readline(), self.timeout)
                except asyncio.TimeoutError:
                    res = b''
                if res == b'':
                    raise OSError
                print('Received {} from client {}'.format(ujson.loads(res.rstrip()), self.cid))
                response = {
                'error': 'invalid request',
                'status': 'retry'
                 }
                swriter.write(ujson.dumps(response))
                await swriter.drain()  # Echo back
        except OSError:
            pass
        print('Client {} disconnect.'.format(self.cid))
        await sreader.wait_closed()
        print('Client {} socket closed.'.format(self.cid))

    async def close(self):
        print('Closing server')
        self.server.close()
        await self.server.wait_closed()
        print('Server closed.')

server = Server()
try:
    asyncio.run(server.run())
except KeyboardInterrupt:
    print('Interrupted')  # This mechanism doesn't work on Unix build.
finally:
    asyncio.run(server.close())
    _ = asyncio.new_event_loop()