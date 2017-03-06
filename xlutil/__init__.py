# xlutil/__init__.py

""" Util library for python XLattice packages. """

__version__ = '0.0.2'
__version_date__ = '2017-03-06'

__all__ = ['__version__', '__version_date__', 'XLUtilError', ]


class XLUtilError(RuntimeError):
    """ General purpose exception for the package. """
