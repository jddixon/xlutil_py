#!/usr/bin/env python3
# xlattice_py/test_context.py

""" Verify the XLattice Context functions as expected. """

import unittest

from xlattice import Context


class TestContext(unittest.TestCase):
    """ Verify the XLattice Context functions as expected. """

    def setUp(self):
        self.ctx = Context()

    def tearDown(self):
        pass

    def test_empty(self):
        self.assertEqual(0, len(self.ctx))
        self.assertEqual(None, self.ctx.parent)
        self.assertEqual(None, self.ctx.lookup("foo"))

    def test_adding_nones(self):
        try:
            self.ctx.bind(None, "bar")
            self.fail("bind with None name succeeded!")
        except Exception:
            # success
            pass
        try:
            self.ctx.bind("foo", None)
            self.fail("bind with None object succeeded!")
        except Exception:
            # success
            pass

    def test_simple_bindings(self):
        self.ctx.bind("foo", "that was foo")
        self.ctx.bind("bar", "that was bar")
        self.assertEqual(2, self.ctx.size())
        self.assertEqual("that was foo", self.ctx.lookup("foo"))
        self.assertEqual("that was bar", self.ctx.lookup("bar"))

    def test_nested_contexts(self):
        ctx1 = Context(self.ctx)
        ctx2 = Context(ctx1)
        self.assertTrue(self.ctx == ctx1.parent)
        self.assertTrue(ctx1 == ctx2.parent)
        self.ctx.bind("foo", "bar0")
        ctx1.bind("foo", "bar1")
        ctx2.bind("foo", "bar2")
        self.assertEqual("bar2", ctx2.lookup("foo"))
        ctx2.unbind("foo")
        self.assertEqual("bar1", ctx2.lookup("foo"))
        ctx1.unbind("foo")
        self.assertEqual("bar0", ctx2.lookup("foo"))
        self.ctx.unbind("foo")
        self.assertIsNone(ctx2.lookup("foo"))

        self.ctx.bind("wombat", "Freddy Boy")
        self.assertEqual("Freddy Boy", ctx2.lookup("wombat"))
        # ctx99 = ctx2.parent = None
        ctx2.parent = None
        # self.assertEqual(ctx99, ctx2)
        self.assertIsNone(ctx2.parent)
        self.assertIsNone(ctx2.lookup("wombat"))  # broke chain of contexts


if __name__ == "__main__":
    unittest.main()
