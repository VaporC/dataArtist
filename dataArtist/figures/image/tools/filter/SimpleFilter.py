


from dataArtist.widgets.Tool import Tool 




class SimpleFilter(Tool):
    '''
    Various simple spatial filters:
    * Median
    * Gaussian
    * Maximum
    * Minimum
    '''
    icon = 'filter.svg'

    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)

        #speed-up start
        from scipy.ndimage.filters import median_filter, gaussian_filter, \
                                          maximum_filter, minimum_filter
        
        from skimage.restoration import nl_means_denoising

        self.FILTER = {'median':median_filter, 
                'Gaussian':gaussian_filter, 
                'maximum':maximum_filter, 
                'minimum':minimum_filter,
                'Non-local means':nl_means_denoising}

             
        pa = self.setParameterMenu() 
        self.createResultInDisplayParam(pa)

        self.pType = pa.addChild({
            'name':'Type',
            'type':'list',
            'limits':self.FILTER.keys(),
            'value':'median'})                             
        
        self.pSeparate = pa.addChild({
            'name':'Filter layers separate',
            'type':'bool',
            'value':True})

        self.pSize = pa.addChild({
            'name':'size',
            'type':'int',
            'value':3,
            'limits':[1, 1000]})

        self.pMode = pa.addChild({
            'name':'mode',
            'type':'list',
            'limits':['reflect', 'constant', 'nearest', 'mirror', 'wrap'],
            'value':'reflect'})

        self.pCVal = pa.addChild({
            'name':'cval',
            'type':'float',
            'value':0.0,
            'limits':[0, 1000]})

        self.pOrigin = pa.addChild({
            'name':'origin',
            'type':'int',
            'value':0,
            'limits':[0, 1000]})

        self.pAddChangesLayer = pa.addChild({
            'name':'Add changes layer',
            'type':'bool',
            'value':False})

        
    def activate(self):
        self._back = self.display.widget.image    
        image = self._back.copy()

        kwargs = {'size':self.pSize.value(),
                  'mode':self.pMode.value(),
                  'cval':self.pCVal.value(),
                  'origin':self.pOrigin.value()}
        
        v = self.pType.value()

        filt= self.FILTER[v]
        
        if v == 'Gaussian':
            kwargs.pop('origin')#Gaussian doesnt have this option
            kwargs['sigma'] = kwargs.pop('size')#rename 
        elif v == 'Non-local means':
            s = kwargs.pop('size')
            kwargs['patch_size'] = s
            kwargs['patch_distance'] = int(s*1.5)
            kwargs.pop('cval')
            kwargs.pop('origin')
            kwargs.pop('mode')
        
        if self.pSeparate.value():
            #APPLY ON EACH IMAGE SEPARATELY:
            self.startThread(lambda image=image, kwargs=kwargs:
                    [filt(i, **kwargs) for i in image], self.processDone)
        else:
            #APPLY ON STACK:
            self.startThread(lambda image=image, kwargs=kwargs:
                             filt(image, **kwargs), self.processDone)
    

    def processDone(self, out):
        self.handleOutput(out, title='filtered')

        if self.pAddChangesLayer.value():
            diff = self._back - out
            self.display.widget.addColorLayer(diff, 'filter')
        del self._back