import tkinter
import asyncio
import threading
import websockets
from websockets import exceptions
import json
from datetime import datetime


# Starthilfe für asynkrone Funktion connect
def _asyncio_thread():
    async_loop.create_task(connect())
    async_loop.run_forever()


async def connect():
    async with websockets.connect("ws://194.163.132.218:8765") as websocket:
        while True:
            message = await websocket.recv()
            print(message)


async def send(websocket, name):
    while True:
        message = await queue.get()
        await websocket.send(msg)

def buttonexecutor(e=None):
    msg = entry.get()
    asyncio.run_coroutine_threadsafe(messagesender(msg), async_loop)
    entry.delete(0, "end")


async def messagesender(message):
    await queue.put(message)


def logger(reason, message):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    text.configure(state="normal")
    text.insert("end", f"({current_time}) [ {reason} ] {message}\n")
    text.configure(state="disabled")


if __name__ == '__main__':
    # Asyncio
    async_loop = asyncio.get_event_loop()
    queue = asyncio.Queue()

    # Erstelle tkinter
    root = tkinter.Tk()
    root.title("Messanger")

    text = tkinter.Text(root, width=150, state="disabled")
    text.pack()

    entry = tkinter.Entry(root, state="disabled", width=100)
    entry.pack()

    tkinter.Button(master=root, text="Senden", command=buttonexecutor).pack()

    # Starte Websocket Verbindung
    thread = threading.Thread(target=_asyncio_thread).start()

    # Starte tkinter
    root.mainloop()