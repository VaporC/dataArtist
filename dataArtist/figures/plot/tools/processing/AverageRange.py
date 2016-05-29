import numpy as np
from pyqtgraph_karl import LinearRegionItem

from dataArtist.widgets.Tool import Tool



class AverageRange(Tool):
    '''
    average the y values of all plots within a given range
    '''
    icon = 'averageRange.svg'
    
    def __init__(self, plotDisplay):
        Tool.__init__(self, plotDisplay)

        self.region = None
        self.out = None
        self.outStd = None

        pa = self.setParameterMenu() 
        
        self.pAll = pa.addChild({
            'name':'All',
            'type':'bool',
            'value':True})
        self.pAll.sigValueChanged.connect(self._pAllChanged)

        self.pLive =  self.pAll.addChild({
            'name':'Live',
            'type':'bool',
            'value':False,
            'visible':False}) 
        self.pLive.sigValueChanged.connect(self._pLiveChanged) 
        
        self.pStart =  self.pAll.addChild({
            'name':'Start',
            'type':'float',
            'value':0,
            'visible':False})
             
        self.pStop =  self.pAll.addChild({
            'name':'Stop',
            'type':'float',
            'value':10,
            'visible':False})
 
        self.pStd =  self.pAll.addChild({
            'name':'Standard deviation',
            'type':'bool',
            'value':False})


    def _pLiveChanged(self, param, live):
        if live:
            if self.region is None: 
                self.region = LinearRegionItem()
                self.region.setZValue(10)
                # Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this 
                # item when doing auto-range calculations.
                self.display.widget.addItem(self.region, ignoreBounds=True)
                self.region.sigRegionChanged.connect(self._updatePStartStop)
            else:
                self.region.show()
        else:
            self.region.hide()
            
        if self.region is not None:
            try:
                self.region.sigRegionChanged.disconnect(self._regionChanged )
            except:
                pass
            if live:
                self.region.sigRegionChanged.connect(self._regionChanged )


    def _regionChanged(self, region):
        self._update( region.getRegion() )

          
    def _pAllChanged(self, param, value):
        [ch.show(not value) for ch in param.children()]
        if all and self.region is not None:
            self.region.hide()


    def _updatePStartStop(self, region):
        mn, mx = region.getRegion()
        self.pStart.setValue(mn)
        self.pStop.setValue(mx)
        

    def _update(self, limits=None):
        curves = self.display.widget.curves
        x = self.display.stack.values
        y = []
        s = self.pStd.value()
        yStd = []
        for curve in curves:
            if limits:
                b1 = np.argmax(curve.xData>=limits[0])
                b2 = np.argmax(curve.xData>=limits[1])
                if b2 == 0:
                    b2 = -1
            else:
                b1,b2 = None,None
                
            y.append(np.nanmean(curve.yData[b1:b2]))
            if s:
                yStd.append(np.nanstd(curve.yData[b1:b2]))

        if self.out == None or self.out.isClosed():
            self.out = self.display.workspace.addDisplay( 
                    origin=self.display,
                    axes=self.display.axes.copy(('stack',1)), 
                    title='ROI',
                    names=['ROI'],
                    data=[(x,y)])
        else:
            self.out.widget.curves[0].setData(x,y)
        
        if s:
            if self.outStd == None or self.outStd.isClosed():
                self.outStd = self.display.workspace.addDisplay( 
                        origin=self.display,
                        axes=self.display.axes.copy(('stack',1)), 
                        title='ROI - std',
                        names=['ROI - std'],
                        data=[(x,yStd)])
            else:
                self.outStd.widget.curves[0].setData(x,yStd)         


    def activate(self):
        if not self.pAll.value():
            limits = (self.pStart.value(), self.pStop.value())
        else:
            limits = None
        self._update(limits)
