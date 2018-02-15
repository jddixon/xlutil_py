# xlutil_py/src/xlutil/context.py

"""
The XLattice Context.

A naming context consisting of a possibly nested set of name-to-object
bindings.  If there is a parent context and a key cannot be resolved
in this context, an attempt will be made to resolve it in the parent,
recursively.

Names added to the context must not be None.

This implementation is intended to be thread-safe.
"""


class ContextError(RuntimeError):
    """ Handles Context-related exceptions. """

# Any reason to make this ABCMeta ?


class Context(object):
    """ The XLattice context. """

    def __init__(self, parent=None):
        """ Create a Context, optionally with a parent. """
        self._ctx = dict()
        self._parent = parent

    def synchronize(self):
        """
        TBD magic.

        This makes no sense as it is set out.
        """

    def bind(self, name, obj):        # -> Context
        """
        Bind a name to an Object at this Context level.  Neither name
        nor object may be None.

        If this context has a parent, the binding at this level will
        mask any bindings in the parent and above.

        @param name the name being bound
        @param o    the Object it is bound to
        @raises ContextError if either is None.
        """

        if name is None or obj is None:
            raise ContextError("name or object is None")
        self.synchronize()      # XXX needs to sync block
        self._ctx[name] = obj
        return self

    def lookup(self, name):          # -> object
        """
        Looks up a name recursively.  If the name is bound at this level,
        the object it is bound to is returned.  Otherwise, if there is
        a parent Context, the value returned by a lookup in the parent
        Context is returned.  If there is no parent and no match, returns
        None.

        @param name the name we are attempting to match
        @return     the value the name is bound to at this or a higher level
                    or None if there is no such value
        """
        if name is None:
            raise ContextError("name cannot be None")
        obj = None
        self.synchronize()
        if name in self._ctx:
            obj = self._ctx[name]
        elif self._parent is not None:
            obj = self._parent[name]
        return obj

    def unbind(self, name):        # -> None
        """
        Remove a binding from the Context.  If there is no such binding,
        silently ignore the request.  Any binding at a higher level, in
        the parent Context or above, is unaffected by this operation.

        @param name Name to be unbound.
        """
        self.synchronize()
        # XXX Need to sync on block
        if name is None:
            raise ContextError("name is None")
        # XXX will raise if not in dict
        del self._ctx[name]

    def size(self):                 # -> int
        """ Return the number of bindings at this level. """
        self.synchronize()          # XXX need to sync on block
        return len(self._ctx)

    @property
    def parent(self):
        """
        Return a reference to the parent Context or None if there is none.
        """
        return self._parent

    @parent.setter
    def parent(self, new_parent):
        """
        Change the parent Context. This method returns a reference to
        this instance, to allow method calls to be chained.

        @param  new_parent New parent Context, possibly None.
        Return a reference to the current Context
        """

        self._parent = new_parent
        return self
