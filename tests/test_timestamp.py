#!/usr/bin/python3

# ~/dev/py/xlutil/testTimestamp.py

import os
import time
import unittest
from xlutil import mk_epoch_from_utc, get_utc_timestamp


class TestTimestamp(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

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
