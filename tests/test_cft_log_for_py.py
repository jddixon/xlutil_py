#!/usr/bin/env python3
# testCFTLogForPy.py

""" Test the C fault-tolerant log for Python. """

import os
import sys
import time
import unittest

import xlattice
from rnglib import SimpleRNG
# pylint: disable=no-name-in-module
from cFTLogForPy import (
    init_cft_logger, open_cft_log, log_msg, close_cft_logger)


sys.path.insert(0, 'build/lib.linux-x86_64-3.6')  # for the .so


class TestCFTLogForPy(unittest.TestCase):
    """ Test the C fault-tolerant log for Python. """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    def unique_file_name(self):
        """ Create a locally unique file name under tmp/. """

        log_file = "tmp/foo%04x" % self.rng.next_int16()
        while os.path.exists(log_file):
            log_file = "tmp/foo%04x" % self.rng.next_int16()
        return log_file

    # actual unit tests #############################################
    def test_version(self):
        """ Display library version info. """

        version = xlattice.__version__
        print("VERSION %s" % version, end=' ')
        if version >= '0.5.1':
            print(" %s" % xlattice.__version_date__)
        else:
            self.fail("have loaded an old version of the library")

    def test_open_and_close(self):
        """ Test open and close functions. """

        log_file = self.unique_file_name()
        status = init_cft_logger()
        status = open_cft_log(log_file)
        self.assertEqual(0, status)
        time.sleep(0.2)
        if status:
            print("open_cft_log failed, status is %d" % status)
        else:
            time.sleep(0.2)
            status = close_cft_logger()
        time.sleep(0.2)
        self.assertEqual(0, status)
        os.path.exists(log_file)

    class DumbLogger:
        """ A very simple logger for testing. """

        def __init__(self):
            self.log_file = "tmp/dumb.log"

        def open_log(self):
            """ Open the dummy logger. """
            init_cft_logger()
            return open_cft_log(self.log_file)

        def close_log(self):
            """ Close the dummy logger. """
            return close_cft_logger()

    def test_dumb_logger(self):
        """ Run some simple tests of the DumbLogger. """

        logger = self.DumbLogger()
        time.sleep(0.1)
        status = logger.open_log()
        self.assertEqual(0, status)
        time.sleep(0.1)
        status = logger.close_log()
        time.sleep(0.1)
        self.assertEqual(0, status)
        self.assertTrue(os.path.exists(logger.log_file))

    def test_initialization(self):
        """Tests init, log messages, close, with sleeps. """

        log_file = self.unique_file_name()
        init_cft_logger()
        log_ndx = open_cft_log(log_file)
        if log_ndx:
            print("open_cft_logger failed, log_ndx is %d" % log_ndx)
        else:
            log_msg(log_ndx, "now is the winter of our discontent\n")
            log_msg(log_ndx, "made glorious summer by this son of York\n")
            log_msg(log_ndx, "buffers are temporarily multiples of 64B\n")
            log_msg(log_ndx,
                    "... so these few message should overflow a page\n")
            # print "ABOUT TO WRITE BLOCK 0";    sys.stdout.flush()
            for n__ in range(128):
                #       ....x....1....x....2....x....3....x....4...
                log_msg(
                    log_ndx,
                    "padding ljlkjk;ljlj;k;lklj;j;kjkljklj %04x\n" %
                    n__)
                # we see 0 .. 87 consistently, so 88 * 43 = 3784 bytes
                # have been written and the next line would take it to
                # print '%3d' % n, ; sys.stdout.flush()     # DEBUG
            # print # DEBUG

            # print "BLOCK 0 WRITTEN";    sys.stdout.flush()
            time.sleep(0.2)     # NOTE
            for n__ in range(128):
                log_msg(
                    log_ndx, "padding ljlkjk;ljlj;k;lklj;j;kjkljklj %04x\n" %
                    (n__ + 128))
            # print "BLOCK 1 WRITTEN";    sys.stdout.flush()
            time.sleep(0.2)     # NOTE
            for n__ in range(128):
                log_msg(
                    log_ndx, "padding ljlkjk;ljlj;k;lklj;j;kjkljklj %04x\n" %
                    (n__ + 256))
            # print "BLOCK 2 WRITTEN";    sys.stdout.flush()
            time.sleep(0.2)     # NOTE
            for n__ in range(128):
                log_msg(
                    log_ndx, "padding ljlkjk;ljlj;k;lklj;j;kjkljklj %04x\n" %
                    (n__ + 384))
            # print "BLOCK 3 WRITTEN";    sys.stdout.flush()
            # close_cft_logger(None)

            # print "BRANCHING TO close_cft_logger"; sys.stdout.flush()   # NOT
            # :1SEEN
            close_cft_logger()
            # print "close_cft_logger returns %s" % str(junk);
            # sys.stdout.flush()

            time.sleep(0.2)     # NOTE_AT_END


if __name__ == '__main__':
    unittest.main()
