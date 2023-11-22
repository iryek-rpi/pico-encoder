import asyncio
from asyncio import Transport, Future, AbstractEventLoop
from typing import Optional

class HTTPGetClientProtocol(asyncio.Protocol):
    def __init__(self, host: str, loop: AbstractEventLoop):
        self._host: str = host
        self._future: Future = loop.create_future()
        self._transport: Optional[Transport] = None
        self._response_buffer: bytes = b''

    async def get_response(self):
        print(f'\n###### get_response(): awaiting self._future')
        return await self._future

    def _get_request_bytes(self) -> bytes:
        request = f"GET / HTTP/1.1\r\n" \
        f"Connection: close\r\n" \
        f"Host: {self._host}\r\n\r\n"

        return request.encode()

    def connection_made(self, transport: Transport):
        print(f'\n###### Connection made to {self._host}')
        self._transport = transport
        print(f'###### Writing to transport:{transport} data:{self._get_request_bytes()}')
        self._transport.write(self._get_request_bytes())

    def data_received(self, data):
        print(f'\n###### Data received!')
        self._response_buffer = self._response_buffer + data

    def eof_received(self) -> Optional[bool]:
        print(f'\n###### EOF received!')
        self._future.set_result(self._response_buffer.decode())
        return False

    def connection_lost(self, exc: Optional[Exception]) -> None:
        print(f'\n###### Connection lost')
        if exc is None:
            print('Connection closed without error.')
        else:
            self._future.set_exception(exc)