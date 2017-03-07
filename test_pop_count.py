#!/usr/bin/env python3
# xlutil_py/test_pop_count.py

""" Test the pop_count (aka SWAR) functions. """

#import hashlib
#import os
import time
import unittest

from rnglib import SimpleRNG
from xlutil import popcount32, popcount64, dump_byte_slice


class TestPopCount(unittest.TestCase):
    """ Test the pop_count (aka SWAR) functions. """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    def slow_popcount32(self, n):  # uint32 -> uint
        count = 0                   # uint, we trust
        for ndx in range(32):
            count += n & 1
            n >>= 1
        return count

    def slow_popcount64(self, n):      # uint64 -> uint
        count = 0
        for ndx in range(64):
            count += n & 1
            n >>= 1
        return count

    def crude_popcount32(self, signed):
        unsigned = signed % 0x100000000
        return bin(unsigned).count('1')

    def crude_popcount64(self, signed):
        unsigned = signed % 0x10000000000000000
        return bin(unsigned).count('1')

    def test_swar32low_order(self):
        self.assertEqual(popcount32(0x00000000), 0)
        self.assertEqual(popcount32(0x00000001), 1)
        self.assertEqual(popcount32(0x00000002), 1)
        self.assertEqual(popcount32(0x00000003), 2)
        self.assertEqual(popcount32(0x00000007), 3)
        self.assertEqual(popcount32(0x0000000f), 4)
        self.assertEqual(popcount32(0x0000001f), 5)
        self.assertEqual(popcount32(0x0000003f), 6)
        self.assertEqual(popcount32(0x0000007f), 7)
        self.assertEqual(popcount32(0x000000ff), 8)

        self.assertEqual(popcount32(0x00000100), 1)
        self.assertEqual(popcount32(0x00000101), 2)

        self.assertEqual(popcount32(0x000001ff), 9)
        self.assertEqual(popcount32(0x000003ff), 10)
        self.assertEqual(popcount32(0xffffffff), 32)

    def test_swar32(self):
        for ndx in range(8):
            n = self.rng.next_int32()
            slow_count = self.slow_popcount32(n)
            swar32count = popcount32(n)
            crude_count = self.crude_popcount32(n)
            # DEBUG
            #print("%d: n = %x" % (ndx, n))
            #print("    slow_count:  %d" % slow_count)
            #print("    crude_count: %d" % crude_count)
            #print("    swar32count: %d" % swar32count)
            # print()
            # END
            self.assertEqual(swar32count, slow_count)
            self.assertEqual(swar32count, crude_count)

    def test_swar64low_order(self):
        self.assertEqual(popcount64(0x0000000000000000), 0)
        self.assertEqual(popcount64(0x0000000000000001), 1)
        self.assertEqual(popcount64(0x0000000000000002), 1)
        self.assertEqual(popcount64(0x0000000000000003), 2)
        self.assertEqual(popcount64(0x0000000000000007), 3)
        self.assertEqual(popcount64(0x000000000000000f), 4)
        self.assertEqual(popcount64(0x000000000000001f), 5)
        self.assertEqual(popcount64(0x000000000000003f), 6)
        self.assertEqual(popcount64(0x000000000000007f), 7)
        self.assertEqual(popcount64(0x00000000000000ff), 8)
        self.assertEqual(popcount64(0x00000000000001ff), 9)
        self.assertEqual(popcount64(0x00000000000003ff), 10)
        self.assertEqual(popcount64(0x00000000000007ff), 11)
        self.assertEqual(popcount64(0x0000000000000fff), 12)
        self.assertEqual(popcount64(0xffffffffffffffff), 64)

    def test_swar64(self):
        for ndx in range(8):
            n1 = self.rng.next_int64()
            n2 = self.rng.next_int64()
            n = (n1 << 32) ^ n2         # we want a full 64 random bits
            slow_count = self.slow_popcount64(n)
            swar64count = popcount64(n)
            crude_count = self.crude_popcount64(n)
            self.assertEqual(swar64count, slow_count)
            self.assertEqual(swar64count, crude_count)

if __name__ == '__main__':
    unittest.main()
