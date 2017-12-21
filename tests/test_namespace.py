#!/usr/bin/python3

# ~/dev/py/xlutil/testNamespace.py

import time
import unittest
from rnglib import SimpleRNG
from xlutil import Namespace

RNG = SimpleRNG(time.time())


class TestNamespace(unittest.TestCase):
    next_seq_nbr = 0

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # utility functions ---------------------------------------------

    def msg_values(self):
        """ returns a list """

        timestamp = int(time.time())
        seq_nbr = TestNamespace.next_seq_nbr
        TestNamespace.next_seq_nbr += 1     # used, so increment it

        zone_name = RNG.next_file_name(8)
        expected_serial = RNG.next_int32()
        actual_serial = RNG.next_int32()
        while actual_serial == expected_serial:
            actual_serial = RNG.next_int32()

        # NOTE that this is a list
        return [timestamp, seq_nbr, zone_name, expected_serial, actual_serial]

    # actual unit test(s) -------------------------------------------

    def test_a_namespace(self):

        now = int(time.time())
        options = {}                # what we convert into a namespace of sorts
        options['just_show'] = True  # False
        options['log_dir'] = 'logs'
        options['port'] = 55555
        options['show_timestamp'] = False
        options['show_version'] = False
        options['testing'] = False
        options['timestamp'] = now
        options['verbose'] = True  # False

        ns_ = Namespace(options)

        self.assertTrue(ns_.just_show)
        self.assertEqual('logs', ns_.log_dir)
        self.assertEqual(55555, ns_.port)
        self.assertFalse(ns_.show_timestamp)
        self.assertFalse(ns_.show_version)
        self.assertFalse(ns_.testing)
        self.assertEqual(now, ns_.timestamp)
        self.assertTrue(ns_.verbose)


if __name__ == '__main__':
    unittest.main()
