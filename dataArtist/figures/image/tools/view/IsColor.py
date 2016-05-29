import numpy as np

from dataArtist.widgets.Tool import Tool

from imgProcessor.transformations import isColor, toColor, toGray


class IsColor(Tool):
    '''
    Indicate whether image is color 
    activate: transform image to color image
    deactivate: transform image to grayscale image
    '''
    icon = 'isColor.svg'
    
    def __init__(self, display):
        Tool.__init__(self, display)
        
        display.sigLayerChanged.connect(self._check)
        display.sigNewLayer.connect(self._check)

        pa = self.setParameterMenu() 

        pSep = pa.addChild({
            'name': 'Separate color channels',
            'type': 'action'}) 
        pSep.sigActivated.connect(self.separate)

        self.createResultInDisplayParam(pa)
        
        self._check()


    def _check(self):
        i = self.display.widget.image
        if i is not None:
            self.setChecked(isColor(i))


    def separate(self):
        i = self.display.widget.image
        assert isColor(i), 'Only works on color images'
        out = np.transpose(i, axes=(3,0,1,2))
        self.handleOutput(out, title='Color channels separated', 
                               names=['red', 'green', 'blue'])

        
    def activate(self):
        w = self.display.widget
        w.setImage(toColor(w.image))


    def deactivate(self):
        w = self.display.widget
        w.setImage(toGray(w.image))