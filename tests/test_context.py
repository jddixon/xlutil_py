#!/usr/bin/python3

# ~/dev/py/xlutil/testContext.py

# import os
# import threading
import time
import unittest
from rnglib import SimpleRNG
from xlutil import Context

rng = SimpleRNG(time.time())


class TestContext (unittest.TestCase):

    def setUp(self):
        self.ctx = Context()

    def tearDown(self):
        pass

    # utility functions ---------------------------------------------

    # actual unit test(s) -------------------------------------------

    def testContext(self):
        pass

    def testEmpty(self):
        self.assertIsNotNone(self.ctx)
        self.assertEqual(0, len(self.ctx))
        self.assertIsNone(self.ctx.parent)
        self.assertIsNone(self.ctx.lookup("foo"))

    def testAddingNulls(self):
        try:
            self.ctx.bind(None, "bar")
            self.fail("bind with None name succeeded!")
        except Exception as e:
            pass  # success
        try:
            self.ctx.bind("foo", None)
            self.fail("bind with None object succeeded!")
        except Exception as e:
            pass  # success

    def testSimpleBindings(self):
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

    def testNestedContexts(self):
        childCtx = Context(self.ctx)
        grandChild = Context(childCtx)
        self.assertTrue(self.ctx == childCtx.parent)
        self.assertTrue(childCtx == grandChild.parent)

        # masking bindings
        self.ctx.bind("foo", "bar0")     # <-- should persist
        childCtx.bind("foo", "bar1")
        grandChild.bind("foo", "bar2")
        self.assertEqual("bar2", grandChild.lookup("foo"))
        grandChild.unbind("foo")
        self.assertEqual("bar1", grandChild.lookup("foo"))

        childCtx.unbind("foo")
        self.assertEqual("bar0", grandChild.lookup("foo"))
        self.ctx.unbind("foo")
        self.assertIsNone(grandChild.lookup("foo"))

        self.ctx.bind("wombat", "Freddy Boy")
        self.assertEqual("Freddy Boy", grandChild.lookup("wombat"))
        grandChild.parent = None
        self.assertIsNone(grandChild.parent)
        # broke chain of contexts
        self.assertIsNone(grandChild.lookup("wombat"))


if __name__ == '__main__':
    unittest.main()
