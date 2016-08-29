from dataArtist.widgets.Tool import Tool
from dataArtist.figures.image.tools.globals.CalibrationFile import CalibrationFile



class CorrectCamera(Tool):
    '''
    Correct for the following camera related distortions:
    
    1. Single time effects (only if multiple images are in display)
    2. Dark current (either calculated or given in other display)
    3. Vignetting/Sensitivity
    4. Image artifacts 
    5. Blur (not at the moment)
    6. Lens distortion
    
    using a camera calibration file
    '''
    icon = 'correctCamera.svg'

    def __init__(self, display):
        Tool.__init__(self, display)

        self.calFileTool = self.showGlobalTool(CalibrationFile)
        self._bgDisplay = None

        pa = self.setParameterMenu() 

        self.pCalName = pa.addChild({
            'name':'Camera calibration',
            'type':'str',
            'value':'',
            'readonly':True,
            'tip':"The current calibration file. To change, use 'CalibrationFile' tool button"})
        self._menu.aboutToShow.connect(self._updatepCal)

        self.createResultInDisplayParam(pa)

        self.pAllLayers  = pa.addChild({
            'name':'Execute on',
            'type':'list',
            'value':'all layers average',
            'tip': '''
all layers: 
        average: all images are averaged and single time effects (STE) are removed
        indiviual: all images are corrected, no averaging, no ste removal
pair of two layers: every next 2 image are averaged and STE removed
current layer: only the current image is taken - no average, no STE removal
                    ''',
            'limits':['current layer', 
                      'all layers average',
                      'all layers individual',
                       'pair of two layers']})

#         ps = self.pSTEremoval  = pa.addChild({
#             'name':'Single-time-effect removal',
#             'type':'bool',
#             'value':False,
#             'tip':'Averages every two images in a row in this display'})
#         
#         self.pAllLayers.sigValueChanged.connect(lambda p,v:
#             ps.setOpts(value=True, readonly=True) 
#             if v == 'all layers' 
#             else ps.setOpts(readonly=False))
#         self.pAllLayers.setValue(True)
        

        self.pDeblur  = pa.addChild({
            'name':'Deblur',
            'type':'bool',
            'value':False,
            'tip':'Whether to deconvolve the image - this might take some minutes'})

        self.pDenoise  = pa.addChild({
            'name':'Denoise',
            'type':'bool',
            'value':False,
            'tip':'Remove noise using Non-Local Means Denoising - this takes some time'})

        self.pKeepSize  = pa.addChild({
            'name':'Keep size',
            'type':'bool',
            'value':True})

        self.pBgMethod  = pa.addChild({
            'name':'Background',
            'type':'list',
            'value':'from display',
            'limits': ['calculate', 'from display']})
        self.pBgMethod.sigValueChanged.connect(self._pBgMethodChanged) 

        self.pBgExpTime  = self.pBgMethod.addChild({
            'name':'Exposure time',
            'type':'float',
            'value':10,
            'suffix': 's', 
            'siPrefix':True,
            'visible':False,
             'limits':[0,1e6]})

        self.pBgFromDisplay  = self.pBgMethod.addChild({
            'name':'From display',
            'type':'menu',
            'value':'-'})
        self.pBgFromDisplay.aboutToShow.connect(
#                                 self._buildBgFromDisplayMenu)

                lambda m, fn=self._setBGDisplay:
                            self.buildOtherDisplaysMenu(
                                    m,fn))



        self.pThreshold  = pa.addChild({
            'name':'Artifact removal threshold',
            'type':'float',
            'value':0.0,
            'limits':[0.,1.],
            'tip':'Increase value to increase filter effect'})

#         self.pUncertainty  = pa.addChild({
#             'name':'Return correction uncertainty',
#             'type':'bool',
#             'value':False})


    def _updatepCal(self):
        v = self.calFileTool.pCal.value()
        self.pCalName.setValue( v )
        hasCal =  v != '-'
        self.pDeblur.show(hasCal)
        self.pDenoise.show(hasCal)
        self.pKeepSize.show(hasCal)
        if hasCal:
            self.pBgMethod.setOpts(readonly=False)
        else:
            self.pBgMethod.setOpts(value= 'from display',readonly=True)


    def _pBgMethodChanged(self, param, value):
        '''
        show/hide right parameters for chosen option
        '''
        if value == 'calculate':
            self.pBgExpTime.show()
            self.pBgFromDisplay.hide()
        else:
            self.pBgFromDisplay.show()
            self.pBgExpTime.hide()
     
     
    def _setBGDisplay(self, display):
        self._bgDisplay = display


#     def _buildBgFromDisplayMenu(self, menu):
#         '''
#         add an action for all layers of other ImageDisplays
#         '''
#         menu.clear()
#         for d in self.display.workspace.displays():
#             if (d.widget.__class__ == self.display.widget.__class__ 
#                 and d.name() != self.display.name()):
#                 a = menu.addAction(d.name())
#                 a.triggered.connect(
#                     lambda checked, d=d: 
#                         [menu.setTitle(d.name()[:20]),
#                         self.__setattr__('_bgDisplay', d)] )


    def activate(self):        
        '''
        open camera calibration and undistort image(s)
        '''
        self.startThread(self._process, self._done)


    def _process(self):
        w = self.display.widget
        im = w.image
        
        out = []
        
        #CHECK SETUP:
#         if self.pCalName.value() =='-':# is None:
#             raise Exception('no calibration file given')
        #GET VARIABLES:
        bgImages = None
        exposureTime = None
        if self.pBgMethod.value() == 'calculate':
            exposureTime = self.pBgExpTime.value()
        elif self.pBgFromDisplay.value() != '-': 
            bgImages  = self._bgDisplay.widget.image
#             if len(bgImages)==1:
#                 bgImages = bgImages[0]

#         if not self.pAllLayers.value():
#             im = [im[w.currentIndex]]

        l = len(im)
        wc = w.currentIndex
                                    #start, stop,step
        c = {'current layer':       (wc, wc+1, 1),
             'all layers average':  (0,  l+1,  l),
             'all layers individual':(0, l,    1),
             'pair of two layers':   (0, l,    2)}[
                                    self.pAllLayers.value()]


#         ste = self.pSTEremoval.value()
#         if ste:
#             if len(im) %2 != 0:
#                 raise Exception('need an even number of images (min 2) for STE removal')        
#             c = 2
#         else:
#             c = 1


        r = range(*c)

#         for i in range(0,len(im),c):
#             if ste:
#                 im1 = im[i]
#                 im2 = im[i+1]
#             else:
#                 im1 = im[i]
#                 im2 = None

        for i in range(len(r)-1):
            

            out.append( self.calFileTool.correct(
                                images=im[r[i]:r[i+1]], 
                                exposure_time=exposureTime, 
                                bgImages=bgImages, 
                                threshold=self.pThreshold.value(),
                                keep_size=self.pKeepSize.value(),
                                deblur=self.pDeblur.value(),
                                denoise=self.pDenoise.value())
                       )
        return out
    
    
    def _done(self, out):
        self.handleOutput(out, title='corrected camera distortion', 
                               changes='corrected camera distortion')