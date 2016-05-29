from scipy.ndimage import sobel
import numpy as np

from dataArtist.widgets.Tool import Tool



class EdgeDetection(Tool):
    '''
    Execute an edge detection (Sobel)
    '''
    icon = 'edgeDetection.svg'

    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)        
        pa = self.setParameterMenu() 
        self.createResultInDisplayParam(pa)


    @staticmethod
    def _filter(img):
        sx = sobel(img, axis=0, mode='constant')
        sy = sobel(img, axis=1, mode='constant')
        return np.hypot(sx, sy)


    def activate(self):  
        out = []
        for i in self.display.widget.image:
            out.append(self._filter(i))

        self.handleOutput(out, title='Edge filtered (sobel)')