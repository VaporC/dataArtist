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
            'name':'Execute on all layers',
            'type':'bool',
            'value':True})

        self.pSTEremoval  = pa.addChild({
            'name':'Single-time-effect removal',
            'type':'bool',
            'value':False,
            'tip':'Averages every two images in a row in this display'})

        self.pDeblur  = pa.addChild({
            'name':'Deblur',
            'type':'bool',
            'value':False,
            'tip':'Whether to deconvolve the image - this might take some minutes'})

        self.pKeepSize  = pa.addChild({
            'name':'Keep size',
            'type':'bool',
            'value':True})

        self.pBgMethod  = pa.addChild({
            'name':'Background',
            'type':'list',
            'value':'calculate',
            'limits': ['calculate', 'from display']})
        self.pBgMethod.sigValueChanged.connect(self._pBgMethodChanged) 

        self.pBgExpTime  = self.pBgMethod.addChild({
            'name':'Exposure time',
            'type':'float',
            'value':10,
            'suffix': 's', 
            'siPrefix':True,
             'limits':[0,1e6]})

        self.pBgFromDisplay  = self.pBgMethod.addChild({
            'name':'From display',
            'type':'menu',
            'value':'[Choose]',
            'visible':False})
        self.pBgFromDisplay.aboutToShow.connect(self._buildBgFromDisplayMenu)

        self.pThreshold  = pa.addChild({
            'name':'Artifact removal threshold',
            'type':'float',
            'value':0.2,
            'tip':'Set to 0 to disable artifact removal'})

#         self.pUncertainty  = pa.addChild({
#             'name':'Return correction uncertainty',
#             'type':'bool',
#             'value':False})


    def _updatepCal(self):
        self.pCalName.setValue( self.calFileTool.pCal.value() )


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
 

    def _buildBgFromDisplayMenu(self, menu):
        '''
        add an action for all layers of other ImageDisplays
        '''
        menu.clear()
        for d in self.display.workspace.displays():
            if (d.widget.__class__ == self.display.widget.__class__ 
                and d != self.display):
                a = menu.addAction(d.name())
                a.triggered.connect(
                    lambda checked, d=d: 
                        [menu.setTitle(d.name()[:20]),
                        self.__setattr__('_bgDisplay', d)] )


    def activate(self):        
        '''
        open camera calibration and undistort image(s)
        '''
        self.startThread(self._process, self._done)


    def _process(self):
        w = self.display.widget
        im = w.image
        
        if not self.pAllLayers.value():
            im = [im[w.currentIndex]]
        
        out = []
        
        #CHECK SETUP:
        if self.pCalName.value() =='-':# is None:
            raise Exception('no calibration file given')
        #GET VARIABLES:
        if self.pBgMethod.value() == 'calculate':
            exposureTime = self.pBgExpTime.value()
            bgImages = None
        else:
            exposureTime = None
            bgImages  = self._bgDisplay.widget.image
            if len(bgImages)==1:
                bgImages = bgImages[0]

        ste = self.pSTEremoval.value()
        if ste:
            if len(im) %2 != 0:
                raise Exception('need an even number of images (min 2) for STE removal')        
            c = 2
        else:
            c = 1

        for i in range(0,len(im),c):
            if ste:
                im1 = im[i]
                im2 = im[i+1]
            else:
                im1 = im[i]
                im2 = None

            out.append( self.calFileTool.correct(
                                image1=im1, 
                                image2=im2,
                                exposure_time=exposureTime, 
                                bgImages=bgImages, 
                                threshold=self.pThreshold.value(),
                                keep_size=self.pKeepSize.value(),
                                deblur=self.pDeblur.value())
                       )
        return out
    
    
    def _done(self, out):
        self.handleOutput(out, title='corrected camera distortion', 
                               changes='corrected camera distortion')