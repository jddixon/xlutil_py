#!/usr/bin/env python3
# xlattice_py/testTimestamp.py

""" Test timestamp-related functions. """

import calendar
import os
import time
import unittest

from xlutil import(mk_epoch_from_utc, get_utc_timestamp,
                   parse_timestamp, timestamp, timestamp_now)

from rnglib import SimpleRNG


class TestTimestamp(unittest.TestCase):
    """ Test timestamp-related functions. """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # Note that in the Go code timestamp is an int64, whereas here it
    # is a string.

    def test_constructor(self):
        """ Verify that successive timestamps are about the same. """

        struct_now = time.gmtime()                  # struct_time
        gmt_now = calendar.timegm(struct_now)       # seconds from epoch
        str_now = timestamp(gmt_now)
        now_again = parse_timestamp(str_now)
        str_again = timestamp(now_again)
        self.assertEqual(str_now, str_again)

    def test_parser(self):
        """ Exercise the timestamp parser. """

        example = "2004-11-18 20:03:34"
        from_epoch = parse_timestamp(example)      # seconds from epoch
        from_as_str = timestamp(from_epoch)
        self.assertEqual(from_as_str, example)

    def test_now(self):
        """ Verify that timestamp_now() returns the GMT time. """

        struct_now = time.gmtime()                 # struct_time
        gmt_now = calendar.timegm(struct_now)      # seconds from epoch
        now_as_str = timestamp_now()               # in string format
        now2 = parse_timestamp(now_as_str)
        self.assertTrue(now2 - gmt_now <= 1)

    def test_epoch_converter(self):
        # using code should set this:
        os.environ['TZ'] = 'UTC'
        t__ = time.time()
        tstamp = get_utc_timestamp()      # UTC
        s__ = mk_epoch_from_utc(tstamp)
        if t__ > s__:
            delta_t = t__ - s__
        else:
            delta_t = s__ - t__
        self.assertTrue(delta_t <= 1)


if __name__ == '__main__':
    unittest.main()
