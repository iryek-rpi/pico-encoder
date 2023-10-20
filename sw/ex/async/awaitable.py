import asyncio
import time

async def do_something(t):
    while True:
        print(f'\nDo somthing not yeilding for {t} sec ', end=':')
        for i in range(t):
            print(i, end=' ')
            time.sleep(1)
        await asyncio.sleep(2) 

async def do_something_else(t):
    while True:
        print(f'\nDo_something else yielding for {t} sec ', end=':')
        for i in range(t):
            print('*', end=' ')
            await asyncio.sleep(0.5)

def main():
    loop=asyncio.get_event_loop()
    loop.create_task(do_something(5))
    loop.create_task(do_something_else(5))
    #loop.run_until_complete(asyncio.sleep(30))
    loop.run_forever()
    print('main done')

if __name__ == "__main__":
    #asyncio.run(main())
    main()