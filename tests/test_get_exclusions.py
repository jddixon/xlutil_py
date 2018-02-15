#!/usr/bin/env python3
# test_get_exclusions.py

""" Test the glob/wildcard functions in xlattice/util.py """

import time
import unittest

from xlutil import get_exclusions, make_ex_re
from rnglib import SimpleRNG


class TestGetExclusions(unittest.TestCase):
    """ Test the glob/wildcard functions in xlattice/util.py """

    def setUp(self):
        self.rng = SimpleRNG(time.time())                 # XXX NOT USED

    def tearDown(self):
        pass

    def do_test_expected_exclusions(self, exre):
        """ Should always match. """
        self.assertIsNotNone(exre.match('merkle.pyc'))
        self.assertIsNotNone(exre.match('.svn'))
        self.assertIsNotNone(exre.match('.foo.swp'))       # vi backup file
        self.assertIsNotNone(exre.match('junkEverywhere'))  # note 'junk'
        self.assertIsNotNone(exre.match('.merkle'))

    def do_test_expected_matches(self, match_re, names):
        """ Should always match. """
        for name in names:
            self.assertIsNotNone(match_re.match(name))

    def do_test_expected_match_failures(self, match_re, names):
        """ Should never match. """
        for name in names:
            m__ = match_re.match(name)
            if m__:
                print("WE HAVE A MATCH ON '%s'" % name)
            # self.assertEquals( None, where )

    def do_test_get_exclusions(self, proj_dir):
        """
        This test assumes that there is a local .gitignore containing
        at least '.merkle', '.svn*' '*.swp', and 'junk*'
        """

        # convert .gitignore's contents to a list of parenthesized
        # regular expressions
        globs = get_exclusions(proj_dir, '.gitignore')
        self.assertIsNotNone(len(globs) > 0)

        exre = make_ex_re(globs)
        self.assertIsNotNone(exre is not None)
        self.do_test_expected_exclusions(exre)

    def test_get_exclusions(self):
        """ Exercise get_exclusions and related functions. """
        self.do_test_get_exclusions('.')


if __name__ == '__main__':
    unittest.main()
