## MicroPython.org
* https://micropython.org/download/W5500_EVB_PICO/
* W5500_EVB_PICO-20230426-v1.20.0.uf2

## Wiznet
* 
* W5500_EVB_PICO_Hardwired_2023.10.12_Wiznet.uf2
  * MicroPython의 firmware에 Wiznet stack 올린 파일
  * https://github.com/wiznetmaker/Hard_wired_WIZNET5K-Micropython/tree/main/firmware
  * https://forum.wiznet.io/t/topic/11759/2
  * Error at asyncio stream
```
 ----WIZNET5K_PROVIDED_STACK----
Waiting for Link...
Waiting for Link...
Waiting for Link...
IP assigned:  192.168.2.8
run_forever
Task exception wasn't retrieved
future: <Task> coro= <generator object 'start_server' at 2000c440>
Traceback (most recent call last):
  File "asyncio/core.py", line 1, in run_until_complete
  File "asyncio/stream.py", line 1, in start_server
OSError: [Errno 107] ENOTCONN
Task exception wasn't retrieved
future: <Task> coro= <generator object 'start_server' at 2000c490>
Traceback (most recent call last):
  File "asyncio/core.py", line 1, in run_until_complete
  File "asyncio/stream.py", line 1, in start_server
OSError: [Errno 107] ENOTCONN
>>> 
Connection lost -- device reports readiness to read but returned no data (device disconnected or multiple access on port?)

Use Stop/Restart to reconnect.

Process ended with exit code 1.
```

