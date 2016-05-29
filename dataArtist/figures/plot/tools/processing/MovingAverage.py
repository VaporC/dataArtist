import numpy as np

from fancytools.math.MovingAverage import MovingAverage as M

from dataArtist.widgets.Tool import Tool
from fancytools.fcollections.WeakList import WeakList


class MovingAverage(Tool):
    '''
    Smooth the plots through moving average 
    '''
    icon = 'movingAverage.svg'
    
    def __init__(self, plotDisplay):
        Tool.__init__(self, plotDisplay)
        self._curves = WeakList()
        

        pa = self.setParameterMenu() 

        self.pN = pa.addChild({
            'name':'Quantity',
            'type':'int',
            'value':2,
            'limits':[2,100000]}) 
        
        self.pDim =  pa.addChild({
            'name':'Dimension',
            'type':'list',
            'value':'y',
            'limits':['x','y', 'both']})       


    def activate(self):
        m = M(self.pN.value())

        
#         self._back = []
        for n, curve in enumerate(self.display.widget.curves):
            if curve in self._curves:
                continue
            
            m.reset()
            
            x,y = curve.xData, curve.yData
#             self._back.append((x,y))
            d = self.pDim.value()
            if d == 'both' or d == 'x':
                x = [m.update(val) for val in x]
            if d == 'both' or d == 'y':
                y = [m.update(val) for val in y] 

            #curve.setData(x,y)           

            try:
                self._curves[n].setData(x,y)
            except IndexError:
                self._curves.append( self.display.addLayer(
                                        label='Moving average n %i' %n, 
                                        data=np.array((x,y)).T ) )



#     def deactivate(self):
#         for curve, b in zip(self.display.widget.curves, self._back):
#             curve.setData(b[0],b[1])   
  