import numpy as np
 
#OWN
from dataArtist.widgets.Tool import Tool
from dataArtist.functions import RMS



class PlotTrend(Tool):
    '''
    Plot the trend of pixels within a certain intensity range
    E.g.: whether brighter pixels are also getting brighter over time
    '''
    icon = 'trend.svg'
    
    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)

        pa = self.setParameterMenu() 

        self.pNPlots = pa.addChild({
            'name': 'Number of plots',
            'type': 'int',
            'value':10,
            'limits':[1,10000]}) 

        self.pVar = pa.addChild({
            'name': 'Show Variance',
            'type': 'bool',
            'value':False}) 
        
        self.pRMS = pa.addChild({
            'name': 'Show RMS',
            'type': 'bool',
            'value':False}) 

        self.pLimitRange = pa.addChild({
            'name': 'Limit Range',
            'type': 'bool',
            'value':False}) 
        self.pLimitRange.sigValueChanged.connect(lambda param, val: 
                [ch.show(val) for ch in param.children()])
        
        self.pMin = self.pLimitRange.addChild({
            'name': 'Minimum',
            'type': 'float',
            'value':0,
            'limits':[0,1e10],
            'visible':False}) 

        self.pMax = self.pLimitRange.addChild({
            'name': 'Maximum',
            'type': 'float',
            'value':255,
            'visible':False}) 
 

    def activate(self):
        img = self.display.widget.image
        
        if self.pLimitRange.value():
            mn,mx = self.pMin.value(), self.pMax.value()
        else:
            mn, mx = np.min(img[0]), np.max(img[0])
            
        bins = np.linspace(mn, mx, self.pNPlots.value()+1)
        plots = []
        var_plots = []
        rms_plots = []
        names = []
        xvals = self.display.stack.values
        for start, stop in zip(bins[:-1],bins[1:]):
            #get positions from first image:
            indexes = np.logical_and(img[0]>=start,img[0]<=stop)
            nPx = np.sum(indexes)
            if not nPx:
                #no values found in given range / one one element is True
                continue
            yvals = []
            var_yvals = []
            rms_yvals = []
            names.append('(%s) %s - %s' %(nPx, round(start,2),round(stop,2))) 
            
            #prevent stack overflow with float16 (with returns inf):
            #dtype = np.float32 if img[0].dtype==np.float16 else None    
      
            for layer in img:
                #CALCULATE PLOT VALUES:
                mean = np.mean(layer[indexes])
                yvals.append(mean)
                if self.pVar.value():
                    var_yvals.append(np.var(layer[indexes]))
                if self.pRMS.value():
                    rms_yvals.append(RMS(layer[indexes]) - mean)                    
            #APPEND PLOT VALUES:    
            plots.append((xvals, yvals))
            var_plots.append((xvals, var_yvals))
            rms_plots.append((xvals, rms_yvals))
            
        #CREATE DISPLAYS:
        self.display.workspace.addDisplay(
                origin=self.display,
                axes=self.display.axes.copy(('stack',0)),
                names=names,
                data=plots, 
                title='Averaged trend')   
        
        if self.pVar.value():
            self.display.workspace.addDisplay(
                    origin=self.display,
                    axes=self.display.axes.copy(('stack',0)),
                    names=names,
                    data=var_plots, 
                    title='Variance trend ')   

        if self.pRMS.value():
            self.display.workspace.addDisplay(
                    origin=self.display,
                    axes=self.display.axes.copy(('stack',0)),
                    names=names,
                    data=rms_plots, 
                    title='RMS trend - %s')                   