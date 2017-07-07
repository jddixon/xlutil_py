# xlutil/__init__.py

"""
Utility library for python XLattice packages.
"""

import time
from .context import Context

__version__ = '0.1.4'
__version_date__ = '2017-07-07'

__all__ = ['__version__', '__version_date__',
           'getUTCTimestamp', 'mkEpochFromUTC',
           'mkTimestamp', 'mkEpoch',       # CONSIDER ME DEPRECATED
           'popcount32', 'popcount64', 'dump_byte_slice',

           # classes
           'Context', 'Namespace',
           'XLUtilError',
           ]


class XLUtilError(RuntimeError):
    """ General purpose exception for the package. """

# -- NAME SPACE -----------------------------------------------------


class Namespace(dict):
    def __init__(self, pairs={}):
        super(Namespace, self).__init__(pairs)

    def __getattribute__(self, name):
        try:
            return self[name]
        except KeyError:
            errMsg = "'%s' object has no attribute '%s'" % (
                type(self).__name__, name)
            raise AttributeError(errMsg)

    def __setattr__(self, name, value):
        self[name] = value



# POPCOUNT ----------------------------------------------------------
"""
Utility library for python XLattice packages.

POPCOUNT

The 32- and 64-bit versions of the SWAR algorithm.  These are variants of
the code in Bagwell's "Ideal Hash Trees".  The algorithm seems to have been
created by the aggregate.org/MAGIC group at the University of Kentucky
earlier than the fall of 1996.  Illmari Karonen (vyznev.net) explains the
algorithm at
stackoverflow.com/questions/22081738/how-variable-precision-swar-algorithm-workds
"""


# These should best be uint32s.
OCTO_FIVES = 0x55555555
OCTO_THREES = 0x33333333
OCTO_ONES = 0x01010101
OCTO_FS = 0x0f0f0f0f

# And these uint64s
HEXI_FIVES = 0x5555555555555555
HEXI_THREES = 0x3333333333333333
HEXI_ONES = 0x0101010101010101
HEXI_FS = 0x0f0f0f0f0f0f0f0f


def popcount32(nnn):  # uint32 -> uint
    """ Count the number of bits set in a 32-bit value. """

    # nnn %= 0x100000000    # convert to uint32
    nnn = nnn - ((nnn >> 1) & OCTO_FIVES)
    nnn = (nnn & OCTO_THREES) + ((nnn >> 2) & OCTO_THREES)
    return (0xffffffff & (((nnn + (nnn >> 4)) & OCTO_FS) * OCTO_ONES)) >> 24


def popcount64(nnn):  # uint32 -> uint
    """ Count the number of bits set in a 64-bit value. """

    # nnn %= 0x10000000000000000    # convert to uint64
    nnn = nnn - ((nnn >> 1) & HEXI_FIVES)
    nnn = (nnn & HEXI_THREES) + ((nnn >> 2) & HEXI_THREES)
    return (0xffffffffffffffff & (
        ((nnn + (nnn >> 4)) & HEXI_FS) * HEXI_ONES)) >> 56


def dump_byte_slice(byte_str):            # -> str
    """ Convert a bytes-like object to a hex string. """
    sss = []
    for val in byte_str:
        sss.append("%02x" % val)

    return ''.join(sss)

# TIMESTAMP ---------------------------------------------------------


def getUTCTimestamp():
    """ returns the current UTC time as a CCYYMMDD-HHMMSS string"""
    return "%04d%02d%02d-%02d%02d%02d" % time.gmtime()[:6]


def mkEpochFromUTC(date_time):
    """
    Convert UTC timestamp to integer seconds since epoch.

    Using code should set
        os.environ['TZ'] = 'UTC'
    """
    pattern = '%Y%m%d-%H%M%S'
    return int(time.mktime(time.strptime(date_time, pattern)))


# CONSIDER ME DEPRECATED
mkEpoch = mkEpochFromUTC
mkTimestamp = getUTCTimestamp
# END DEPRECATED
