import argparse
import asyncio
import os
from typing import AsyncIterator


CHUNK_SIZE = 100


async def readlines(reader: asyncio.StreamReader) -> AsyncIterator[bytes]:
    while line := await read_until_eol(reader):
        yield line


async def read_until_eol(reader: asyncio.StreamReader) -> bytes:
    """Returns a line of text or empty bytes object if EOF is received.
    """
    data = b''
    sep = os.linesep.encode()
    while data := data + await reader.read(CHUNK_SIZE):
        if sep in data:
            message, _, data = data.partition(sep)
            return message + sep


async def write(writer: asyncio.StreamWriter, data: bytes) -> None:
    writer.write(data)
    await writer.drain()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=8080)
    return parser.parse_args()