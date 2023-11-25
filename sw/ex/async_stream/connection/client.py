import asyncio
import sys
from contextlib import suppress
from typing import IO

import aiofiles

from chat.common import parse_args
from chat.common import readlines
from chat.common import write


HOST = '127.0.0.1'
PORT = 8080


async def handle_reads(reader: asyncio.StreamReader) -> None:
    async for echoed in readlines(reader):
        if echoed:
            print(f'{echoed.decode()!r}')
        else:
            print('EOF received. The server may be dead.')
            break


async def connect(file: IO[str]) -> None:
    args = parse_args()
    reader, writer = await asyncio.open_connection(args.host, args.port)
    handler = asyncio.create_task(handle_reads(reader))
    loop = asyncio.get_event_loop()

    async for message in aiofiles.threadpool.wrap(file, loop=loop):
        await write(writer, message.encode())

    handler.cancel()
    with suppress(asyncio.CancelledError):
        await handler

    writer.close()
    await writer.wait_closed()
    print('Connection closed.')


if __name__ == '__main__':
    asyncio.run(connect(sys.stdin))