#!/usr/bin/env python3
# testLibev.py

""" Test libev functions used by this package. """

import os
import signal
import sys
import time
import unittest

import pyev
from rnglib import SimpleRNG

sys.path.insert(0, 'build/lib.linux-x86_64-2.7')  # for the .so


def sig_cb(watcher, revenets):
    """ Handle keyboard interrupt. """

    print("\n<KEYBOARD INTERRUPT>")
    loop = watcher.loop
    # pylint inexplicably reports EVBREAK_ALL not a member of pyev
    # pylint: disable=no-member
    loop.stop(pyev.EVBREAK_ALL)


def guillotine_cb(watcher, revents):
    """ Kill the event loop. """

    # pylint: disable=no-member
    watcher.loop.stop(pyev.EVBREAK_ALL)


def timer_cb(watcher, revents):
    """ Timed callback, right out of the book. """

    watcher.data += 1
    print("timer.data: {0}".format(watcher.data))
    print("timer.loop.iteration: {0}".format(watcher.loop.iteration))
    print("timer.loop.now(): {0}".format(watcher.loop.now()))


TICK = 0.051
LIFETIME = 1.720


class TestLibev(unittest.TestCase):
    """ Test libev functions used by this package. """

    def setUp(self):
        self.fd_ = None
        self.log_name = None
        self.loop = None
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        if self.loop:
            self.loop.stop()

    # utility functions #############################################

    def setup_async_logging(self):
        """ Set up async loggig for a test. """

        os.makedirs('tmp', exist_ok=True, mode=0o755)
        # pylint: disable=no-member
        self.loop = pyev.default_loop()
        self.log_name = 'tmp/log%05x' % self.rng.next_int32(1024 * 1024)

        # never used, never closed !
        self.fd_ = os.open(self.log_name,
                           os.O_CREAT | os.O_APPEND | os.O_NONBLOCK,   # flags
                           0o644)                                      # mode

        # set up watchers ##################################
        # ticks every second
        timer = self.loop.timer(0, TICK, timer_cb, 0)
        timer.start()

        # kills the event loop after LIFETIME seconds
        life_is_short = self.loop.timer(LIFETIME, 0, guillotine_cb, 0)
        life_is_short.start()

        # lets the keyboard end things early
        sig_handler = self.loop.signal(signal.SIGINT, sig_cb)
        sig_handler.start()

        self.loop.start()

    # actual unit tests #############################################

    def test_async_log(self):
        """ Test the async log -- in a primitive way. """

        t00 = time.time()
        self.setup_async_logging()
        t01 = time.time()
        delta_t = 1.0 * (t01 - t00)
        self.assertTrue(delta_t >= LIFETIME and delta_t < LIFETIME + 0.005)


if __name__ == '__main__':
    unittest.main()
