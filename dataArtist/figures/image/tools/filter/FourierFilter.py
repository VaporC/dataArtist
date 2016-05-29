from imgProcessor.filters.FourierFilter import FourierFilter as FourierFilterProc

from dataArtist.widgets.Tool import Tool


class FourierFilter(Tool):
    '''
    Various FOURIER transformation based filters
    '''
    icon = 'fourierTransformation.svg'

    def __init__(self, display):
        Tool.__init__(self, display)
        #OUTPUT DISPLAYS:
        self.reconstructedDisplay = None
        self.fourierDisplay = None
        self.procFourierDisplay = None
        self.differenceDisplay = None
        #MENU:
        pa = self.setParameterMenu() 

        pUpdate = pa.addChild({
            'name': 'Update',
            'type': 'action'}) 
        pUpdate.sigActivated.connect(self.activate)

        self.pHighPass = pa.addChild({
            'name': 'High pass',
            'type': 'slider',
            'value':0,
            'limits':[0,1]})    

        self.pLowPass = pa.addChild({
            'name': 'Low pass',
            'type': 'slider',
            'value':0,
            'limits':[0,1]}) 
        
        pFilterValues = pa.addChild({
            'name': 'Filter values',
            'type': 'group'}) 
               
        self.pSmallerThreshold = pFilterValues.addChild({
            'name': 'smaller than',
            'type': 'slider',
            'value':0,
            'limits':[0,1]})
         
        self.pBiggerThreshold = pFilterValues.addChild({
            'name': 'bigger than',
            'type': 'slider',
            'value':0,
            'limits':[0,1]})
        
        pDeleteArea = pa.addChild({
            'name': 'Delete area',
            'type': 'group'}) 
        
        pDeleteAreaFrom = pDeleteArea.addChild({
            'name': 'From',
            'type': 'group'})  
           
        self.pAreaFromX = pDeleteAreaFrom.addChild({
            'name': 'x',
            'type': 'slider',
            'value':0,
            'limits':[0,1]}) 
        
        self.pAreaFromY = pDeleteAreaFrom.addChild({
            'name': 'y',
            'type': 'slider',
            'value':0,
            'limits':[0,1]}) 
            
        pDeleteAreaTo = pDeleteArea.addChild({
            'name': 'To',
            'type': 'group'})   
          
        self.pAreaToX = pDeleteAreaTo.addChild({
            'name': 'x',
            'type': 'slider',
            'value':0,
            'limits':[0,1]}) 
        
        self.pAreaToY = pDeleteAreaTo.addChild({
            'name': 'y',
            'type': 'slider',
            'value':0,
            'limits':[0,1]})     
        
        pOutput = pa.addChild({
            'name': 'Output',
            'type': 'group'}) 

        self.pDifferenceImage = pOutput.addChild({
            'name': 'Difference Image',
            'type': 'bool',
            'value':True})
        
        self.pFourierImage = pOutput.addChild({
            'name': 'Fourier Image',
            'type': 'bool',
            'value':True}) 
        
        self.pProcessedFourierImage = pOutput.addChild({
            'name': 'Processed Fourier Image',
            'type': 'bool',
            'value':True}) 


    def activate(self):
        self.setChecked (True)

        if len(self.display.axes) > 4:
            raise Exception("doesn't work on stacked images for now")
        w = self.display.widget
        f = FourierFilterProc(w.image[w.currentIndex])
        
        #FOURIER MAGNITUDE SPECTRUM:
        if self.pFourierImage.value():
            if not self.fourierDisplay or self.fourierDisplay.isClosed():
                self.fourierDisplay = self.display.workspace.addDisplay(
                        origin=self.display,
                        data=[f.magnitudeSpectrum()], 
                        title='Fourier')    
            else:
                self.fourierDisplay.widget.setImage(
                        f.magnitudeSpectrum(), autoRange=False)

        #PROCESSING:
        f.highPassFilter(self.pHighPass.value())
        f.lowPassFilter(self.pLowPass.value())
        f.suppressValuesSmallerThanThresholdToZero(self.pSmallerThreshold.value())
        f.suppressValuesBiggerThanThresholdToZero(self.pBiggerThreshold.value())
        f.deleteArea(self.pAreaFromX.value(), self.pAreaFromY.value(), 
                     self.pAreaToX.value(), self.pAreaToY.value())

        #RECONSTRUCTED IMAGE:
        reconstrImg = f.reconstructImage()
        if not self.reconstructedDisplay or self.reconstructedDisplay.isClosed():
            self.reconstructedDisplay = self.display.workspace.addDisplay(
                                                origin=self.display,
                                                data=[reconstrImg], 
                                                title='Reconstructed')
        else:
            self.reconstructedDisplay.widget.setImage(reconstrImg, autoRange=False)

        #DIFFERENCE IMAGE
        if self.pDifferenceImage.value():
            diffImg = self.display.widget.image - reconstrImg
            if not self.differenceDisplay or self.differenceDisplay.isClosed():

                self.differenceDisplay = self.display.workspace.addDisplay(
                                                origin=self.display,
                                                data=[diffImg], 
                                                title='Difference')
            else:
                self.differenceDisplay.widget.setImage(diffImg, autoRange=False)
                
        #PROCESSED FOURIER
        if self.pProcessedFourierImage.value():
            if not self.procFourierDisplay or self.procFourierDisplay.isClosed():
                self.procFourierDisplay = self.display.workspace.addDisplay(
                                                    origin=self.display,
                                                    data=[f.magnitudeSpectrum()], 
                                                    title='Processed fourier')         
            else:
                self.procFourierDisplay.widget.setImage(f.magnitudeSpectrum(), autoRange=False)

                
    def deactivate(self):
        [d.close() for d in (
                self.differenceDisplay, self.reconstructedDisplay,
                self.procFourierDisplay, self.fourierDisplay)]
