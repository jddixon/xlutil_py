#!/usr/bin/env python3
# testRegexesFromWildcards.py

""" test generation of regular expressions from wildcards (globs) """

import time
import unittest
from rnglib import SimpleRNG
from xlutil import make_ex_re, make_match_re
# , regexes_from_wildcards      # NOT TESTED


class TestRegexesFromWildcards(unittest.TestCase):
    """ test generation of regular expressions from wildcards (globs) """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################

    def do_test_expected_matches(self, match_re, names):
        """ Verify that matches succeed for all names. """
        for name in names:
            self.assertIsNotNone(match_re.match(name))

    def do_test_expected_match_failures(self, match_re, names):
        """ Verify that matches fail for all names. """
        for name in names:
            m__ = match_re.match(name)
            self.assertIsNone(m__)

    def do_test_expected_exclusions(self, ex_re):
        """ Verify that names are not matched. """
        self.assertIsNotNone(ex_re.match('foolish'))
        self.assertIsNotNone(ex_re.match('superbar'))
        self.assertIsNotNone(ex_re.match('junky'))
        self.assertIsNotNone(ex_re.match('.merkle'))
        self.assertIsNotNone(ex_re.match('foo.pyc'))

    def test_make_ex_re(self):
        """test utility for making excluded file name regexes"""
        ex_re = make_ex_re(None)
        self.assertTrue(ex_re is not None)

        # should not be present
        self.assertIsNone(ex_re.match('bar'))
        self.assertIsNone(ex_re.match('foo'))

        exc = []
        exc.append('foo*')
        exc.append('*bar')
        exc.append('junk*')
        exc.append('.merkle')
        exc.append('*.pyc')
        ex_re = make_ex_re(exc)
        self.do_test_expected_exclusions(ex_re)

        self.assertIsNotNone(ex_re.match('foobarf'))
        self.assertIsNone(ex_re.match(' foobarf'))      # leading space

        self.assertIsNotNone(ex_re.match('ohMybar'))

        self.assertIsNone(ex_re.match('ohMybarf'))
        self.assertIsNotNone(ex_re.match('junky'))
        self.assertIsNone(ex_re.match(' junk'))

    def test_make_match_re(self):
        """test utility for making matched file name regexes"""
        match_re = make_match_re(None)
        self.assertIsNotNone(match_re)

        matches = []
        matches.append('foo*')
        matches.append('*bar')
        matches.append('junk*')
        match_re = make_match_re(matches)
        self.do_test_expected_matches(
            match_re, ['foo', 'foolish', 'roobar', 'junky'])
        self.do_test_expected_match_failures(
            match_re, [' foo', 'roobarf', 'myjunk'])
        # [ 'roobarf', 'myjunk'])

        matches = ['*.tgz']
        match_re = make_match_re(matches)
        self.do_test_expected_matches(
            match_re, ['junk.tgz', 'notSoFoolish.tgz'])
        self.do_test_expected_match_failures(
            match_re, ['junk.tar.gz', 'foolish.tar.gz'])

        matches = ['*.tgz', '*.tar.gz']
        match_re = make_match_re(matches)
        self.do_test_expected_matches(
            match_re,
            ['junk.tgz', 'notSoFoolish.tgz',
             'junk.tar.gz', 'ohHello.tar.gz'])
        self.do_test_expected_match_failures(
            match_re, ['junk.gz', 'foolish.tar'])


if __name__ == '__main__':
    unittest.main()
