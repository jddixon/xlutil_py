#!/usr/bin/env python3
# testCFTLogObj.py

""" Test the C fault-tolerant log for python. """

import os
import sys
import time
import unittest

import xlattice

# pylint: disable=no-name-in-module
import cFTLogForPy
# pylint: disable=no-name-in-module
from cFTLogForPy import (
    # open_cft_log, log_msg not imported
    init_cft_logger, close_cft_logger)

from rnglib import SimpleRNG

sys.path.insert(0, 'build/lib.linux-x86_64-3.4')  # for the .so


class TestCLogObj(unittest.TestCase):
    """ Test the C fault-tolerant log for python. """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################
    def unique_file_name(self):
        """ Create a file under tmp/ with a locally unique name. """

        log_file = "tmp/foo%04x" % self.rng.next_int16()
        while os.path.exists(log_file):
            log_file = "tmp/foo%04x" % self.rng.next_int16()
        return log_file

    # actual unit tests #############################################
    def test_version_and_max_log(self):
        """ Display the library version number. """

        version = xlattice.__version__
        print("VERSION %s" % version, end=' ')
        if version >= '0.5.1':
            print(" %s" % xlattice.__version_date__)
            # pylint: disable=no-member
            self.assertEqual(16, cFTLogForPy.max_log)
        else:
            print(" THIS IS AN OLD VERSION OF THE LIBRARY")

    def test_ctor(self):
        """
        Verify that the constructor creates a logger with sensible props.
        """

        init_cft_logger()
        log_file = self.unique_file_name()
        # pylint: disable=no-member
        obj = cFTLogForPy.LogForPy()
        obj.init(log_file)
        self.assertEqual(0, obj.ndx())
        self.assertEqual(0, obj.count())
        self.assertEqual(log_file, obj.log_file())

    def test_count(self):
        """ Verify that the message count is correct. """

        messages = ["now is the winter of our discontent\n",
                    "made glorious summer by this son of York\n",
                    "and all the clouds that lowered upon our house\n",
                    "... and so forth and so on\n", ]
        log_file = self.unique_file_name()
        # this 3-line stanza needs to be shortened
        init_cft_logger()
        obj = cFTLogForPy.LogForPy()  # pylint: disable=no-member
        obj.init(log_file)
        self.assertEqual(log_file, obj.log_file())       # must follow init()

        log_ndx = obj.ndx()
        self.assertEqual(0, log_ndx)
        expected = 0
        count = obj.count()
        self.assertEqual(expected, count)
        for msg in messages:
            # pylint: disable=no-member
            obj.log_msg(msg)
            expected += 1
            count = obj.count()
            self.assertEqual(expected, count)

        # XXX OLD MODULE-LEVEL FUNC
        status = close_cft_logger(log_ndx)
        # print("close_cft_logger returns %s" % str(status))
        self.assertEqual(status, 0)


if __name__ == '__main__':
    unittest.main()
