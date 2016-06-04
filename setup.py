# -*- coding: utf-8 -*-
'''
usage:
 (sudo) python setup.py +
     install        ... local or global (if executed with admin rights)
     register        ... at http://pypi.python.org/pypi
     sdist            ... create *.tar to be uploaded to pyPI
     sdist upload    ... build the package and upload in to pyPI
'''

import os
# import sys
# import shutil
from setuptools import find_packages
from setuptools import setup

import dataArtist as package

# #if no arguments given
# if not sys.argv[1:]:
#     sys.exit(__doc__)

mainPath = os.path.abspath(os.path.dirname(__file__))


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    p = os.path.join(*paths)
    if os.path.exists(p):
        with open(p, 'r') as f:
            return f.read()
    return ''


setup(
    name=package.__name__,
    version=package.__version__,
    author=package.__author__,
    author_email=package.__email__,
    url=package.__url__,
    license=package.__license__,
    install_requires=[
        # OWN
        "fancytools",
        "fancywidgets",
        "appbase",
        "imgProcessor",
        # "interactiveTutorial"
        "pyqtgraph_karl",  # a fork of the original pyqtgraph
        # FOREIGN
        "puka",  # a RabbitMQ client
        "numpy",
        "scipy",
        "scikit-image",
        "lxml",
        "transforms3d",
        "cssselect",
        "hachoir-core",
        "hachoir-metadata",
        "hachoir-parser",
        "exifread",
        # "pypiwin32", # pip integration for pywin32, which is not in pip http://sourceforge.net/projects/pywin32/files/pywin32/Build%20219/
        "pygments",
        "tifffile",# for tiffFileReader
        "enum34", #neede by numba(llvmlite) ... and for some reason not installed 
        # TO BE INSTALLED MANUALLY:
        # opencv
        # PyQt4
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    description=package.__doc__,
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,

    entry_points={
        'gui_scripts': [
            'dataArtist = dataArtist.gui:main',
                        ]
                  },    
    long_description=(
        read('README.rst')  # + '\n\n' +
        # read('CHANGES.rst') + '\n\n' +
        # read('AUTHORS.rst')
        )
    )

# remove the build
# else old and non-existent files could come again in the installed pkg

# bPath = os.path.join(mainPath,'build')
# if os.path.exists(bPath):
#     shutil.rmtree(bPath)
