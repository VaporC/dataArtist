from dataArtist.widgets.Tool import Tool

from imgProcessor.signal import signalRange



class Colorbar(Tool):
    '''
    Show/Hide the color bar
    '''
    icon = 'colorbar.svg'
    reinit = True

    def __init__(self, display):
        Tool.__init__(self, display)
        self.setChecked(True)
        
        pa = self.setParameterMenu() 

        pFit = pa.addChild({
            'name': 'Fit',
            'type': 'action'})
        pFit.sigActivated.connect(self._fit)
        
        pLevels = pa.addChild({
            'name': 'autoLevels',
            'type': 'bool',
            'value':True})
        
        pRange = pa.addChild({
            'name': 'autoHistogramRange',
            'type': 'bool',
            'value':True})
        
        self.pPrintView = pa.addChild({
            'name': 'print view',
            'type': 'bool',
            'value':False})
        
        pShowHist = self.pPrintView.addChild({
            'name': 'show histogram',
            'type': 'bool',
            'value':False})        
   
        pLevels.sigValueChanged.connect(lambda param, value: 
                self.display.widget.setOpts(autoLevels=value))
        pRange.sigValueChanged.connect(lambda param, value: 
                self.display.widget.setOpts(autoHistogramRange=value))                
        self.pPrintView.sigValueChanged.connect(lambda param, value: 
                self.display.widget.setHistogramPrintView(
                                        value, pShowHist.value()))        
        pShowHist.sigValueChanged.connect(self._pShowHistChanged)        


    def _fit(self):
        w = self.display.widget
        img = w.image[w.currentIndex]
        r = signalRange(img, nSigma=3)
        w.ui.histogram.setLevels(*r)
        

    def _pShowHistChanged(self, param, val):
        if self.pPrintView.value():
            self.pPrintView.setValue(False)
            self.pPrintView.setValue(True)


    def activate(self):
        w = self.display.widget
        h = w.ui.histogram
        try:
            w.imageItem.sigImageChanged.disconnect(h.imageChanged)
            #update:
            h.imageChanged()
        except:
            pass
        w.imageItem.sigImageChanged.connect(h.imageChanged)
        h.show()
        

    def deactivate(self):
        w = self.display.widget
        h = w.ui.histogram
        h.hide()
        try:
            #no need to update histogram when not divible
            w.imageItem.sigImageChanged.disconnect(h.imageChanged)
        except:
            pass
    
    
    def setLevels(self, start, stop):
        '''
        convenience function for easy access from built-in console
        '''
        self.display.widget.ui.histogram.setLevels(start,stop)