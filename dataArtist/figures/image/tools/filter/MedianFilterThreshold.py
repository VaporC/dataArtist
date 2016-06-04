from imgProcessor.filters.medianThreshold import medianThreshold

from dataArtist.widgets.Tool import Tool


class MedianFilterThreshold(Tool):
    __doc__ = medianThreshold.__doc__
    icon = 'medianThreshold.svg'

    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)        
        
        pa = self.setParameterMenu() 
        self.createResultInDisplayParam(pa)

        self.pSize = pa.addChild({
            'name':'Size',
            'type':'int',
            'value':3,
            'limits':[1, 1000]})
        
        self.pThreshold = pa.addChild({
            'name':'Threshold',
            'type':'float',
            'value':0.2,
            'tip': 'ratio to exceed to be filtered'})
        self.pCondition = pa.addChild({
            'name':'Condition',
            'type':'list',
            'value':'>',
            'limits': ['>', '<']})
        
        self.pAddChangesLayer = pa.addChild({
            'name':'Add changes layer',
            'type':'bool',
            'value':True})


    def activate(self):  
        img = self.display.widget.image
        #PROCESS:
        (out, indices) = medianThreshold(
                            img, self.pThreshold.value(), 
                            self.pSize.value(), 
                            self.pCondition.value(),
                            copy=self.pOutDisplay.value()!='[REPLACE]' )
        #DISPLAY:
        self.handleOutput(out, title='MedianThreshold', changes='median threshold')
        #CHANGES:
        if self.pAddChangesLayer.value() and indices.any():
            self.display.widget.addColorLayer(indices, 'medianThreshold', tip='blablabla')
