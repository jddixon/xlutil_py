#!/usr/bin/python3

# ~/dev/py/xlutil/testNamespace.py

import os
import threading
import time
import unittest
from rnglib import SimpleRNG
from xlutil import Namespace

rng = SimpleRNG(time.time())


class TestNamespace (unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # utility functions ---------------------------------------------

    def msgValues(self):
        """ returns a list """
        global nextSeqNbr

        timestamp = int(time.time())
        seqNbr = nextSeqNbr
        nextSeqNbr += 1     # used, so increment it

        zoneName = rng.nextFileName(8)
        expectedSerial = rng.nextInt32()
        actualSerial = rng.nextInt32()
        while actualSerial == expectedSerial:
            actualSerial = rng.nextInt32()

        # NOTE that this is a list
        return [timestamp, seqNbr, zoneName, expectedSerial, actualSerial]

    # actual unit test(s) -------------------------------------------

    def testANamespace(self):

        now = int(time.time())
        options = {}                # what we convert into a namespace of sorts
        options['justShow'] = True  # False
        options['logDir'] = 'logs'
        options['port'] = 55555
        options['showTimestamp'] = False
        options['showVersion'] = False
        options['testing'] = False
        options['timestamp'] = now
        options['verbose'] = True  # False

        ns = Namespace(options)

        self.assertTrue(ns.justShow)
        self.assertEqual('logs', ns.logDir)
        self.assertEqual(55555, ns.port)
        self.assertFalse(ns.showTimestamp)
        self.assertFalse(ns.showVersion)
        self.assertFalse(ns.testing)
        self.assertEqual(now, ns.timestamp)
        self.assertTrue(ns.verbose)


if __name__ == '__main__':
    unittest.main()
