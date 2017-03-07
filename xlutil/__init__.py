# xlutil/__init__.py

""" Util library for python XLattice packages. """

__version__ = '0.1.0'
__version_date__ = '2017-03-07'

__all__ = ['__version__', '__version_date__',
           'popcount32', 'popcount64', 'dump_byte_slice',
           'XLUtilError', ]


class XLUtilError(RuntimeError):
    """ General purpose exception for the package. """


"""
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


def popcount32(n):  # uint32 -> uint
    n %= 0x100000000    # convert to uint32
    n = n - ((n >> 1) & OCTO_FIVES)
    n = (n & OCTO_THREES) + ((n >> 2) & OCTO_THREES)
    return (0xffffffff & (((n + (n >> 4)) & OCTO_FS) * OCTO_ONES)) >> 24


def popcount64(n):  # uint32 -> uint
    n %= 0x10000000000000000    # convert to uint64
    n = n - ((n >> 1) & HEXI_FIVES)
    n = (n & HEXI_THREES) + ((n >> 2) & HEXI_THREES)
    return (0xffffffffffffffff & (((n + (n >> 4)) & HEXI_FS) * HEXI_ONES)) >> 56


def dump_byte_slice(slice):            # -> str
    ss = ''
    for char in slice:
        ss.append("%02x", char)

    return ''.join(ss)
