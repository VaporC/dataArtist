from scipy.ndimage.filters import median_filter
import numpy as np
import cv2

from dataArtist.widgets.Tool import Tool 


class CV2Denoise(Tool):
    '''
    use Non-local Means Denoising algorithm given by OpenCV
    works on grey, coloured single and multiple images
    IMPORTANT: works only on uint8 images images(0-255)
                -> converts to this value, if not done already
    
    http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_photo/py_non_local_means/py_non_local_means.html
    '''
    icon = 'CV2denoise.svg'

    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)
            
        self.function = None
        
        pa = self.setParameterMenu() 
        self._menu.aboutToShow.connect(self._setupMenu)
                            
        self.createResultInDisplayParam(pa)

        self.pConvMethod = pa.addChild({
            'name':'conversion method (to 8bit)',
            'type':'list',
            'value':'scale',
            'limits':['clip', 'scale']})
        
        self.pOptional = pa.addChild({
            'name':'Optional (expand to setup)',
            'type':'empty',
            'expanded':False,
            'isgroup':True})

        self.pTemplateWindowSize = self.pOptional.addChild({
            'name':'templateWindowSize ',
            'type':'int',
            'limits':[3,1000],
            'tip':'''Size in pixels of the template patch that is used 
            to compute weights. Should be odd. Recommended value 7 pixels''',
            'value':7})

        self.pSearchWindowSize  = self.pOptional.addChild({
            'name':'searchWindowSize  ',
            'type':'int',
            'limits':[3,1000],
            'tip':'''Size in pixels of the window that is used to compute 
            weighted average for given pixel. Should be odd. Affect 
            performance linearly: greater searchWindowsSize - 
            greater denoising time. Recommended value 21 pixels''',
            'value':21})

        self.pH = self.pOptional.addChild({
            'name':'h',
            'type':'int',
            'value':10,
            'tip':'''Parameter regulating filter strength. 
            Big h value perfectly removes noise but also removes image 
            details, smaller h value preserves details but also 
            preserves some noise''',
            'limits':[1, 1000]})

        #only color
        self.pHForColorComponents = self.pOptional.addChild({
            'name':'hForColorComponents ',
            'type':'int',
            'value':10,
            'tip':'''The same as h but for color components. 
            For most images value equals 10 will be enought to remove 
            colored noise and do not distort colors''',
            'limits':[1, 1000]})

        #only stack
        self.pImgToDenoiseIndex = pa.addChild({
            'name':'imgToDenoiseIndex ',
            'type':'int',
            'value':1,
            'tip':'''Target image to denoise index in srcImgs sequence''',
            'limits':[0, 1000]})
        #only stack 
        self.pTemporalWindowSize = pa.addChild({
            'name':'temporalWindowSize ',
            'type':'int',
            'value':1,
            'tip':'''Number of surrounding images to use for target image denoising. 
            Should be odd. Images from imgToDenoiseIndex - 
            temporalWindowSize / 2 to imgToDenoiseIndex - temporalWindowSize 
            / 2 from srcImgs will be used to denoise srcImgs[imgToDenoiseIndex]''',
            'limits':[0, 1000]})

        self.pAddChangesLayer = self.pOptional.addChild({
            'name':'Add changes layer',
            'type':'bool',
            'value':True,
            })


    def _setupMenu(self):
        '''
        setup for self.function and self.args taken from http://docs.opencv.org/master/modules/photo/doc/denoising.html
        '''
        image = self.display.widget.image
        self.args = ()
        #find the fitting function for the image:        
        if image.ndim == 4:
            # coloured image stack
            self.function = cv2.fastNlMeansDenoisingColoredMulti 

            if not self.pOptional.opts['expanded']:
                #use defaults given by openCV
                self.args = (self.pImgToDenoiseIndex.value(), 
                             self.pTemporalWindowSize.value())
            else:
                self.args = (self.pImgToDenoiseIndex.value(), 
                             self.pTemporalWindowSize.value(),
                             None, #destination image
                             self.pH.value(),
                             self.pHColor.value(),
                             self.pTemplateWindowSize.value(),
                             self.pSearchWindowSize.value())
            
            self.pTemporalWindowSize.show()
            self.pImgToDenoiseIndex.show()
            self.pHForColorComponents.show()
            
        elif image.ndim == 3 and len(image)>1:
            if len(self.display.filenames) > 1:
                # grey scale image stack
                self.function = cv2.fastNlMeansDenoisingMulti 
                
                if not self.pOptional.opts['expanded']:
                    #use defaults given by openCV
                    self.args = (self.pImgToDenoiseIndex.value(), 
                                 self.pTemporalWindowSize.value())
                else:
                    self.args = (self.pImgToDenoiseIndex.value(), 
                                 self.pTemporalWindowSize.value(),
                                 None, #destination image
                                 self.pH.value(),
                                 #self.pHColor.value(),
                                 self.pTemplateWindowSize.value(),
                                 self.pSearchWindowSize.value())
      
                self.pTemporalWindowSize.show()
                self.pImgToDenoiseIndex.show()
                self.pHForColorComponents.hide()

            else:
                #single coloured image
                self.function = cv2.fastNlMeansDenoisingColored
                
                if not self.pOptional.opts['expanded']:
                    #use defaults given by openCV
                    self.args = ()
                else:
                    self.args = (#self.pImgToDenoiseIndex.value(), 
                                 #self.pTemporalWindowSize.value(),
                                 None, #destination image
                                 self.pH.value(),
#                                  self.pHColor.value(),
                                 self.pTemplateWindowSize.value(),
                             self.pSearchWindowSize.value())               
                                
                self.pTemporalWindowSize.hide()
                self.pImgToDenoiseIndex.hide()
                self.pHForColorComponents.show()
        else:
            #single grey scale image
            self.function = cv2.fastNlMeansDenoising 

            if not self.pOptional.opts['expanded']:
                #use defaults given by openCV
                self.args = ()
            else:
                self.args = (#self.pImgToDenoiseIndex.value(), 
                             #self.pTemporalWindowSize.value(),
                             None, #destination image
                             self.pH.value(),
                             #self.pHColor.value(),
                             self.pTemplateWindowSize.value(),
                             self.pSearchWindowSize.value()) 

            self.pTemporalWindowSize.hide()
            self.pImgToDenoiseIndex.hide()
            self.pHForColorComponents.hide()


    def activate(self):
        image = np.array(self.display.widget.image)

        self._setupMenu()
        
        scale=mn=0
        #TRANSFORM TO UINT8:
        orig_dtype = image.dtype
        if orig_dtype != np.uint8:
            if self.pConvMethod.value() == 'clip':
                image = [np.uint8(np.clip(i,0,255)) for i in image]
            else: #scale
                med = median_filter(image[0], 3)
                mn = np.min(med)
                image -= mn # set min to 0
                scale = np.max(med) / 255.0
                image /= scale
                image = np.clip(image, 0,255)
                image = image.astype(np.uint8)
        
        #if len(image)==1:
        #    image = image[0]
        
        self.startThread(
            lambda image=image, scale=scale, mn=mn, orig_dtype=orig_dtype:
                self._process(image, scale, mn, orig_dtype), self._processDone)


    def _processDone(self, out):
        self.handleOutput([out], title='CV2 Denoised')
        
        if self.pAddChangesLayer.value():
            diff = self.display.widget.image - out
            if diff.any():
                self.display.widget.addColorLayer(diff, 'CV2 denoised')


    def _process(self, image, scale, mn, orig_dtype):
        out = []
        for i in image:
            i = self.function(i, *self.args)
            if self.pConvMethod.value() == 'scale':
                i = i.astype(orig_dtype)
                i *= scale
                i+=mn
            out.append(i)
        return out
