#!/usr/bin/python3
# xlutil_py/setup.py

""" Setuptools project configuration for xlutil_py. """

from os.path import exists
# from setuptools import setup, Extension
from distutils.core import setup, Extension

MODULE1 = Extension('cFTLogForPy',
                    ['src/extsrc/cFTLogForPy.c',
                     'src/extsrc/evLoop.c',
                     'src/extsrc/logBufs.c',
                     'src/extsrc/modFunc.c',
                     'src/extsrc/threading.c', ],
                    include_dirs=['/usr/include/python3.6m',
                                  '/usr/include', ],
                    libraries=['ev', ],
                    library_dirs=['/usr/local/lib', ],)

LONG_DESC = None
if exists('README.md'):
    with open('README.md', 'r') as file:
        LONG_DESC = file.read()

setup(name='xlutil_py',
      version='0.2.1',
      author='Jim Dixon',
      author_email='jddixon@gmail.com',
      long_description=LONG_DESC,
      packages=['xlutil'],
      package_dir={'': 'src'},
      py_modules=[],
      include_package_data=False,
      zip_safe=False,
      scripts=[],
      ext_modules=[MODULE1],
      description='utilid layer for xlattice_py',
      url='https://jddixon.github.io/xlutil_py',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python 2.7',
          'Programming Language :: Python 3.3',
          'Programming Language :: Python 3.4',
          'Programming Language :: Python 3.5',
          'Programming Language :: Python 3.6',
          'Programming Language :: Python 3.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],)
