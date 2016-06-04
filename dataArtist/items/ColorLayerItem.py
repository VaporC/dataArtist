import pyqtgraph_karl as pg
import numpy as np
from pyqtgraph_karl.Qt import QtGui, QtCore

RED = QtGui.QColor(QtCore.Qt.red).rgb()



class ColorLayerItem(pg.ImageItem):
    '''
    An color overlay for ImageWidget.
    The transparency is given through the [image] array.
    '''
    def __init__(self, image, imageWidget, alpha=0.5,
                 color=RED, histogram=None, pos=None,**kwargs):
        self.histogram = None
        self.alpha = alpha
        self.color = color
        self.histogramPos = pos # the position within a histogram to get the colour from
        self.vb = imageWidget.view.vb

        self.image_full = image
        self._lastInd = imageWidget.currentIndex
        if self.image_full.ndim == 3: #multiple images
            image = self.image_full[self._lastInd]
            imageWidget.sigTimeChanged.connect(self.changeLayer)

        pg.ImageItem.__init__(self, image, **kwargs)
        self.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)

        #create an empty QImage:  
        self._initQImg() 

        if histogram:
            self._setHistogram(histogram)

        self.updateImage()


    def _initQImg(self):
        self.qimage = QtGui.QImage(self.image.shape[0], 
                                   self.image.shape[1],
                                   QtGui.QImage.Format_ARGB32)


    def changeLayer(self, ind):
        '''
        update to show the colour overlay corresponding to the layer index
        '''        
        if ind != self._lastInd:
            self.image = self.image_full[ind]
            self.updateImage()
            self._lastInd = ind


    def getQColor(self):
        c = QtGui.QColor(self.color)
        c.setAlpha(int(self.alpha*255))
        return  c


    def setQColor(self, qcolor):
        self.color = qcolor.rgb()
        self.setAlpha(float(qcolor.alpha())/255)
      

    def setLayer(self, layer, index=None):
        if layer.shape == self.image_full.shape:
            self.image = layer
        elif layer.shape == self.image_full[index].shape:
            self.image_full[index] = layer
        else:
            if self.image_full.ndim == 3: #multiple images
                self.image_full = np.expand_dims(layer, axis=0)
            self.image = layer
            self._initQImg() 
        self.updateImage()
 
 
    def updateImage(self):
        self.qalpha = self._mkQImg()
        self.updateLayer()


    def setAlpha(self, alpha):
        self.alpha = alpha
        self.qalpha = self._mkQImg()
        self.updateLayer()
        

    def updateLayer(self):
        #fill the color layer with the color:
        self.qimage.fill(self.color)
        #add the alpha layer again because it is deleted after .fill:
        self.qimage.setAlphaChannel(self.qalpha) 
        self.vb.updateViewRange()    


    def _mkQImg(self):
        '''create a QImage from self.image_full'''
        im = self.image
        a = self.alpha
        if im.dtype == bool:
            mn = False
            mx = True/ a
        else:
            mn = np.min(im) 
            mx = np.max(im)
            if a > 0:
                mx /= a

        if np.isnan(mn):
            mn,mx = np.nanmin(im), np.nanmax(im) / a
        argb, alpha = pg.functions.makeARGB(im, levels=[mn,mx])
        qalpha = pg.functions.makeQImage(argb, alpha, transpose=True)
        qalpha.convertToFormat(QtGui.QImage.Format_Indexed8)
        return qalpha


    def _setHistogram(self, histogram):
        '''
        connect the changes in the color values of the histogram to _setColor
        '''
        if self.histogram:
            self.histogram.sigLevelsChanged.disconnect(self._setColorViaHistogram)
            self.histogram.gradient.sigGradientChanged.disconnect(
                                                      self._setColorViaHistogram)

        self.histogram = histogram
        self.histogram.sigLevelsChanged.connect(self._setColorViaHistogram)
        self.histogram.gradient.sigGradientChanged.connect(self._setColorViaHistogram)
        self._setColorViaHistogram()


    def _setColorViaHistogram(self):
        #get boundaries from the histogram
        mn,mx = self.histogram.getLevels()
        if mn <= self.histogramPos <= mx:
            #calc x as relative position (0-1) between the boundaries 
            if self.histogramPos == mn:
                x = 0
            else:
                x = (self.histogramPos-mn) / (mx-mn)
            self.color = self.histogram.gradient.getColor(x).rgb()
            self.updateLayer()
        else:
            self.qimage.fill(QtGui.QColor(0,0,0,0).rgba())
            self.vb.updateViewRange()