import numpy as np

from imgProcessor.transform.equalizeImage import equalizeImage
from imgProcessor.signal import scaleSignal

from dataArtist.widgets.Tool import Tool



class ScaleHistogram(Tool):
    '''
    Equalize the histogram (contrast) of all given images
    '''
    icon = 'equalize.svg'
    
    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)

        self._refImg = None

        pa = self.setParameterMenu() 

        self._methods =  {
              #NAME: (FUNCTION, HISTOGRAM LEVELS)
              'Reference image':
                (lambda x: scaleSignal(x,reference=self._refImg),None),
              'Equalize histogram':
                (equalizeImage,None), 
              'Scale Background-Signal: 0-1':
                (lambda x: scaleSignal(x,backgroundToZero=True), [0,1]),
              'Scale signal +/-3std':
                (scaleSignal,[0,1]),
              'Average=1':
                (self._fnSameAverage,None)}

        self.pMethod = pa.addChild({
            'name': 'Method',
            'type': 'list',
            'value':'Scale signal +/-3std',
            'limits':self._methods.keys()}) 
        
        self.pRefImgChoose = self.pMethod.addChild({
                'name':'Reference image',
                'value':'From display',
                'type':'menu',
                'visible':False})
        self.pRefImg = self.pRefImgChoose.addChild({
                'name':'Chosen',
                'value':'-',
                'type':'str',
                'readonly':True})
        
        self.pRefImgChoose.aboutToShow.connect(lambda menu: 
            self.buildOtherDisplayLayersMenu(menu, self._setRefImg) )
        
        self.pMethod.sigValueChanged.connect(
                lambda p,v:self.pRefImgChoose.show(v=='Reference image'))


    def _setRefImg(self, display, layernumber, layername):
        '''
        extract the reference image and -name from a given display and layer number
        '''
        im  = display.widget.image
        self._refImg = im[layernumber]
        self.pRefImg.setValue(layername)
        
        
    def _fnSameAverage(self, img):
        return img / img.mean()


    def activate(self):
        img = self.display.widget.image

        fn,levels = self._methods[self.pMethod.value()]
        #APPLY FOR EACH LAYER:
        for n,i in enumerate(img):
            try:
                out = fn(i)
                if isinstance(out,np.ndarray):
                    img[n] = out
            except Exception, err:
                print("couldn't scale image: %s" %err)
        self.display.changeLayer(img, 'Equalized', levels=levels)
