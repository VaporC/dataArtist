import numpy as np

from dataArtist.widgets.Tool import Tool



class Squeeze(Tool):
    '''
    Show changes within the stack layers relative to a reference layer
    as semi-transparent colour overlay
    '''
    icon = 'squeeze.svg'
    #TODO: set gradient points at each layer - fill with color
    #TODO: decide whether pos/neg/abs changed to plot
    #TODO. if 2 img are comp. together a pos/neg colorbar is possible
    #TODO: opt which base image
    #TODO: transparency slider
    #TODO: histogram values according to z-axis
    #TODO: greyscalecheck
            # s = self.imageView.image.shape
            # if not ( len(s) == 3 and s[2] in (3,4)#isGrayscale():
                #    raise Exception( 'can only activate if images are greyscale')


    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)

        self.methods = {
             'absolute':self._absolute,
            # 'relative':self._relative,
             'positive':self._pos,
             'negative':self._neg}

        pa = self.setParameterMenu() 

        self.pRefLayer = pa.addChild({
            'name': 'Reference Image',
            'type': 'list',
            'limits':[]})
        self._menu.aboutToShow.connect(
            lambda: self.pRefLayer.setLimits(self.display.layerNames()))

        self.pMethod = pa.addChild({
            'name': 'Method',
            'type': 'list',
            'limits':['absolute','positive', 'negative'] })

        self.pAlpha = pa.addChild({
            'name': 'Alpha',
            'type': 'float',
            'value':1,
            'limits':[0,1]})

        self.pFilter = pa.addChild({
            'name': 'Filter values',
            'type': 'bool',
            'value':False})
        self.pFilter.sigValueChanged.connect(lambda p,v:
                        [ch.show(v) for ch in p.childs])

        self.pFilterRelative = self.pFilter.addChild({
            'name': 'relative values',
            'type': 'bool',
            'value':False,
            'visible':False,
            'tip': 'True: filter values from 0 to 1 (100%)-max.value; False: absolute values'})
        self.pFilterRelative.sigValueChanged.connect(self._filterRelativeChanged )

        self.pFilterFrom = self.pFilter.addChild({
            'name': 'From',
            'type': 'float',
            'value':0,
            'visible':False,
            'limits':[0,1] })
        self.pFilterTo = self.pFilter.addChild({
            'name': 'To',
            'type': 'float',
            'value':1,
            'visible':False,
            'limits':[0,1] })

        
    def _filterRelativeChanged(self, param, value):
        self.pFilterFrom.setName('From [%]' if value else 'From')
        self.pFilterTo.setName('To [%]' if value else 'To')
        if value:
            l = [0,1]
        else:
            #cannot unset limit a.t.m. so set wide range
            l = [-1e20,1e20]
        self.pFilterFrom.setLimits(l)
        self.pFilterTo.setLimits(l)


    @staticmethod
    def _absolute(arr,bg):
        return np.abs(arr-bg)
    
    
#     @staticmethod    
#     def _relative(arr,bg):
#         return np.abs((arr-bg)/bg)
    
    @staticmethod
    def _pos(arr,bg):
        arr-=bg
        arr[arr<0]=0
        return arr
    
    
    @staticmethod
    def _neg(arr, bg):
        arr-=bg
        arr[arr>0]=0
        arr*=-1
        return arr


    def activate(self):
        w = self.display.widget
        if len(w.image) == 1:
            raise Exception('need a 3d-image for the z-stack tools')
        
        #GET INDEX OF THE BACKGROUND LAYER:
        val = self.pRefLayer.value()
        vals = self.display.layerNames()
        if not val:
            bg_index = 0
        else:
            bg_index = vals.index(val)
            
        #COLOR LAYERS:
        colorLayers = w.image.copy().astype(float)
        bg = colorLayers[bg_index]
            #REMOVE BACKGROUND:
        colorLayers = np.delete(colorLayers, bg_index, axis=0)
        method = self.methods[self.pMethod.value()]
            #PROCESS:
        colorLayers = method(colorLayers,bg)

        f = self.pFilterFrom.value()
        t = self.pFilterTo.value()

        mx = np.max(colorLayers)
        colorLayers /= mx
        if self.pFilter.value():
            if not self.pFilterRelative.value():
                f /=mx
                t /=mx
            if f > 0:
                colorLayers[colorLayers<f] = f
                colorLayers -= f
            if t < 1:
                colorLayers /= t
                colorLayers[colorLayers>1] = 1
        
        self.cNames = []
        m = 0
        #ADD COLOR LAYERS AS OVERLAY:
        for n,zval in enumerate(self.display.stack.values):
            if n != bg_index:
                name = str(zval)
                w.addColorLayer(colorLayers[m], name, tip='', 
                                alpha=self.pAlpha.value())
                self.cNames.append(name)
                m += 1


    def deactivate(self):
        for name in self.cNames:
            try:
                self.display.widget.removeColorLayer(name)
            except KeyError:
                pass #layer removed otherwise                
        self.cNames = []