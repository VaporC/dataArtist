import numpy as np

from imgProcessor.measure.SNR.SNR import SNR
from imgProcessor.measure.SNR.SNR_IEC import SNR_IEC
from imgProcessor.measure.SNR.SNRaverage import SNRaverage

#OWN
from dataArtist.widgets.Tool import Tool 



class SignalToNoise(Tool):
    '''
    Calculate the signal-to-noise ratio two one/two EL images
    and an optional background image
    '''
    icon = 'SignalToNoise.svg'

    def __init__(self, display):
        Tool.__init__(self, display)

        self.outDisplay = None

        self._refBg = None
        self._refBg_i = None
        
        self._ref2 = None
        self._ref2_i = None

        pa = self.setParameterMenu() 

        self.pMethod = pa.addChild({
                    'name':'Method',
                    'value':'IEC TS 60904-13',
                    'type':'list',
                    'limits':['IEC TS 60904-13', 'Bedrich2016']})

        self.pRefBg = pa.addChild({
                    'name':'Background image',
                    'value':'-',
                    'type':'menu'})
        self.pRefBg.aboutToShow.connect(lambda menu, d='_refBg', i='_refBg_i': 
                                        self.buildRefImgMenu(menu, d,i))

        self.pRefImg2 = pa.addChild({
                    'name':'Equivalent image',
                    'value':'-',
                    'type':'menu'})
        self.pRefImg2.aboutToShow.connect(lambda menu, d='_ref2', i='_ref2_i': 
                                        self.buildRefImgMenu(menu, d,i))

        self.pShowMap = pa.addChild({
                    'name':'Show map',
                    'value':True,
                    'type':'bool'})   
        
        self.pUnit = pa.addChild({
                    'name':'Unit',
                    'value':'-',
                    'type':'list',
                    'limits':['-', 'db']})           

        self.pAverage = pa.addChild({
                    'name':'Averaging method',
                    'value':'X75',
                    'type':'list',
                    'limits':['average','X75', 'RMS']})

        self.pExBg = self.pAverage.addChild({
                    'name':'Exclude Background',
                    'value':True,
                    'type':'bool'})
        self.pOnImgAvg = self.pAverage.addChild({
                    'name':'Refer to image average',
                    'value':False,
                    'type':'bool',
                    'tip': '''Check if SNR should be representative 
                    for the average of both image and its reference.'''})

        self.pMethod.sigValueChanged.connect(self._pMethodChanged)
        self.pMethod.sigValueChanged.emit(None, self.pMethod.value())


    def _pMethodChanged(self, p,v):
        i = v=='Bedrich2016'
        self.pShowMap.show(i)
        self.pAverage.show(i)
        self.pExBg.show(i)
        self.pOnImgAvg.show(i)
        
        
    def buildRefImgMenu(self, menu, refDisplay, refLayerIndex):
        '''
        fill the menu with all available images within other displays
        '''
        menu.clear()

        def setRefImg(display, layernumber, layername):
            menu.setTitle(layername[:20])
            self.__setattr__(refDisplay, display)
            self.__setattr__(refLayerIndex, layernumber)

        menu.addAction('-').triggered.connect(lambda: setRefImg(None, None, '-'))

        for d in self.display.workspace.displays():
            if (isinstance(d.widget,self.display.widget.__class__) 
                    and d != self.outDisplay): 
                m = menu.addMenu(d.name())
                for n,l in enumerate(d.layerNames()):
                    m.addAction(l).triggered.connect(
                        lambda checked, d=d, n=n,l=l: 
                            setRefImg(d, n, l) )


    def _printSNRavg(self, avg):
        msg = 'average signal-to-noise: %s [%s]  ||   method: %s' %(
                avg, self.pUnit.value(), self.pMethod.value())
        if self.pMethod.value() == 'Bedrich2016':
            msg += ', averaging: %s, background exclusion: %s' %(
                self.pAverage.value(), self.pExBg.value())
        print msg
                

    def activate(self):
        img = self.display.widget.image
        unit = self.pUnit.value()

        for n, i1 in enumerate(img):
            if self._ref2 is not None:
                i2 = self._ref2.widget.image[self._ref2_i]
            else:
                i2 = None
            if self._refBg is not None:
                ibg = self._refBg.widget.image[self._refBg_i]
            else:
                ibg = 0
            
            #ref. image must be different than image:
            if ( (self._refBg and self._refBg.number == self.display.number 
                    and self._refBg_i == n ) 
                or 
                 (self._ref2 and self._ref2.number == self.display.number 
                    and self._ref2_i == n) ) :
                continue 
            
            if self.pMethod.value() != 'Bedrich2016':
                assert i2 is not None, 'Reference image must be defined for IEC method'                
                snr = SNR_IEC(i1,i2,ibg)
                
                if unit == 'db':
                    snr = 10*np.log10(snr)
                self._printSNRavg(snr)
            
            else:
                snr = SNR(i1,i2,ibg, 
                          imgs_to_be_averaged=self.pOnImgAvg.value())
    
                if unit == 'db':
                    snr = 10*np.log10(snr)
                
                avg = SNRaverage(snr, self.pAverage.value(), self.pExBg.value())
                self._printSNRavg(avg)
    
                if self.pShowMap.value():
                    if self.outDisplay is None or self.outDisplay.isClosed():
                        self.outDisplay =  self.display.workspace.addDisplay(
                                origin=self.display,
                                data=[snr], 
                                title='Signal-to-Noise ratio')
                    else:
                        self.outDisplay.addLayer(data=snr, origin=self.display, index=n)