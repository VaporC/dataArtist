**dataArtist** - *...scientific data processing made easy.*

[Download for Windows 7-10] (https://github.com/radjkarl/dataArtist/releases/tag/v0.1-alpha)


![screenshot]


## About
*dataArtist* is a graphical program for interactive data analysis and processing. It is currently specialized image processing tasks in combination with electroluminescence imaging of photovoltaic devices.
It is written in Python (2.7) and is released under open source.
*dataArtist* is written to be platform independent. It is known to run under Windows 7-10 and Ubuntu Linux 14.10 (soon).

__Please cite *dataArtist* as follows:__
> K.G. Bedrich et al., �Electroluminescence Imaging of PV Devices: Camera Calibration and Image Correction� in IEEE PVSC, 2016.

## Manuals
[USER manual](../blob/master/LICENSE)
[DEVELOPERS manual](../blob/master/LICENSE)

## Tutorials
General usage, camera calibration and image correction are explained in youtube screencast sessions, see
[![IMAGE ALT TEXT HERE](http://img.youtube.com/vi/YOUTUBE_VIDEO_ID_HERE/0.jpg)](https://www.youtube.com/channel/UCjjngrC3jPdx1HL8zJ8yqLQ)


## Supported file types
Data is imported through drag n'drop.  

1. Images
  * Common used (TIF, BMP, PNG, JPG, CSV, TXT, MAT)
  * RAW, if data type and image shape are known
  * Numpy arrays
2. Plots
  * CSV, TXT, numpy arrays


## Installation
### Portable version
* *dataArtist* runs out of the box. No installation needed (currently Windows only). See section [Releases](https://github.com/radjkarl/dataArtist/releases).

### Installation into existing Python installation using pip
* A few packages used by dataArtist are not available via pip. Please refer to the [user manual](../blob/master/dataArtist/media/USER_MANUAL.pdf) for more information.
* Once these packages are installed, open a command shell and type:

`pip install dataArtist`



## Scripting, Automation, Modding
*dataArtist* comes with a built-in python shell. Data can be examplary accessed though `d1.l3` (display 1, data layer 3) and tools e.g. through `d.tools['Axes'].click()` (in current display execute tool 'Axes').
*dataArtist* allows adding own tools, displays and importers, for examples, see dataArtist/modding.


## Main dependencies
Package | Description
------- | -----------
[pyqtgraph_karl](https://github.com/radjkarl/pyqtgraph_karl) | Scientific Graphics and GUI Library based on Qt (Fork)
[imgProcessor](https://github.com/radjkarl/imgProcessor) | General propose image processing libary
[appBase](https://github.com/radjkarl/appBase) | Base packages for apps, based on Qt
[fancyWidgets](https://github.com/radjkarl/fancyWidgets) | A collection of fancy widgets, based on Qt
[fanctTools](https://github.com/radjkarl/fancyTools) | A collection of useful not-GUI tools


## Example: Electroluminescence imaging


### Camera calibration
For camera calibration all needed images are dropped into *dataArtist* and the matching tool is executed. The calibration results are hereinafter saved to a calibration file. The determination of the point spread function is exemplary shown in the following figure:
![screenshot_psf]
> dataArtist screenshot � toolbar �calibration�. **a**: Best focus determination; **b**: noise-level-function measurement; **c**: Dark current mapping; **d**: Flat field mapping; **e**: PSF estimation (selected): **f**: lens distortion measurement 


### Image correction
The correction of EL image is shown in the following figure. 15. Perspective correction (red box) can be done either using the outline of the PV device (automatically detected or manually defined) or using a reference image. 
![screenshot_correction]
> dataArtist screenshot � **a**: tool 'CalibrationFile'; **b**: tool 'CorrectCamera'; **c**: tool 'PerspectiveCorrection'
> **green line**: Camera correction; **red line**: Perspective correction

[logo]: https://cloud.githubusercontent.com/assets/350050/15405164/00b08326-1dbe-11e6-959d-c7745de7d167.png "dataArtist logo"
[screenshot]: https://cloud.githubusercontent.com/assets/350050/15406631/806a7a8a-1dc4-11e6-9e76-709cd482857f.png "dataArtist screenshot"
[screenshot_psf]: https://cloud.githubusercontent.com/assets/350050/15404653/bd2e51b6-1dbb-11e6-8282-2ea539f0286d.png "dataArtist camera calibration"
[screenshot_correction]: https://cloud.githubusercontent.com/assets/350050/15404785/53d4c992-1dbc-11e6-93b7-c6108ab9a2b0.png "dataArtist image correction"