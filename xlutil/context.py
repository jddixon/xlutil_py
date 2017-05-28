# ~/dev/py/xlutil/xlutil/context.py

import threading


class Context(object):

    """
    A naming context consisting of a possibly nested set of name-to-object
    bindings.  If there is a parent context and a key cannot be resolved
    in this context, an attempt will be made to resolve it in the parent,
    recursively.

    Names added to the context must not be null.

    This implementation is intended to be thread-safe.
    """

    def __init__(self, parent=None, **kwargs):
        if parent is not None and not isinstance(parent, Context):
            raise ValueError('parent must be a Context')
        self._parent = parent            # may of course be None
        if kwargs:
            self._ctx = {kwargs}
        else:
            self._ctx = {}
        self._ctxLock = threading.Lock()  # born free

    def bind(self, name, value):
        """
        Bind a name to an Object at this Context level.  Neither name
        nor object may be null.

        If this context has a parent, the binding at this level will
        mask any bindings in the parent and above.

        @param name the name being bound
        @param o    the Object it is bound to
        @throws IllegalArgumentException if either is null.
        """
        if name is None:
            raise ValueError('name may not be None')
        if value is None:
            raise ValueError('value may not be None')
        self._ctxLock.acquire()
        self._ctx[name] = value
        self._ctxLock.release()
        return self                 # to support chaining

    def lookup(self, name):
        """
        Looks up a name recursively.  If the name is bound at this level,
        the object it is bound to is returned.  Otherwise, if there is
        a parent Context, the value returned by a lookup in the parent
        Context is returned.  If there is no parent and no match, returns
        None.

        @param name the name we are attempting to match
        @return     the value the name is bound to at this or a higher level
                    or null if there is no such value
        """
        if name is None:
            raise ValueError('name may not be None')
        value = None
        try:
            self._ctxLock.acquire()
            try:
                value = self._ctx[name]
            except KeyError as ke:
                if self._parent is not None:
                    value = self._parent.lookup(name)
        finally:
            self._ctxLock.release()
        return value

    def unbind(self, name):
        """
        Remove a binding from the Context.  If there is no such binding,
        silently ignore the request.  Any binding at a higher level, in
        the parent Context or above, is unaffected by this operation.

        @param name Name to be unbound.
        """
        if name is None:
            raise ValueError('name may not be None')
        try:
            self._ctxLock.acquire()
            del self._ctx[name]
        finally:
            self._ctxLock.release()

    def __contains__(self, whatever):
        """
        Support for 'in'.  However, this only considers the dictionary
        at this level.
        """
        retVal = False
        if whatever is not None:
            self._ctxLock.acquire()
            retVal = whatever in self._ctx
            self._ctxLock.release()
        return retVal

    def keys(self):
        """
        Returns an unordered list of keys from the dictionary at this
        level, locking the dictionary for the time required to copy
        the list of keys.
        """
        retVal = None
        self._ctxLock.acquire()
        retVal = list(self._ctx.keys())
        self._ctxLock.release()
        return retVal

    def __len__(self):
        self._ctxLock.acquire()
        val = len(self._ctx)
        self._ctxLock.release()
        return val

    @property
    def parent(self): return self._parent     # may be None

    @parent.setter
    def parent(self, newParent):
        """
        Change the parent Context.

        @param  newParent New parent Context, possibly null.
        """
        if newParent is not None and not isinstance(newParent, Context):
            raise ValueError('new parent must be a Context or None')
        self._ctxLock.acquire()
        self._parent = newParent
        self._ctxLock.release()

    def flush(self):
        pass
