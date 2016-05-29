import cv2
import numpy as np
from  pyqtgraph_karl.Qt import QtCore

from imgProcessor.transformations import toFloatArray

from dataArtist.widgets.Tool import Tool



class VideoStream(Tool):
    '''
    Capture the video stream from a connected webcam.
    '''
    icon = 'webcam.svg'
    
    def __init__(self, display):
        Tool.__init__(self, display)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._grabImage)
        self.firstTime = True

        pa = self.setParameterMenu()

        self.pGrayscale = pa.addChild({
            'name': 'Grayscale',
            'type': 'bool',
            'value': True}) 

        self.pFloat = pa.addChild({
            'name': 'To float',
            'type': 'bool',
            'value': True}) 
        
        pFrequency = pa.addChild({
            'name': 'Read frequency [Hz]',
            'type': 'float',
            'value': 20.0,
            'limits':[0,1000]}) 
        pFrequency.sigValueChanged.connect(self._setInterval)
        
        self._setInterval(pFrequency, pFrequency.value())

        self.pBuffer = pa.addChild({
            'name': 'Buffer last n images',
            'type': 'int',
            'value': 0}) 


    def _setInterval (self, param, freq):
        self.timer.setInterval(1000.0/param.value())


    def activate(self):
        if self.firstTime:
            self.display.addLayer(filename='VideoStream')
            self.firstTime = False
        self.vc = cv2.VideoCapture(-1)
        self.timer.start()


    def deactivate(self):
        self.timer.stop()
      
        
    def _grabImage(self):
        w = self.display.widget
        rval, img = self.vc.read()
        if rval:
            #COLOR
            if self.pGrayscale.value():
                img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            else:
                img = cv2.cvtColor(img, cv2.cv.CV_BGR2RGB)
            img = cv2.transpose(img)
            if self.pFloat.value():
                img = toFloatArray(img)
            i = w.image
            b = self.pBuffer.value()
            if b:
                #BUFFER LAST N IMAGES
                if i is None or len(i) < b:
                    self.display.addLayer(data=img)
                else:
                    #TODO: implement as ring buffer using np.roll()
                    img = np.insert(i, 0, img, axis=0)
                    img = img[:self.pBuffer.value()]
                    w.setImage(img, autoRange=False, autoLevels=False)
            else:
                w.setImage(img, autoRange=False, autoLevels=False)               