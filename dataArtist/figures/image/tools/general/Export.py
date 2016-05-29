import cv2
from pyqtgraph_karl.Qt import QtGui
import numpy as np

from fancywidgets.pyQtBased.Dialogs import Dialogs
from imgProcessor.transformations import toUIntArray
from imgProcessor.imgIO import out

from dataArtist.widgets.Tool import Tool



class Export(Tool):
    '''
    Save the display image to file
    '''
    icon = 'export.svg' 

    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)
       
        self._dialogs = Dialogs()

        ftypes = """Portable Network Graphics (*.png)
Windows bitmaps (*.bmp *.dib)
JPEG files (*.jpeg *.jpg *.jpe)
JPEG 2000 files (*.jp2)
Portable image format (*.pbm *.pgm *.ppm)
Sun rasters (*.sr *.ras)
TIFF files (*.tiff *.tif)"""

        self.engine = {'original':
                        (self.exportOriginal, 
                            ftypes),
                       'rendered': 
                            (self.exportRendered, 
                             ftypes),
                       'Numpy array':
                            (self.exportNumpy,
                             'Numpy array (*.npy)'),
                       'Txt file': 
                            (lambda:self.exportNumpy(np.savetxt), 
                             'Text file (*.txt)'),
                       }
        pa = self.setParameterMenu() 

        self.pExportAll = pa.addChild({
            'name': 'export all image layers',
            'type': 'bool',
            'value':False})
        
        self.pEngine = pa.addChild({
            'name': 'Type',
            'type': 'list',
            'value':'original',
            'limits':self.engine.keys(),
            'tip':'''original: export the original image array
rendered: export the current display view'''})
        
        self.pCutNegativeValues = self.pEngine.addChild({
            'name': 'Cut negative values',
            'type': 'bool',
            'value':False,
            'visible':True})
        self.pStretchValues = self.pEngine.addChild({
            'name': 'Stretch values',
            'type': 'bool',
            'value':False,
            'visible':True})
        
        self.pOnlyImage = self.pEngine.addChild({
            'name': 'Only image',
            'type': 'bool',
            'value':False,
            'tip':'True - export only the shown image - excluding background and axes',
            'visible':False})

        self.pEngine.sigValueChanged.connect(self._pEngineChanged)        

        self.pResize = pa.addChild({
            'name': 'Resize',
            'type': 'bool',
            'value':False})
        
        self.pAspectRatio = self.pResize.addChild({
            'name': 'Keep Aspect Ratio',
            'type': 'bool',
            'value':True,
            'visible':False}) 
         
        self.pWidth = self.pResize.addChild({
            'name': 'Width',
            'type': 'int',
            'value': 0,
            'visible':False})
        self.pWidth.sigValueChanged.connect(self._pWidthChanged)
         
        self.pHeight = self.pResize.addChild({
            'name': 'Height',
            'type': 'int',
            'value': 0,
            'visible':False})
        self.pHeight.sigValueChanged.connect(self._pHeightChanged)

        self.pResize.sigValueChanged.connect(lambda param, value: 
                            [ch.show(value) for ch in param.children()] )

        self.pPath = pa.addChild({
            'name': 'path',
            'type': 'str',
            'value':''})
        
        pChoosePath = self.pPath.addChild({
            'name': 'choose',
            'type': 'action'})
        pChoosePath.sigActivated.connect(self._pChoosePathChanged)

        self._menu.aboutToShow.connect(self._updateDisplayDize)
   
   
    def _pChoosePathChanged(self, param):
        self._choosePath()
        self.activate()
       
       
    def _pEngineChanged(self, param, val):
        self.pCutNegativeValues.show(val == 'original')
        self.pStretchValues.show(val == 'original')
        self.pOnlyImage.show(val == 'rendered')
        
            

    def _updateDisplayDize(self):
        size = self.display.size()
        w = size.width()
        h = size.height()
        self.aspectRatio = h / float(w)
        self.pWidth.setValue(w, blockSignal=self._pWidthChanged) 
        self.pHeight.setValue(h, blockSignal=self._pHeightChanged)
        
 
    def _pHeightChanged(self, param, value):
        if self.pAspectRatio.value():
            self.pWidth.setValue(value/self.aspectRatio, 
                                 blockSignal=self._pWidthChanged)
        

    def _pWidthChanged(self, param, value):
        if self.pAspectRatio.value():
            self.pHeight.setValue(value*self.aspectRatio, 
                                  blockSignal=self._pHeightChanged)
  

    def _choosePath(self):
        filt = self.engine[self.pEngine.value()][1]
        kwargs = dict(filter=filt, selectedFilter='png')
        f = self.display.filenames[0]
        if f is not None:
            kwargs['directory'] = f.dirname()
            
        path = self._dialogs.getSaveFileName(**kwargs)
        if path and path != '.':
            self.pPath.setValue(path)


    def activate(self):
        #CHECK PATH
        if not self.pPath.value():
            self._choosePath()
            if not self.pPath.value():
                raise Exception('define a file path first!')

        self.engine[ self.pEngine.value() ][0] ()



    def exportRendered(self):
        '''
        Use QPixmap.grabWidget(display) to save the image
        '''
        d = self.display
        try:
            #get instance back from weakref
            d = d.__repr__.__self__
        except:
            pass
        #PREPARE LAYOUT:
        d.release()
        d.hideTitleBar()
        
        if self.pResize.value():
            d.resize(self.pWidth.value(), self.pHeight.value())            
        #SAVE:
        path = self.pPath.value()
        
        def grabAndSave(path2):
            if self.pOnlyImage.value():
                item = d.widget.imageItem
                b = item.sceneBoundingRect().toRect()
                w = QtGui.QPixmap.grabWidget(d.widget, b)
            else:
                w = QtGui.QPixmap.grabWidget(d)
            w.save(path2)
            print 'Saved image under %s' %path2
        
        if self.pExportAll.value():
            #EACH LAYER SEPARATE
            old_i = d.widget.currentIndex
            for i in range(len(d.widget.image)):
                path2 = path.replace('.', '__%s.' %i)
                d.widget.setCurrentIndex(i)
                grabAndSave(path2)
            d.widget.setCurrentIndex(old_i)
        else:
            grabAndSave(path)
        #RESET LAYOUT:
        d.showTitleBar()
        d.embedd()
            

    def exportNumpy(self, method=np.save):
        '''
        Export as a numpy array *.npy
        '''
        path = self.pPath.value()
        w = self.display.widget
        image = w.image

        if not self.pExportAll.value():
            image = image[w.currentIndex]
        method(path, image)
        print 'Saved image under %s' %path


    def exportOriginal(self):
        '''
        Use cv2.imwrite() to save the image array
        '''
        def export(img, path):
            if self.pResize.value():
                img = cv2.resize(img, (self.pHeight.value(), self.pWidth.value()) )
            else:
                img = img.copy()
            int_img = toUIntArray(img, 
                                  cutNegative=self.pCutNegativeValues.value(), 
                                  cutHigh=~self.pStretchValues.value())
            cv2.imwrite(path,out(int_img))
            print 'Saved image under %s' %path
        w = self.display.widget            
        image = w.image
        path = self.pPath.value()
        
        if self.pExportAll.value():
            for n, img in enumerate(image):
                path2 = path.replace('.', '__%s.' %n)
                export(img, path2)
        else:
            image = image[w.currentIndex]
            export(image, path)