import numpy as np
from pyqtgraph.Qt import QtGui
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

        self._linked_displays = []
        self._actions = []

        w = self.display.widget

        pa = self.setParameterMenu() 

        pSync = pa.addChild({
            'name':'Synchronize',
            'value':'Display',
            'type':'menu',
            'highlight':True
            })
        pSync.aboutToShow.connect(self._buildLinkColorbar)

        pFit = pa.addChild({
            'name': 'Fit',
            'type': 'action'})
        pFit.sigActivated.connect(self._fit)

        pLevels = pa.addChild({
            'name': 'autoLevels',
            'type': 'bool',
            'value':w.opts['autoLevels']})
        pLevels.sigValueChanged.connect(lambda param, value: 
                w.setOpts(autoLevels=value))
         
        pRange = pa.addChild({
            'name': 'autoHistogramRange',
            'type': 'bool',
            'value':w.opts['autoHistogramRange']})
        pRange.sigValueChanged.connect(lambda param, value: 
                w.setOpts(autoHistogramRange=value))  
        
        self.pPrintView = pa.addChild({
            'name': 'print view',
            'type': 'bool',
            'value':False})
        self.pPrintView.sigValueChanged.connect(lambda param, value: 
               w.setHistogramPrintView(value, pShowHist.value()))  
                
        pShowHist = self.pPrintView.addChild({
            'name': 'show histogram',
            'type': 'bool',
            'value':False})        
        pShowHist.sigValueChanged.connect(self._pShowHistChanged)  
        
        pLog = pa.addChild({
            'name': 'Transform to base 10 logarithm',
            'tip':'The absolute is taken to include negative values as well',
            'type': 'action'})
        pLog.sigActivated.connect(self._log10)

   
    def _log10(self):
        d = self.display
        w = d.widget
        img = np.abs(w.image)
        img = np.log10(img)
#         img[np.logical_or(np.isnan(img), np.isinf(img))]=0
        img[np.isinf(img)]=0 # no NaN any more because no negate values in img
        
        d.backupChangedLayer(changes='Transform to  base 10 logarithm')
        w.update(img)
        w.updateView()


    def _buildLinkColorbar(self, menu):
        menu.clear()
        self._actions = []
        
        for d in self.display.otherDisplaysOfSameType():
            a = QtGui.QAction(d.name(),menu, checkable=True)
            menu.addAction(a)
            self._actions.append(a)

            if d in self._linked_displays:
                a.setChecked(True)
            a.triggered.connect(lambda checked, d=d, self=self: 
                                self._linkColorbar(d, checked))



    def _linkColorbar(self, display, dolink=True):
        '''
        Link gradient and range from this display to the given slave display
        '''
        master = self.display.widget.ui.histogram
        slave = display.widget.ui.histogram
        
        if dolink:
            self.setChecked(True)
            self._linked_displays.append(display)
            master.linkHistogram(slave, connect=True)
            master.gradient.linkGradient(slave.gradient, connect=True)
        else:
            self._linked_displays.remove(display)
            #undo linking:
            master.linkHistogram(slave, connect=False)
            master.gradient.linkGradient(slave.gradient, connect=False)
            #check whether at least on of the other links is still active, 
            #      else: uncheck
            inactive = True
            for a in self._actions:
                if a.isChecked():
                    inactive = False
                    break
            if inactive:
                self.setChecked(False)


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