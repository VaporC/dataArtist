import numpy as np

from dataArtist.widgets.Tool import Tool

class Average(Tool):
    '''
    add an average layer
    '''
    icon = 'average.svg'
    
    def __init__(self, plotDisplay):
        Tool.__init__(self, plotDisplay)


    def activate(self):
        curves = self.display.widget.curves
        if len(curves) == 1:
            avX = [curves[0].xData.min(), curves[0].xData.max()]
            y = curves[0].yData.mean()
            avY = [y,y]
        else:
            avX = [curve.xData for curve in self.display.widget.curves]
            avX = np.mean(avX, axis=0)
            avY = [curve.yData for curve in self.display.widget.curves]
            avY = np.mean(avY, axis=0)
        self.display.addLayer(label='Average', data=np.array((avX,avY)).T )
