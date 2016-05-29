import numpy as np
 
from imgProcessor.transform.PerspectiveTransformation import PerspectiveTransformation 

#OWN
from dataArtist.widgets.Tool import Tool



class PatternRecognition(Tool):
    '''
    Fit/Add last/all layer(s) of this display to a given reference image
    using pattern recognition
    '''
    
    #TODO: make this this working on unloaded images
    
    icon = 'patternRecognition.svg'

    def __init__(self, display):
        Tool.__init__(self, display)
        
        self._refImg = None

        pa = self.setParameterMenu() 

        self.createResultInDisplayParam(pa)

        self.pOperation = pa.addChild({
            'name':'Operation',
            'type':'list',
            'value':'fit',
            'limits':['add', 'fit']})

        self.pExecOn = pa.addChild({
            'name':'Execute on',
            'type':'list',
            'value':'all images',
            'limits':['all images', 'last image']})
 
        pRefImgChoose = pa.addChild({
                    'name':'reference image',
                    'value':'from display',
                    'type':'menu'})
        
        self.pRefImg = pRefImgChoose.addChild({
                    'name':'chosen',
                    'value':'-',
                    'type':'str',
                    'readonly':True})
        
        pRefImgChoose.aboutToShow.connect(lambda menu: 
            self.buildOtherDisplayLayersMenu(menu, self._setRefImg) )
 
 
    def _setRefImg(self, display, layernumber, layername):
        '''
        extract the reference image and -name from a given display and layer number
        '''
        im  = display.widget.image
        self._refImg_from_own_display = -1
        self._refImg = im[layernumber]
        if display == self.display:
            self._refImg_from_own_display = layernumber
        self.pRefImg.setValue(layername)


    def activate(self):   
        self.startThread(self._process, self._done)


    def _process(self): 
        img = self.display.widget.image
        only_last = self.pExecOn.value() == 'last image'  

        if self._refImg is None:
            self.setChecked(False)
            raise Exception('choose an reference image first')
        
        print('EXECUTE ', self.__class__.__name__)
        p = PerspectiveTransformation(self._refImg)
        if self.pOperation.value() == 'fit':
            method = p.fitImg
        else:
            method = p.addImg
            
        out = np.empty_like(img)
        
        for n, i in enumerate(img):
            if not only_last or only_last and n == len(img)-1:
                #if not same image
                if n != self._refImg_from_own_display:
                    #PROCESS:
                    try:
                        i = method(i.copy())
                    except Exception, errm:
                        print(self.__class__.__name__ + 'Error: ', errm)
                out[n] = i
        return out, n


    def _done(self, (out, index)):
        self.handleOutput(out, title='PerspectiveFit', 
                               changes='PerspectiveFit', 
                               index=index)    