import cv2
import numpy as np

from fancywidgets.pyqtgraphBased.parametertree.parameterTypes import GroupParameter
from imgProcessor.transformations import transpose
#OWN
from dataArtist.input.reader._ReaderBase import ReaderBase


   
        
class ImageWithOpenCV(ReaderBase):
    '''
    Read all kind of images using openCV (excluding stacked tif)
    '''
    axes = ['x', 'y', '']  
    preferred=True 

    ftypes = ('bmp','dib', #Windows bitmaps
              'jpeg', 'jpg', 'jpe', #JPEG files
              'jp2', #JPEG 2000
              'png', #Portable Network Graphics
              'pbm', 'pgm', 'ppm', #Portable image format
              'sr', 'ras', #Sun rasters
              'tiff', 'tif' #TIFF files
              )


    def __init__(self, *args, **kwargs):
        ReaderBase.__init__(self, *args, **kwargs)
        self.preferences = _ImagePreferences()


    @staticmethod 
    def check(ftype, fname):  
        return ftype in ImageWithOpenCV.ftypes
    

    def open(self, filename):
        p = self.preferences
        #open in 8 bit? 
        if p.p8bit.value():
            col = 0
        else:  
            col = cv2.IMREAD_ANYDEPTH
        if p.pGrey.value() and not p.pSplitColors.value():
            col = col | cv2.IMREAD_GRAYSCALE
        else:
            col |= cv2.IMREAD_ANYCOLOR

        #OPEN
        img = cv2.imread(str(filename), col) #cv2.IMREAD_UNCHANGED)
        if img is None:
            raise Exception("image '%s' doesn't exist" %filename)
        #due to different conventions:
        img = transpose(img) 
        
        #crop
        if p.pCrop.value():
            r = (p.pCropX0.value(),
                 p.pCropX1.value(),
                 p.pCropY0.value(),
                 p.pCropY1.value())
            img = img[r[0]:r[1],r[2]:r[3]]
        
        #resize  
        if p.pResize.value():
            img = cv2.resize(img, (p.pResizeX.value(), p.pResizeY.value())) 

        labels = None
        if img.ndim == 3:
            if p.pSplitColors.value():
                img = np.transpose(img, axes=(2,0,1))
                labels = ['blue', 'green','red']
            else:
                #rgb convention
                img = cv2.cvtColor(img, cv2.cv.CV_BGR2RGB)

        #change data type to float
        img = self.toFloat(img, p.pToFloat.value(), p.pForceFloat64.value()) 
        return img, labels

    



class _ImagePreferences(GroupParameter):
    
    def __init__(self, name=' Image import'):
        
        GroupParameter.__init__(self, name=name)
        
        self.pToFloat = self.addChild({
                'name':'transform to float',
                'type':'bool',
                'value':True})
        self.pForceFloat64 = self.pToFloat.addChild({
                'name':'Force double precision (64bit)',
                'type':'bool',
                'value':False})
        self.pToFloat.sigValueChanged.connect(lambda p,v:
                      self.pForceFloat64.show(v))
        self.pGrey = self.addChild({
                'name':'Force grayscale',
                'type':'bool',
                'value':False})
        self.pSplitColors = self.pGrey.addChild({
                'name':'Split color channels',
                'type':'bool',
                'value':False,
                'visible':False})
        self.pGrey.sigValueChanged.connect(lambda p,v:
                    self.pSplitColors.show(v))
        self.p8bit = self.addChild({
                'name':'8bit',
                'type':'bool',
                'value':False})
        self.pCrop = self.addChild({
                'name':'crop',
                'type':'bool',
                'value':False})
        fn = lambda param, value, self=self: [ch.show(value) for ch in param.children()]
        self.pCrop.sigValueChanged.connect(fn)          

        pX = self.pCrop.addChild({
                'name':'x',
                'type':'empty'})               
        self.pCropX0 = pX.addChild({
                'name':'start',
                'type':'int',
                'value':0}) 
        self.pCropX1 = pX.addChild({
                'name':'stop',
                'type':'int',
                'value':500}) 
        pY = self.pCrop.addChild({
                'name':'y',
                'type':'empty'}) 
        self.pCropY0 = pY.addChild({
                'name':'start',
                'type':'int',
                'value':0}) 
        self.pCropY1 = pY.addChild({
                'name':'stop',
                'type':'int',
                'value':500}) 
        fn(self.pCrop, self.pCrop.value())    

        self.pResize = self.addChild({
                'name':'resize',
                'type':'bool',
                'value':False})
        fn = lambda param, value, self=self: [ch.show(value) for ch in param.children()]
        self.pResize.sigValueChanged.connect(fn)          
        self.pResizeX = self.pResize.addChild({
                'name':'width',
                'type':'int',
                'value':100}) 
        self.pResizeY = self.pResize.addChild({
                'name':'height',
                'type':'int',
                'value':100})
        fn(self.pResize, self.pResize.value()) 