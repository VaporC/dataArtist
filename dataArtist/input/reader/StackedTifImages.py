import tifffile as tff

from imgProcessor.transformations import transpose
import cv2

#OWN
from ImageWithOpenCV import ImageWithOpenCV
        
        
        
class StackedTifImages(ImageWithOpenCV):
    '''
    Read one or multiple (stacked) TIF images
          created with imageJ 
    '''
    axes = ['x', 'y', '']   
    ftypes = ('tiff', 'tif')
    preferred = True


    def __init__(self, *args, **kwargs):
        ImageWithOpenCV.__init__(self, *args, **kwargs)
        p = self.preferences
        p.pGrey.setValue(True)
        p.pGrey.setOpts(readonly=True)
        #p.pResize.setOpts(readonly=True)


    @staticmethod 
    def check(ftype, fname):  
        if ftype in StackedTifImages.ftypes:
            try:
                tif = tff.TIFFfile(str(fname))
                #try to extract labels names set by imageJ:
                tif.pages[0].imagej_tags['labels']
                return True
            except AttributeError:
                #not an imageJ stack
                return False
    

    def open(self, filename):
        prefs = self.preferences
        #OPEN
        tif = tff.TIFFfile(str(filename))
        img = tif.asarray()
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
        
        try:
            #try to extract labels names set by imageJ:
            labels = tif.pages[0].imagej_tags['labels']
            #remove surplus information:
            for n, l in enumerate(labels):
                try:
                    i = l.index('\n')
                    if i != -1:
                        labels[n] = l[:i]
                except ValueError:
                    #no \n in label
                    pass
            
        except AttributeError:
            if img.ndim == 3:
                #color image
                labels = [str(r) for r in range(len(img))]
            else:
                labels = None
             
        tif.close()
        return img, labels