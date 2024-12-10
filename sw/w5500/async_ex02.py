from time import sleep_ms
from machine import Pin, Timer
import rp2
import network
import machine
import uasyncio as asyncio
import net_utils as nu
import utils
import constants as c
from led import *

led_init()

def setup(country, ssid, key):
    rp2.country(country)
    wifi=network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.disconnect()
    LED=Pin("LED", Pin.OUT)
    LED.high()
    timeout=20000
    wifi.connect(ssid,key)
    timer=Timer()
    timer.init(period=200, mode=Timer.PERIODIC,
                            callback=lambda t:LED.toggle())
    s=0
    while timeout>0:
        s=wifi.status()
        if s==3 or s<0:
            break
        sleep_ms(100)
        timeout=timeout-100
   
    if(s<2):
        timer.init(period=1000, mode=Timer.PERIODIC,
                            callback=lambda t:LED.toggle())
    else:
        timer.deinit()
        LED.high()
    return wifi
   
async def comm():
    reader,writer= await asyncio.open_connection("192.168.0.154",2005)
    request = b"GET /index.html HTTP/1.1\r\nHost:example.org\r\n\r\n"
    writer.write(request)
    await writer.drain()
    print(await reader.read(512))
    reader.close()
    
    
async def client():
    relay_reader, relay_writer = await asyncio.open_connection('192.168.0.154', 2005)
    request = b"GET /index.html HTTP/1.1\r\nHost:example.org\r\n\r\n"
    relay_writer.write(request)
    await relay_writer.drain()
    print(await relay_reader.read(512))
    relay_reader.close()

async def handle_server1(reader, writer):
    print(f'server started: {reader}')
    while True:
      await client()
      sleep_ms(500)

async def handle_server(reader, writer):
    print(f'server started: {reader}')
    relay_reader, relay_writer = await asyncio.open_connection('192.168.0.154', 2005)
    request = b"GET /index.html HTTP/1.1\r\nHost:example.org\r\n\r\n"
    
    while True:
        relay_writer.write(request)
        await relay_writer.drain()
        r = await relay_reader.read(32)
        print(r)
        sleep_ms(500)
      
def main():
    global g_settings
    global g_uart

    led_start()
    g_settings = utils.load_settings()
    print(g_settings)
    g_uart, g_settings, ip_assigned = nu.init_connections(g_settings)    

    loop = asyncio.get_event_loop()
    print(f'creating task')
    loop.create_task(asyncio.start_server(handle_server, '0.0.0.0', 2004))

    #loop.create_task(client())
    loop.run_forever()

    #asyncio.run(comm())
  
if __name__ == '__main__':
    main()