'''
Based on https://github.com/GSGBen/pico-serial
  * all these imports come from MicroPython. https://docs.micropython.org/en/latest/index.html
'''
import micropython
from machine import Pin, SPI, RTC
import uselect
import time
import random
from urandom import randint
import math
import sys
from sys import stdin, exit
import gc


CHARACTER_SIZE = 8  # size of each letter in pixels

TERMINATOR = "\n"   # how serial lines are ended


class Pico:
    """
    Global singleton, so we can use `self`. instead of global.
    """

    def __init__(self):
        """
        Run any once-off startup tasks.
        Set up input.
        """

        # give a chance to break the boot to fix serial/code issues. Put any riskier startup code after this
        boot_delay_seconds = 5
        self.delay_boot(2)

        self.run_loop = True

        # store incomplete lines from serial here. list of strings (no typing module in micropython)
        self.buffered_input = []
        # when we get a full line, store it here, without the terminator.
        # gets overwritten if a new line is read (as early as next tick).
        # blanked each tick.
        self.input_line_this_tick = ""

    def main(self):
        """
        Code entrypoint.
        The function that gets called to start.
        All non-setup code here or in functions under it.
        """

        counter = 0

        latest_input_line = ""

        # main loop
        while self.run_loop:

            # buffer from the USB to serial port
            self.read_serial_input()

            ########################### app per tick code here

            # simple output test
            print(counter)
            counter += 1

            # show serial input on the screen.
            # only update if we have a new line
            if self.input_line_this_tick:
                latest_input_line = self.input_line_this_tick

            ########################### end app per tick code here

            # simple loop speed control
            time.sleep_ms(100)

    def read_serial_input(self):
        """
        Buffers serial input.
        Writes it to input_line_this_tick when we have a full line.
        Clears input_line_this_tick otherwise.
        """
        # stdin.read() is blocking which means we hang here if we use it. Instead use select to tell us if there's anything available
        # note: select() is deprecated. Replace with Poll() to follow best practises
        select_result = uselect.select([stdin], [], [], 0)
        while select_result[0]:
            # there's no easy micropython way to get all the bytes.
            # instead get the minimum there could be and keep checking with select and a while loop
            input_character = stdin.read(1)
            # add to the buffer
            self.buffered_input.append(input_character)
            # check if there's any input remaining to buffer
            select_result = uselect.select([stdin], [], [], 0)
        # if a full line has been submitted
        if TERMINATOR in self.buffered_input:
            line_ending_index = self.buffered_input.index(TERMINATOR)
            # make it available
            self.input_line_this_tick = "".join(
                self.buffered_input[:line_ending_index])
            # remove it from the buffer.
            # If there's remaining data, leave that part. This removes the earliest line so should allow multiple lines buffered in a tick to work.
            # however if there are multiple lines each tick, the buffer will continue to grow.
            if line_ending_index < len(self.buffered_input):
                self.buffered_input = self.buffered_input[line_ending_index +
                                                          1:]
            else:
                self.buffered_input = []
        # otherwise clear the last full line so subsequent ticks can infer the same input is new input (not cached)
        else:
            self.input_line_this_tick = ""

    def delay_boot(self, seconds):
        """
        Wait for the given amount of time, allowing breaking with key_a and key_b at the same time,
        """
        tick_ms_timestamp = time.ticks_ms()
        delta_time_ms = 0
        timer_ms = 0
        max_ms = seconds * 1000

        while timer_ms < max_ms:
            delta_time_ms = time.ticks_diff(time.ticks_ms(), tick_ms_timestamp)
            tick_ms_timestamp = time.ticks_ms()
            timer_ms += delta_time_ms

    def exit(self):
        self.run_loop = False

if __name__ == "__main__":
    pico = Pico()
    pico.main()
    gc.collect()
