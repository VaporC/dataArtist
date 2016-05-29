from pyqtgraph_karl import ErrorBarItem 
from collections import OrderedDict

from dataArtist.widgets.Tool import Tool



class ErrorBar(Tool):
    '''
    Add y-values of other plot as error bars to this one.
    '''
    icon = 'errorBar.svg'
    
    def __init__(self, plotDisplay):
        Tool.__init__(self, plotDisplay)
        
        self.errorBars = []

        pa = self.setParameterMenu() 
        
        self.pSource = pa.addChild({
            'name':'Source',
            'type':'list'})
        
        self.pBLength = pa.addChild({
            'name':'Beam length [px]',
            'type':'float',
            'value':10,
            'limits':[1,300]})
        self.pBLength.sigValueChanged.connect(self._bLengthChanged)
 
        self.pStype = pa.addChild({
            'name':'Keep curve style',
            'type':'bool',
            'value':True})
       
        self._menu.aboutToShow.connect(self._updateMenu)


    def _bLengthChanged(self, p, v):
        for e in self.errorBars:
            e.opts['beam'] = v
            e.setData(**e.opts)
        

    def _updateMenu(self):
        self._w = OrderedDict()
        for d in self.display.workspace.displays():
            if d != self.display and d.widget.__class__ == self.display.widget.__class__:
                self._w[d.name()] = d.widget
        self.pSource.setLimits(self._w.keys())
        

    def deactivate(self):
        for e in self.errorBars:
            self.display.widget.removeItem(e)
        self.errorBars = []      
        
        
    def activate(self):
        name = self.pSource.value()
        if name:
            w1 = self.display.widget
            w2 = self._w[name]
            if len(w1.curves) != len(w2.curves):
                raise Exception('number of curves between error source and this display are not equal')
            #physical size of 10 px:
            beamlength = w1.view.vb.viewPixelSize()[0] * self.pBLength.value()
            
            self.deactivate()
            
            for c1,c2 in zip(w1.curves, w2.curves):
                
                if self.pStype.value():
                    pen = c1.opts['pen']
                else:
                    pen = None
                    
                item = ErrorBarItem(x=c1.xData, 
                                    y=c1.yData, 
                                    top=c2.yData/2, 
                                    bottom=c2.yData/2, 
                                    beam=beamlength, 
                                    pen=pen)
                self.errorBars.append(item)
                w1.addItem(item)
                
            self.setChecked(True)
