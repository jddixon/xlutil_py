#!/usr/bin/python3

# ~/dev/py/xlutil/testTimestamp.py

import os
import threading
import time
import unittest
from xlutil import mkEpochFromUTC, mkTimestamp


class TestTimestamp (unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testEpochConverter(self):
        # using code should set this:
        os.environ['TZ'] = 'UTC'
        t = time.time()
        tstamp = mkTimestamp()      # UTC
        s = mkEpochFromUTC(tstamp)
        if t > s:
            deltaT = t - s
        else:
            deltaT = s - t
        self.assertTrue(deltaT <= 1)


if __name__ == '__main__':
    unittest.main()
