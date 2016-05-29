**dataArtist** - *…scientific data processing made easy.*

[Download for Windows 7-10]
(https://github.com/radjkarl/dataArtist/releases/tag/v0.1-alpha)

[screenshot]

About
-----

*dataArtist* is a graphical program for interactive data analysis and
processing. It is currently specialized image processing tasks in
combination with electroluminescence imaging of photovoltaic devices. It
is written in Python (2.7) and is released under open source.
*dataArtist* is written to be platform independent. It is known to run
under Windows 7-10 and Ubuntu Linux 14.10 (soon).

**Please cite *dataArtist* as follows:** > K.G. Bedrich et al.,
“Electroluminescence Imaging of PV Devices: Camera Calibration and Image
Correction” in IEEE PVSC, 2016.

Manuals
-------

`USER manual`_

`DEVELOPERS manual`_

Online Tutorials
----------------

General usage, camera calibration and image correction are explained in
youtube screencast sessions, see |IMAGE ALT TEXT HERE|

Supported file types
--------------------

Data is imported through drag n’drop.

1. Images

-  Common used (TIF, BMP, PNG, JPG, CSV, TXT, MAT)
-  RAW, if data type and image shape are known
-  Numpy arrays

2. Plots

-  CSV, TXT, numpy arrays

Installation
------------

Portable version
~~~~~~~~~~~~~~~~

-  *dataArtist* runs out of the box. No installation needed (currently
   Windows only). See section `Releases`_.

Installation into existing Python installation using pip
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  A few packages used by dataArtist are not available via pip. Please
   refer to the `user manual`_ for more information.
-  Once these packages are installed, open a command shell and type:

``pip install dataArtist``

Scripting, Automation, Modding
------------------------------

*dataArtist* comes with a built-in python shell. Data can be examplary
accessed though ``d1.l3`` (display 1, data layer 3) and tools
e.g. through ``d.tools['Axes'].click()`` (in current display execute
tool ‘Axes’). *dataArtist* allows adding own tools, displays and
importers, for examples, see dataArtist/modding.

Main dependencies
-----------------

+----------------------+----------------------------------------------------------+
| Package              | Description                                              |
+======================+==========================================================+
| `pyqtgraph\_karl`_   | Scientific Graphics and GUI Library based on Qt (Fork)   |
+----------------------+----------------------------------------------------------+
| `imgProcessor`_      | General propose image processing libary                  |
+----------------------+----------------------------------------------------------+
| `appBase`_           | Base packages for apps, based on Qt                      |
+----------------------+----------------------------------------------------------+
| `fancyWidgets`_      | A collection of fancy widgets, based on Qt               |
+----------------------+----------------------------------------------------------+
| `fanctTools`_        | A collection of useful not-GUI tools                     |
+----------------------+----------------------------------------------------------+

Example: Electroluminescence imaging
------------------------------------

Camera calibration
~~~~~~~~~~~~~~~~~~

For camera calibration all needed images are dropped into *dataArtist*
and the matching tool

.. _USER manual: https://github.com/radjkarl/dataArtist/raw/master/dataArtist/media/USER_MANUAL.pdf
.. _DEVELOPERS manual: http://radjkarl.github.io/dataArtist/
.. _Releases: https://github.com/radjkarl/dataArtist/releases
.. _user manual: ../blob/master/dataArtist/media/USER_MANUAL.pdf
.. _pyqtgraph\_karl: https://github.com/radjkarl/pyqtgraph_karl
.. _imgProcessor: https://github.com/radjkarl/imgProcessor
.. _appBase: https://github.com/radjkarl/appBase
.. _fancyWidgets: https://github.com/radjkarl/fancyWidgets
.. _fanctTools: https://github.com/radjkarl/fancyTools

.. |IMAGE ALT TEXT HERE| image:: http://img.youtube.com/vi/YOUTUBE_VIDEO_ID_HERE/0.jpg
   :target: https://www.youtube.com/channel/UCjjngrC3jPdx1HL8zJ8yqLQ