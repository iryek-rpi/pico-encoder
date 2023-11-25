'''
https://github.com/kamilwu/python-asyncio-guide/tree/master/part2/chat
'''
import asyncio
from typing import Dict
from typing import Tuple

from chat.common import parse_args
from chat.common import readlines
from chat.common import write


users: Dict[Tuple[str, int], asyncio.StreamWriter] = {}


async def handle_connection(reader: asyncio.StreamReader,
                            writer: asyncio.StreamWriter) -> None:
    addr = writer.get_extra_info('peername')
    users[addr] = writer
    print(f'{addr}: Connection established.')

    async for data in readlines(reader):
        print(f'{addr}: {data.decode()!r}')
        writes = (write(writer, data) for user, writer in users.items()
                  if user != addr)
        await asyncio.gather(*writes)

    del users[addr]
    print(f'{addr}: Connection closed by the remote peer.')


async def start_server() -> None:
    args = parse_args()
    server = await asyncio.start_server(handle_connection, args.host,
                                        args.port)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(start_server())