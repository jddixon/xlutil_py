#!/usr/bin/env python3
# testProcLock.py

""" Test ProcLock functionality. """

import os
import unittest
import sys
# from rnglib import SimpleRNG
from xlattice.proc_lock import ProcLock, ProcLockError
sys.path.insert(0, 'build/lib.linux-x86_64-3.4')  # for the .so


class TestProcLock(unittest.TestCase):

    """ Test ProcLock functionality. """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_should_fail(self):
        """ Verify that things that should fail do fail. """

        try:
            my_pid = os.getpid()
            mgr = ProcLock('foo')
            self.assertEqual('/tmp/run/foo', mgr.full_path_to_name)
            self.assertEqual(my_pid, mgr.pid)
            self.assertEqual('/tmp/run/foo.pid', mgr.lock_file_name)
            self.assertTrue(os.path.exists(mgr.lock_file_name))
            with open(mgr.lock_file_name, 'r') as file:
                pid_in_file = file.read()
            self.assertEqual(str(my_pid), pid_in_file)

            mgr2 = None
            try:
                mgr2 = ProcLock('foo')
                self.fail('successfully got second lock on locked file')
            except ProcLockError:
                pass
            finally:
                if mgr2:
                    mgr2.unlock()
        finally:
            mgr.unlock()

    def test_should_succeed(self):
        """
        Verify that a lock file is created under /tmp/ and that the
        current PID is written to it.  There should be no errors.
        Verify that the lock file has been removed by the unlock()
        operation.
        """
        try:
            my_pid = os.getpid()
            mgr = ProcLock('foo')

            self.assertEqual('/tmp/run/foo', mgr.full_path_to_name)
            self.assertEqual(my_pid, mgr.pid)
            self.assertEqual('/tmp/run/foo.pid', mgr.lock_file_name)
            self.assertTrue(os.path.exists(mgr.lock_file_name))
            with open(mgr.lock_file_name, 'r') as file:
                pid_in_file = file.read()
            self.assertEqual(str(my_pid), pid_in_file)

        except ProcLockError as exc:
            self.fail("unexpected ProcLockError %s" % exc)
        finally:
            mgr.unlock()
        self.assertFalse(os.path.exists(mgr.lock_file_name))

    def do_double_lock(self, a_path, b_path):
        """ Verify that overlapped locking of the two strings works. """

        # pid = os.getpid()
        a_mgr = ProcLock(a_path)
        b_mgr = ProcLock(b_path)
        a_mgr.unlock()
        b_mgr.unlock()

    def test_distinct_paths(self):
        """ Test non-overlapping relative paths. """
        self.do_double_lock('a/b/c', 'd/e/f')

    def test_shared_paths(self):
        """ Test overlapping relative paths. """
        self.do_double_lock('a/b/c', 'a/b/c/d/e/f')

    def test_absolute_paths(self):
        """ Test both types of absolute paths. """
        self.do_double_lock('/p/q/r', '/s/t/u')     # distinct
        self.do_double_lock('/u/v', '/u/v/w/x')     # shared


if __name__ == '__main__':
    unittest.main()
