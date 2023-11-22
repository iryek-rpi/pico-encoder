import sys
import asyncio
from asyncio import AbstractEventLoop
from cp import HTTPGetClientProtocol

async def make_request(host: str, port: int, loop: AbstractEventLoop) -> str:
    def protocol_factory():
        p = HTTPGetClientProtocol(host, loop)
        print(f'returning a protocol: {p}')
        return p

    a, protocol = await loop.create_connection(protocol_factory, host=host, port=port)
    return await protocol.get_response()

url = 'www.example.com'
url = 'localhost'
async def main(url):
    loop = asyncio.get_running_loop()
    result = await make_request(url, 8080, loop)
    print(f'\n\n########## Result of request: ')
    print(result)

if __name__=='__main__':
    asyncio.run(main(url))