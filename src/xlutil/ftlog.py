# xlattice_py/xlattice/ftLog.py

""" Fault-tolerant log classes and methods. """

import os
import time

# pylint: disable=no-name-in-module
from cFTLogForPy import(
    init_cft_logger, open_cft_log, log_msg, close_cft_logger)


__all__ = ['LogEntry', 'ActualLog', 'LogMgr', ]

# The first line of a chained log is a LogEntry pointing back to
# the previous chunk of the log; its key is the content key of that
# log in U.

# See upax_go/entry.go and entry_test.go


class LogEntry(object):
    """ A fault-tolerant log entry. """

    def __init__(self,
                 tstamp,         # integer timestamp, either 32 or 64 bits
                 key,            # content key, 20 or 32 bytes
                 owner,          # nodeID, 20 or 32 bytes
                 length,         # uint32 length of content, octets
                 src,            # aka 'by'
                 path):          # path relative to project root

        self._tstamp = tstamp
        self._key = key
        self._owner = owner,
        self._length = length
        self._src = src
        self._path = path

    @property
    def tstamp(self):
        """ Return the time at which the logged event occurred. """
        return self._tstamp

    @property
    def key(self):
        """ Return the content key, the SHA1 hash, of the file concerned. """
        return self._key

    @property
    def owner(self):
        """
        Return the 40- or 64-hex sequence identifying who is doing the
        logging.
        """
        return self._owner

    @property
    def length(self):
        """ Return the length of the file. """
        return self._length

    @property
    def src(self):
        """
        Return the 40- or 64-hex sequence identifying the user responsible
        for the file.
        """
        return self._src

    @property
    def path(self):
        """ Return the relative POSIX path to the file, including its name."""
        return self._path

    def __eq__(self, other):
        """ Whether this log entry equals another. """
        if not isinstance(other, LogEntry):
            return False
        return self._tstamp == other.tstamp and\
            self._key == other.key and\
            self._owner == other.owner and\
            self._length == other.length and\
            self._src == other.src and\
            self._path == other.path


# -------------------------------------------------------------------
class ActualLog(object):
    """ Maintains information about each open log """

    def __init__(self, base_name, mgr):
        """
        Creates a new access log. The caller guarantees that the
        base name is unique.
        """
        # __slots__ = { '__baseName',
        self._base_name = base_name
        self._mgr = mgr
        self._log_file = os.path.join(mgr.log_dir, base_name + '.log')
        self._lfd = None

        # we pass the full path name
        self.name_copy = self._log_file.strip()   # should copy the string
        # DEBUG
        # print("trying to open log with path '%s'" % self.nameCopy)
        # END
        lfd = open_cft_log(self.name_copy)
        if lfd < 0:
            raise RuntimeError("ERROR: init_cft_logger returns %d", lfd)
        else:
            # DEBUG
            # print("opened %s successfully with lfd %d" % (
            #   self._log_file, lfd))
            # END
            self._lfd = lfd

    @property
    def base_name(self):
        """ Return the file name, excluding any path information. """
        return self._base_name

    @property
    def lfd(self):
        """ Return the file handle if the directory is open. """
        return self._lfd

    @property
    def log_file(self):
        """ Return the path to the log file, including the file name. """
        return self._log_file

    @property
    def mgr(self):
        """ Return the manager responsible for the log. """
        return self._mgr

    def log(self, msg):
        """ Log a message. """
        now = time.localtime()
        date = time.strftime('%Y-%m-%d', now)
        hours = time.strftime('%H:%M:%S', now)
        text = '%s %s %s\n' % (date, hours, msg)
        # note that this is a tuple
        # status =
        log_msg(self._lfd, text)

        # XXX handle possible errors

#       # DEBUG Python3-style
#       print ("message is: '%s'",  text)
#       # END
        return text

    @property
    def log_file_name(self):
        """ Return a copy of the log file's name. """
        return self.name_copy


class LogMgr(object):
    """ Log manager. """

    def __init__(self, log_dir='logs'):

        # __slots__ = { }

        # a map indexed by the base name of the log
        self._log_map = {}
        self._log_dir = log_dir

        # THIS IS A PARTIAL FIX: the above assumes that all logs
        # share the same directory
        # status =
        init_cft_logger()

    def open(self, base_name):
        """ Open the log, possibly creating it. """

        if base_name in self._log_map:
            raise ValueError('log named %s already exists' % base_name)
        log_handle = ActualLog(base_name, self)
        if log_handle:
            self._log_map[base_name] = log_handle
            # DEBUG
            # print("log_handle for %s is %s" % (baseName, str(log_handle)))
            # END
            return log_handle

    def close(self):
        """ Closes all log files. """
        self._log_map = {}
        # print("BRANCHING TO closeClogger()") ; sys.stdout.flush();
        return close_cft_logger(None)

    @property
    def log_dir(self):
        """ Return a path to the log directory. """
        return self._log_dir
