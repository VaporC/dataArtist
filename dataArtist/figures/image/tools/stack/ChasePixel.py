import numpy as np
from scipy.ndimage import median_filter
  
#OWN
from dataArtist.widgets.Tool import Tool 



class ChasePixel(Tool):
    '''
    Plot the value of multiple pixels (given by a color layer)
    over their changes within the stack relative to layer 0
    '''
    icon = 'chasePixel.svg'

    def __init__(self, display):
        Tool.__init__(self, display)
  
        pa = self.setParameterMenu() 

        self.pMask = pa.addChild({
            'name':'Pixel mask from color layer',
            'type':'list',
            'value':'',
            'limits':[]})
        
        self.pMaxPlots = pa.addChild({
            'name':'Max n plots',
            'type':'int',
            'value':100,
            'limits':[1,1e5]})

        self.pDivideBG = pa.addChild({
            'name':'Divide background',
            'type':'bool',
            'value':True})
        
        self.pBgSize = pa.addChild({
            'name':'Background median kernel size',
            'type':'int',
            'value':3,
            'limits':[1,1e5]})

        self._menu.aboutToShow.connect(self._setPixelMaskOptions)


    def _setPixelMaskOptions(self):
        '''
        fill the pMask parameter with the names of all color layers in this display
        '''
        self.pMask.setLimits(self.display.widget.cItems.keys())


    def activate(self):  
        #CHECK PIXEL MASK:
        if not self.pMask.value():
            self._setPixelMaskOptions()
            if not self.pMask.value():
                raise Exception('no pixel mask given')

        w = self.display.widget
        #CHECK STACK
        if len(w.image) == 1:
            raise Exception('needs image stack')
        
        indices = w.cItems[self.pMask.value()].image > 0
        if indices.ndim == 3: #indices from image stack
            #take indices from last/current image
            indices = indices[-1]#???[w.currentIndex]
 
        xvals = self.display.stack.values
        yvals = [] #pixel values
        for layer in w.image:
            y = layer[indices][:self.pMaxPlots.value()]
            yvals.append(y)
        yvalsCorr = np.array(yvals).T

        plots = []
        names = []
        for n,y in enumerate(yvalsCorr):
            #CREATE A PLOT FOR EACH PIXEL:
            plots.append((xvals, y))
            names.append(str(n))        
            
        self.display.workspace.addDisplay(
                origin=self.display,
                axes=self.display.axes.copy(('stack',0)),
                names=names,
                data=plots, 
                title='pixel abs value')
        
        #BACKGROUND CORRECTION:
        if self.pDivideBG.value():
            #TODO: don't apply median filter on full image but only 
            #      on the neighbours of the px mask, if that's faster
            #BACKGROUND AS MEDIAN OF THE LOCAL AREA:
            bg = median_filter(w.image, size=self.pBgSize.value())
            
            yvals_bg = [] 
            for layer,y in zip(bg, yvals):
                bg_px = layer[indices][:self.pMaxPlots.value()]
                yvals_bg.append(y/bg_px)
            yvals_bg = np.array(yvals_bg).T
            
            plots = []
            names = []
            xvals = self.display.stack.values
            for n,y in enumerate(yvals_bg):
                plots.append((xvals, y))
                names.append(str(n))
    
            self.display.workspace.addDisplay(
                    origin=self.display,
                    axes=self.display.axes.copy(('stack',0)),
                    names=names,
                    data=plots, 
                    title='pixel bg corr')