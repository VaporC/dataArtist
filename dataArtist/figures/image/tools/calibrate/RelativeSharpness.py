import numpy as np

from imgProcessor.measure.sharpness import parameters
 
from dataArtist.widgets.Tool import Tool



class RelativeSharpness(Tool):
    '''
    Calculate the sharpness of one or more input images.
    This method is suitable to best the best camera focus.
    '''
    icon = 'sharpness.svg'
    
    def __init__(self, display):
        Tool.__init__(self, display)

        self.outDisplay = None

        self._method = {
            'tenengrad':parameters.tenengrad,
            'modifiedLaplacian':parameters.modifiedLaplacian,
            'varianceOfLaplacian':parameters.varianceOfLaplacian,
            'normalizedGraylevelVariance':parameters.normalizedGraylevelVariance
                        }

        pa = self.setParameterMenu() 

        self.pLayer = pa.addChild({
            'name': 'apply on',
            'type': 'list',
            'value':'all layers',
            'limits': ['all layers', 'last layer']})       

        self.pNewDisplay = pa.addChild({
            'name': 'create new display',
            'type': 'bool',
            'value':False})      

        self.pMethod = pa.addChild({
            'name': 'method',
            'type': 'list',
            'value':'tenengrad',
            'limits': self._method.keys()}) 


    def activate(self):
        im = self.display.widget.image
        if im is None:
            raise Exception('no images loaded')

        if self.pLayer.value() == 'last layer':
            im = [im[-1]]
        fn = self._method[self.pMethod.value()]
        
        d = [np.array([fn(i) for i in im])]     

        if ( not self.pNewDisplay.value() 
             and self.outDisplay 
             and not self.outDisplay.isClosed() ):
            #append new points
            for curve,newY in zip(self.outDisplay.widget.curves, d):
                x,y = curve.xData, curve.yData
                newX = len(x)  
                x = np.append(x,newX)
                y = np.append(y,newY)
                curve.setData(x,y) 
        else:
            self.outDisplay = self.display.workspace.addDisplay( 
                            origin=self.display,
                            axes=self.display.axes.copy(('stack',0)), 
                            data=d, 
                            title='sharpness')
