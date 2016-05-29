import numpy as np

from dataArtist.widgets.Tool import Tool


class Normalize(Tool):
    '''
    Normalize the range of the y values between 0-1
    '''
    icon = 'normalize.svg'
    
    def __init__(self, plotDisplay):
        Tool.__init__(self, plotDisplay)

        pa = self.setParameterMenu() 

        self.pReference = pa.addChild({
            'name':'Reference',
            'type':'list',
            'value':'min-max',
            'limits':['min-max', 'mean+-3*std']}) 
     

    def activate(self):
        if self.pReference.value() == 'min-max':
            fn = self._fnMinMax
        else:
            fn = self._fnMeanStd
        
        self._back = []
        for curve in self.display.widget.curves:
            self._back.append(curve.yData)
            curve.setData(curve.xData,fn(curve.yData))
            
            
    def deactivate(self):
        for curve, b in zip(self.display.widget.curves, self._back):
            curve.setData(curve.xData,b)


    def _fnMinMax(self, yvals):
        mn = np.min(yvals)
        mx = np.max(yvals)
        return (yvals - mn) / (mx-mn)
    
    
    def _fnMeanStd(self, yvals):
        mean = np.mean(yvals)
        std = np.std(yvals)
        mn = mean - 3*std
        mx = mean + 3*std
        return (yvals - mn) / (mx-mn)  