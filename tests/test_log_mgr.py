#!/usr/bin/env python3
# xlattice_py/testLogMgr.py

""" Test log manager functioning. """

import os
import shutil
import time
import unittest
import sys
from xlattice.ftlog import LogMgr
sys.path.insert(0, 'build/lib.linux-x86_64-3.4')  # for the .so


class TestLogMgr(unittest.TestCase):
    """ Test log manager functioning. """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_just_open_and_close(self):
        """ Test simply opening and then closing a log. """
        if os.path.exists('./logs'):
            shutil.rmtree('./logs')
        mgr = LogMgr('logs')
        logger = mgr.open('foo')
        self.assertIsNotNone(logger)
        # print "XXX NO MESSAGES XXX"
        expected_log_file = 'logs/foo.log'
        self.assertEqual(expected_log_file, logger.log_file_name)
        # we don't provide any way to close individual logs
        mgr.close()

        contents = None
        with open(expected_log_file, 'r') as file:
            contents = file.read()
        if contents:
            contents = contents.strip()
            self.assertEqual(0, len(contents))

    def test_with_single_message(self):
        """ Test opening a log, logging a single message, and closing. """

        if os.path.exists('./logs'):
            shutil.rmtree('./logs')
        mgr = LogMgr('logs')
        logger = mgr.open('foo')
        logger.log('oh hello')
        # can't test this after logger closed - because object destroyes
        expected_log_file = 'logs/foo.log'
        self.assertEqual(expected_log_file, logger.log_file_name)
        mgr.close()

        self.assertTrue(os.path.exists(expected_log_file))
        with open(expected_log_file, 'r') as file:
            contents = file.read()
        contents = contents.strip()
        self.assertTrue(contents.endswith('oh hello'))    # GEEP

    def test_more_messages(self):
        """ Test opening a log, logging several messages, and closing. """

        if os.path.exists('./logs'):
            shutil.rmtree('./logs')
        mgr = LogMgr('logs')
        logger = mgr.open('bar')
        msg = ''
        msg += logger.log("gibberish ending in uhm lots of stuff and A")
        msg += logger.log("gibberish ending in uhm lots of stuff and B")
        msg += logger.log("gibberish ending in uhm lots of stuff and C")
        msg += logger.log("gibberish ending in uhm lots of stuff and D")
        expected_log_file = 'logs/bar.log'
        self.assertEqual(expected_log_file, logger.log_file_name)
        mgr.close()

        self.assertTrue(os.path.exists(expected_log_file))
        with open(expected_log_file, 'r') as file:
            contents = file.read()
        self.assertEqual(msg, contents)          # END

    def test_messages_with_sleeps(self):
        """
        Open a log, log some messages with some intervening sleeps, and
        closing.

        The presence of a time.sleep() _anywhere_ in the method used
        to cause a segfault.
        """
        if os.path.exists('./logs'):
            shutil.rmtree('./logs')
        mgr = LogMgr('logs')
        logger = mgr.open('baz')
        msg = ''
        msg += logger.log("gibberish ending in uhm lots of stuff and A")
        msg += logger.log("gibberish ending in uhm lots of stuff and B")
        time.sleep(0.2)
        msg += logger.log("gibberish ending in uhm lots of stuff and C")
        msg += logger.log("gibberish ending in uhm lots of stuff and D")
        msg += logger.log("gibberish ending in uhm lots of stuff and E")
        time.sleep(0.2)
        msg += logger.log("gibberish ending in uhm lots of stuff and F")
        msg += logger.log("gibberish ending in uhm lots of stuff and G")
        msg += logger.log("gibberish ending in uhm lots of stuff and H")
        time.sleep(0.2)
        expected_log_file = 'logs/baz.log'
        self.assertEqual(expected_log_file, logger.log_file_name)
        mgr.close()

        self.assertTrue(os.path.exists(expected_log_file))
        with open(expected_log_file, 'r') as file:
            contents = file.read()
        self.assertEqual(msg, contents)      # FOOFOO


if __name__ == '__main__':
    unittest.main()
