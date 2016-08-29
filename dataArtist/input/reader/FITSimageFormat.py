# import tifffile as tff

from imgProcessor.transformations import transpose
import cv2

#OWN
from ImageWithOpenCV import ImageWithOpenCV
        

        
class FITSimageFormat(ImageWithOpenCV):
    '''
    Read one or multiple (stacked) TIF images
          created with imageJ 
    '''
    axes = ['x', 'y', '']   
    ftypes = ('fits', 'fit', 'fts')
    preferred = True


    def __init__(self, *args, **kwargs):
        ImageWithOpenCV.__init__(self, *args, **kwargs)
        p = self.preferences
        p.pGrey.setValue(True)
        p.pGrey.setOpts(readonly=True)
        #p.pResize.setOpts(readonly=True)


    @staticmethod 
    def check(ftype, fname):  
        if ftype in FITSimageFormat.ftypes:
            return True
        return False

    

    def open(self, filename):
        import pyfits #save startup time
        f = pyfits.open(filename)
        img = f[0].data
        labels = None#f[0].name
     
        prefs = self.preferences
        #OPEN
        #due to different conventions:
        img = transpose(img) 
        #crop
        if prefs.pCrop.value():
            r = (prefs.pCropX0.value(),
                 prefs.pCropX1.value(),
                 prefs.pCropY0.value(),
                 prefs.pCropY1.value())
            img = img[r[0]:r[1],r[2]:r[3]]
        #resize  
        if prefs.pResize.value():
            img = cv2.resize(img, (prefs.pResizeX.value(), prefs.pResizeY.value())) 
 
        img = self.toFloat(img) 
         

        return img, labels