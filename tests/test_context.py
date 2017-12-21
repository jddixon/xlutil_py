#!/usr/bin/python3

# ~/dev/py/xlutil/testContext.py

# import os
# import threading
import time
import unittest
from rnglib import SimpleRNG
from xlutil import Context

RNG = SimpleRNG(time.time())


class TestContext(unittest.TestCase):

    def setUp(self):
        self.ctx = Context()

    def tearDown(self):
        pass

    # utility functions ---------------------------------------------

    # actual unit test(s) -------------------------------------------

    def test_context(self):
        pass

    def test_empty(self):
        self.assertIsNotNone(self.ctx)
        self.assertEqual(0, len(self.ctx))
        self.assertIsNone(self.ctx.parent)
        self.assertIsNone(self.ctx.lookup("foo"))

    def test_adding_nulls(self):
        try:
            self.ctx.bind(None, "bar")
            self.fail("bind with None name succeeded!")
        except Exception:
            pass  # success
        try:
            self.ctx.bind("foo", None)
            self.fail("bind with None object succeeded!")
        except Exception:
            pass  # success

    def test_simple_bindings(self):
        self.ctx.bind("foo", "that was foo")
        self.ctx.bind("bar", "that was bar")
        self.assertEqual(2, len(self.ctx))
        self.assertEqual("that was foo", self.ctx.lookup("foo"))
        self.assertEqual("that was bar", self.ctx.lookup("bar"))
        # __contains()__ and 'in' -------------------------
        self.assertTrue('foo' in self.ctx)
        self.assertTrue('bar' in self.ctx)
        self.assertFalse('baz' in self.ctx)
        # keys() method -----------------------------------
#       keyz = list(self.ctx.keys())
        self.assertTrue('bar' in list(self.ctx.keys()))
        self.assertFalse('baz' in list(self.ctx.keys()))

    def test_nested_contexts(self):
        child_ctx = Context(self.ctx)
        grand_child = Context(child_ctx)
        self.assertTrue(self.ctx == child_ctx.parent)
        self.assertTrue(child_ctx == grand_child.parent)

        # masking bindings
        self.ctx.bind("foo", "bar0")     # <-- should persist
        child_ctx.bind("foo", "bar1")
        grand_child.bind("foo", "bar2")
        self.assertEqual("bar2", grand_child.lookup("foo"))
        grand_child.unbind("foo")
        self.assertEqual("bar1", grand_child.lookup("foo"))

        child_ctx.unbind("foo")
        self.assertEqual("bar0", grand_child.lookup("foo"))
        self.ctx.unbind("foo")
        self.assertIsNone(grand_child.lookup("foo"))

        self.ctx.bind("wombat", "Freddy Boy")
        self.assertEqual("Freddy Boy", grand_child.lookup("wombat"))
        grand_child.parent = None
        self.assertIsNone(grand_child.parent)
        # broke chain of contexts
        self.assertIsNone(grand_child.lookup("wombat"))


if __name__ == '__main__':
    unittest.main()
