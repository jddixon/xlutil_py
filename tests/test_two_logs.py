#!/usr/bin/env python3
# testTwoLogs.py

""" Test concurrent use of more than one log. """

import os
import shutil
import sys
import unittest
from xlattice.ftlog import LogMgr

sys.path.insert(0, 'build/lib.linux-x86_64-3.4')  # for the .so


class TestTwoLogs(unittest.TestCase):
    """ Test concurrent use of more than one log. """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # utility functions #############################################

    # actual unit tests #############################################

    def test_with_single_message(self):
        """ Log a single message, close log, verify correct state. """

        path_to_logs = os.path.join('tmp', 'logs')
        if os.path.exists(path_to_logs):
            shutil.rmtree(path_to_logs)

        # -- open ---------------------------------------------------
        def show_log_handle(handle):
            """ Dump the log handle for testing. """
            print("HANDLE: %s as %d writing to %s" % (
                handle.base_name, handle.lfd, handle.log_file,))
        mgr = LogMgr(path_to_logs)
        foo_log = mgr.open('foo')
        foo_log.log('oh hello, foo')
        show_log_handle(foo_log)                       # DEBUG

        bar_log = mgr.open('bar')
        bar_log.log('oh hello, bar')
        # showLogHandle(bar_log)                       # DEBUG

        # print("TEST_TWO: closing")
        sys.stdout.flush()

        # -- close --------------------------------------------------
        mgr.close()

        # -- test our expectations ----------------------------------
        expected_log_file = os.path.join(path_to_logs, 'foo.log')
        self.assertEqual(expected_log_file, foo_log.log_file_name)
        self.assertTrue(os.path.exists(expected_log_file))
        with open(expected_log_file, 'r') as file:
            contents = file.read()
        contents = contents.strip()
        self.assertTrue(contents.endswith('oh hello, foo'))  # END FOO

        if bar_log:
            expected_log_file = os.path.join(path_to_logs, 'bar.log')
            self.assertEqual(expected_log_file, bar_log.log_file_name)
            self.assertTrue(os.path.exists(expected_log_file))
            with open(expected_log_file, 'r') as file:
                contents = file.read()
            contents = contents.strip()
            self.assertTrue(contents.endswith('oh hello, bar'))  # END BAR


if __name__ == '__main__':
    unittest.main()
