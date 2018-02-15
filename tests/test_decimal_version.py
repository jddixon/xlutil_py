#!/usr/bin/env python3
# testDecimalVersion.py

""" Test functions related to DecimalVersion class. """

import time
import unittest
import rnglib

from xlutil import DecimalVersion, parse_decimal_version


class TestDecimalVErsion(unittest.TestCase):
    """ Test functions related to DecimalVersion class. """

    def setUp(self):
        self.rng = rnglib.SimpleRNG(time.time())

    def tearDown(self):
        pass

    def test_empty(self):
        """ Verify that empty strings cannot be parsed. """

        try:
            parse_decimal_version(None)
            self.fail("parsed nil string")
        except RuntimeError:
            pass
        try:
            parse_decimal_version("")
            self.fail("parsed empty string")
        except RuntimeError:
            pass
        try:
            parse_decimal_version(" \t ")
            self.fail("parsed whitespace")
        except ValueError:
            pass

    def test4int_constructor(self):
        """ Test full 4-part constructor. """

        dv1 = DecimalVersion(1, 2, 3, 4)
        string = dv1.__str__()
        self.assertEqual("1.2.3.4", string)
        self.assertEqual(dv1.get_a(), 1)
        self.assertEqual(dv1.get_b(), 2)
        self.assertEqual(dv1.get_c(), 3)
        self.assertEqual(dv1.get_d(), 4)
        dv2 = parse_decimal_version(string)
        self.assertEqual(dv1.__eq__(dv2), True)
        self.assertEqual(dv1, dv2)

    def test3int_constructor(self):
        """ Test 3-part constructor (a.b.c). """

        dv1 = DecimalVersion(1, 2, 3)
        string = dv1.__str__()
        self.assertEqual("1.2.3", string)
        self.assertEqual(dv1.get_a(), 1)
        self.assertEqual(dv1.get_b(), 2)
        self.assertEqual(dv1.get_c(), 3)
        self.assertEqual(dv1.get_d(), 0)
        dv2 = parse_decimal_version(string)
        self.assertEqual(dv1.__eq__(dv2), True)
        self.assertEqual(dv1, dv2)

    def test2int_constructor(self):
        """ Test 2-part constructor (a.b). """

        dv1 = DecimalVersion(1, 2)
        string = dv1.__str__()
        self.assertEqual("1.2.0", string)
        self.assertEqual(dv1.get_a(), 1)
        self.assertEqual(dv1.get_b(), 2)
        self.assertEqual(dv1.get_c(), 0)
        self.assertEqual(dv1.get_d(), 0)
        dv2 = parse_decimal_version(string)
        self.assertEqual(dv1.__eq__(dv2), True)
        self.assertEqual(dv1, dv2)

    def test1int_constructor(self):
        """ Test construtor with only major version number. """

        dv1 = DecimalVersion(1)
        string = dv1.__str__()
        self.assertEqual("1.0.0", string)
        self.assertEqual(dv1.get_a(), 1)
        self.assertEqual(dv1.get_b(), 0)
        self.assertEqual(dv1.get_c(), 0)
        self.assertEqual(dv1.get_d(), 0)
        dv2 = parse_decimal_version(string)
        self.assertEqual(dv1.__eq__(dv2), True)
        self.assertEqual(dv1, dv2)

    def make_decimal_version(self):
        """ Creata a quasi-random 4-part version number. """

        v__ = self.rng.next_int32()
        a__ = 0xff & v__
        b__ = 0xff & (v__ >> 8)
        c__ = 0xff & (v__ >> 16)
        d__ = 0xff & (v__ >> 24)
        dver = DecimalVersion(a__, b__, c__, d__)
        self.assertEqual(dver.value, v__)
        self.assertEqual(a__, dver.get_a())
        self.assertEqual(b__, dver.get_b())
        self.assertEqual(c__, dver.get_c())
        self.assertEqual(d__, dver.get_d())

        return v__, a__, b__, c__, d__, dver

    def test_assigning_values(self):
        """ Test various forms of assignment. """

        v__, _, _, _, _, dver = self.make_decimal_version()

        # test int assignment
        dv2 = DecimalVersion()
        dv2.value = v__
        self.assertEqual(dv2.value, v__)
        self.assertEqual(dv2, dver)

        # test str assignment
        dv3 = DecimalVersion()
        dv3.value = dver.__str__()
        self.assertEqual(dv3.value, v__)
        self.assertEqual(dv3, dver)

        # test DecimalVersioen assignment
        dv4 = DecimalVersion()
        dv4.value = dver
        self.assertEqual(dv4.value, v__)
        self.assertEqual(dv4, dver)

    def test_stepping_major(self):
        """ Test stepping the major version number. """

        _, a__, _, _, _, dver = self.make_decimal_version()
        if a__ < 255:
            dver.step_major()
            self.assertEqual(dver.get_a(), a__ + 1)
            self.assertEqual(dver.get_b(), 0)
            self.assertEqual(dver.get_c(), 0)
            self.assertEqual(dver.get_d(), 0)
        else:
            try:
                dver.step_major()
                self.fail("didn't get exception stepping to 256")
            except RuntimeError:
                pass

    def test_stepping_minor(self):
        """ Test stepping the minor version number. """
        _, a__, b__, _, _, dver = self.make_decimal_version()
        if b__ < 255:
            dver.step_minor()
            self.assertEqual(dver.get_a(), a__)
            self.assertEqual(dver.get_b(), b__ + 1)
            self.assertEqual(dver.get_c(), 0)
            self.assertEqual(dver.get_d(), 0)
        else:
            try:
                dver.step_minor()
                self.fail("didn't get exception stepping to 256")
            except RuntimeError:
                pass

    def test_stepping_decimal(self):
        """ Test stepping the decimal (third part of) version number. """

        _, a__, b__, c__, _, dver = self.make_decimal_version()
        if c__ < 255:
            dver.step_decimal()
            self.assertEqual(dver.get_a(), a__)
            self.assertEqual(dver.get_b(), b__)
            self.assertEqual(dver.get_c(), c__ + 1)
            self.assertEqual(dver.get_d(), 0)
        else:
            try:
                dver.step_decimal()
                self.fail("didn't get exception stepping to 256")
            except RuntimeError:
                pass

    def test_stepping_micro(self):
        """ Test stepping the micro (fourth part of) version number. """

        _, a__, b__, c__, d__, dver = self.make_decimal_version()
        if d__ < 255:
            dver.step_micro()
            self.assertEqual(dver.get_a(), a__)
            self.assertEqual(dver.get_b(), b__)
            self.assertEqual(dver.get_c(), c__)
            self.assertEqual(dver.get_d(), d__ + 1)
        else:
            try:
                dver.step_micro()
                self.fail("didn't get exception stepping to 256")
            except RuntimeError:
                pass

    def test_booleans(self):
        """ Verify relops return expected values."""

        # test __eq__()
        v1_, _, _, _, _, dv1 = self.make_decimal_version()
        self.assertEqual(dv1, dv1)
        v2_, _, _, _, _, dv2 = self.make_decimal_version()
        self.assertEqual(dv2, dv2)
        while v1_ == v2_:
            v2_, _, _, _, _, dv2 = self.make_decimal_version()
            self.assertEqual(dv2, dv2)
        self.assertNotEqual(dv1, dv2)

        # test __lt__() ---------------------------------------------
        self.assertFalse(dv1 < dv1)
        self.assertFalse(dv2 < dv2)

        x__ = DecimalVersion(1, 2, 3, 4)
        y__ = DecimalVersion(1, 2, 3, 5)
        self.assertTrue(x__ < y__)
        self.assertFalse(y__ < x__)

        x__ = DecimalVersion(1, 2, 3, 4)
        y__ = DecimalVersion(1, 3, 4, 5)
        self.assertTrue(x__ < y__)
        self.assertFalse(y__ < x__)

        x__ = DecimalVersion(1, 2, 3, 4)
        y__ = DecimalVersion(2, 2, 4, 5)
        self.assertTrue(x__ < y__)
        self.assertFalse(y__ < x__)

        x__ = DecimalVersion(1, 2, 3, 4)
        y__ = DecimalVersion(1, 2, 4, 5)
        self.assertTrue(x__ < y__)
        self.assertFalse(y__ < x__)

        # test __le__() ---------------------------------------------
        self.assertTrue(dv1 <= dv1)
        self.assertTrue(dv2 <= dv2)

        x__ = DecimalVersion(1, 2, 3, 4)
        y__ = DecimalVersion(1, 2, 3, 5)
        self.assertTrue(x__ <= y__)

        x__ = DecimalVersion(1, 2, 3, 4)
        y__ = DecimalVersion(1, 3, 4, 5)
        self.assertTrue(x__ <= y__)

        x__ = DecimalVersion(1, 2, 3, 4)
        y__ = DecimalVersion(2, 2, 4, 5)
        self.assertTrue(x__ <= y__)

        x__ = DecimalVersion(1, 2, 3, 4)
        y__ = DecimalVersion(1, 2, 4, 5)
        self.assertTrue(x__ <= y__)

        # test __gt__() ---------------------------------------------
        self.assertFalse(dv1 > dv1)
        self.assertFalse(dv2 > dv2)

        x__ = DecimalVersion(1, 2, 3, 6)
        y__ = DecimalVersion(1, 2, 3, 5)
        self.assertTrue(x__ > y__)
        self.assertFalse(y__ > x__)

        x__ = DecimalVersion(1, 2, 5, 4)
        y__ = DecimalVersion(1, 2, 4, 5)
        self.assertTrue(x__ > y__)
        self.assertFalse(y__ > x__)

        x__ = DecimalVersion(1, 3, 5, 4)
        y__ = DecimalVersion(1, 2, 4, 5)
        self.assertTrue(x__ > y__)
        self.assertFalse(y__ > x__)

        x__ = DecimalVersion(2, 2, 3, 4)
        y__ = DecimalVersion(1, 2, 4, 5)
        self.assertTrue(x__ > y__)
        self.assertFalse(y__ > x__)

        # test __ge__() ---------------------------------------------
        self.assertTrue(dv1 >= dv1)
        self.assertTrue(dv2 >= dv2)

        x__ = DecimalVersion(1, 2, 3, 6)
        y__ = DecimalVersion(1, 2, 3, 5)
        self.assertTrue(x__ >= y__)

        x__ = DecimalVersion(1, 2, 7, 4)
        y__ = DecimalVersion(1, 2, 4, 5)
        self.assertTrue(x__ >= y__)

        x__ = DecimalVersion(1, 5, 3, 4)
        y__ = DecimalVersion(1, 2, 4, 5)
        self.assertTrue(x__ >= y__)

        x__ = DecimalVersion(21, 2, 3, 4)
        y__ = DecimalVersion(1, 2, 4, 5)
        self.assertTrue(x__ >= y__)


if __name__ == '__main__':
    unittest.main()
