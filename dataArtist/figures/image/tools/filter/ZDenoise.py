import numpy as np
from imgProcessor.transform.imgAverage import imgAverage
from imgProcessor.features.SingleTimeEffectDetection import SingleTimeEffectDetection

#OWN
from dataArtist.widgets.Tool import Tool



class ZDenoise(Tool):
    '''
    Average image with optional Single-Time-Effect removal
    '''
    icon = 'singleTimeEvents.svg'
    
    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)
        
        pa = self.setParameterMenu() 
        self.createResultInDisplayParam(pa)

        self.pSTEremoval = pa.addChild({
            'name': 'Single-time-effect removal',
            'type': 'bool',
            'value':True}) 

        self.pAverageAll =  pa.addChild({
            'name': 'Average all',
            'type': 'bool',
            'value':True}) 
        
        self.pAverageN =  self.pAverageAll.addChild({
            'name': 'New layer every every N images',
            'type': 'int',
            'value':2,
            'limits':[2,1000],
            'visible':False}) 
        self.pAverageAll.sigValueChanged.connect(lambda param, val:
                            self.pAverageN.show(not val))
        
        self.pChangesLayer = self.pSTEremoval.addChild({
            'name': 'Add changes layer',
            'type': 'bool',
            'value':False}) 
        
        self.pNStd = self.pSTEremoval.addChild({
            'name': 'nStd',
            'type': 'float',
            'value':4,
            'tip':'factor image difference over local noise'}) 
        
        self.pSTEremoval.sigValueChanged.connect(lambda p, v:
                            [c.show(p.value()) for c in p.childs])


    def activate(self): 
        self.startThread(self._process, self._done)


    def _process(self):
        img = self.display.widget.image
        
        if img is None:
            img = self.display.filenames
            nLayers = len(img)
        else:
            #img = im.copy()
            if img.ndim > 3:
                nLayers = 1
            else:
                nLayers = len(img)
            
        if nLayers < 2:
            raise Exception('Need at least 2 images')
        
        out = []
        indices = []
        n = self.pAverageN.value()
        old_i = 0
        
        names = []
        
        remove_ste = self.pSTEremoval.value()
        show_changes = self.pChangesLayer.value()


        def fn(img, i0,i1):
            if remove_ste:
                ste = SingleTimeEffectDetection(
                                        img[i0:i1],
                                        save_ste_indices=show_changes,
                                        nStd=self.pNStd.value() )
                out.append(ste.noSTE)
                indices.append(ste.mask_STE)
            else:
                out.append(imgAverage(img[i0:i1]))
            names.append('img[%s:%s]' %(i0,i1))

        #AVERAGE ALL
        if self.pAverageAll.value():
            fn(img, 0,len(img)) 
        else:
            #AVERAGE N IMAGES AND CREATE MUTLIPLE LAYERS
            for i in range(n,nLayers+n,n):
                fn(img, old_i,i)
                old_i = i
        
        if len(indices) == 1:
            indices = indices[0]
        else:
            indices = np.array(indices)          

        return out, indices, names
    
    
    def _done(self, (out,indices, names)):
        d = self.handleOutput(out, title='Z denoised', names=names)
        #CHANGES LAYER
        if self.pSTEremoval.value() and self.pChangesLayer.value() and indices.any():
            d.clicked.emit(d)#load toolbars
            d.widget.addColorLayer(layer=indices, name='single time effects', tip='blablabla')
