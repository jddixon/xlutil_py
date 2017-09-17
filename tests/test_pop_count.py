#!/usr/bin/env python3
# xlutil_py/test_pop_count.py

""" Test the pop_count (aka SWAR) functions. """

import time
import unittest

from rnglib import SimpleRNG
from xlutil import popcount32, popcount64   # , dump_byte_slice


class TestPopCount(unittest.TestCase):
    """ Test the pop_count (aka SWAR) functions. """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    @staticmethod
    def slow_popcount32(nnn):       # uint32 -> uint
        """ count the bits one by one, 32-bit version """
        count = 0                       # uint, we trust
        for _ in range(32):
            count += nnn & 1
            nnn >>= 1
        return count

    @staticmethod
    def slow_popcount64(nnn):    # uint64 -> uint
        """ count the bits one by one, 64-bit version """
        count = 0
        for _ in range(64):
            count += nnn & 1
            nnn >>= 1
        return count

    @staticmethod
    def crude_popcount32(signed):
        """ count bits as 1s in string, 32-bit version """
        unsigned = signed % 0x100000000
        return bin(unsigned).count('1')

    @staticmethod
    def crude_popcount64(signed):
        """ count bits as 1s in string, 64-bit version """
        unsigned = signed % 0x10000000000000000
        return bin(unsigned).count('1')

    def test_swar32specific_cases(self):
        """
        Verify we get expected results for specific cases, 32-bit version.
        """

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
        """
        Verify we get expected results for random values, 32-bit version.
        """
        for _ in range(16):
            nnn = self.rng.next_int32()
            slow_count = self.slow_popcount32(nnn)
            swar32count = popcount32(nnn)
            crude_count = self.crude_popcount32(nnn)
            # DEBUG
            # print("%d: n = %x" % (ndx, nnn))
            # print("    slow_count:  %d" % slow_count)
            # print("    crude_count: %d" % crude_count)
            # print("    swar32count: %d" % swar32count)
            # print()
            # END
            self.assertEqual(swar32count, slow_count)
            self.assertEqual(swar32count, crude_count)

    def test_swar64specific_cases(self):
        """
        Verify we get expected results for specific cases, 64-bit version.
        """
        self.assertEqual(popcount64(0x0000000000000000), 0)
        self.assertEqual(popcount64(0x0000000000000001), 1)
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
        self.assertEqual(popcount64(0x0000000000001fff), 13)

        self.assertEqual(popcount64(0x1fffffffffffffff), 61)
        self.assertEqual(popcount64(0x3fffffffffffffff), 62)
        self.assertEqual(popcount64(0x7fffffffffffffff), 63)
        self.assertEqual(popcount64(0xffffffffffffffff), 64)

        self.assertEqual(popcount64(0x1000000000000000), 1)
        self.assertEqual(popcount64(0x3000000000000000), 2)
        self.assertEqual(popcount64(0x7000000000000000), 3)
        self.assertEqual(popcount64(0x8000000000000000), 1)
        self.assertEqual(popcount64(0xa000000000000000), 2)
        self.assertEqual(popcount64(0xe000000000000000), 3)
        self.assertEqual(popcount64(0xf000000000000000), 4)

    def test_swar64(self):
        """
        Verify we get expected results for random values, 64-bit version.
        """
        for _ in range(16):
            nn1 = self.rng.next_int64()
            nn2 = self.rng.next_int64()
            nnn = (nn1 << 32) ^ nn2         # we want a full 64 random bits
            slow_count = self.slow_popcount64(nnn)
            swar64count = popcount64(nnn)
            crude_count = self.crude_popcount64(nnn)
            self.assertEqual(swar64count, slow_count)
            self.assertEqual(swar64count, crude_count)


if __name__ == '__main__':
    unittest.main()
