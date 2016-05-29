import numpy as np

#OWN
from _ROI import ROIArea, ROITool



class HistogramROI(ROITool):
    '''
    add averaged regions of interest (ROI)
    '''
    icon = 'histogramROI.svg'
    def __init__(self, display):
        ROITool.__init__(self, display)
        self.scene = self.view.scene()
        self.ROI01Slave = None

        self.pLimitBins = self._menu.p.addChild({
            'name': 'Limit number of bins',
            'type': 'bool',
            'value':False,
            'tip':'If False: number of bins is calculated by max(img)-min(img)'})     
        self.pLimitBins.sigValueChanged.connect(lambda param, value: 
                        [ch.show(value) for ch in param.children()] )  

        self.pNBins = self.pLimitBins.addChild({
            'name': 'number of bins',
            'type': 'int',
            'value':100,
            'limits':[1,1e4],
            'visible':False})

        self.pLimitRange = self._menu.p.addChild({
            'name': 'Limit Range',
            'type': 'bool',
            'value':False})     
        self.pLimitRange.sigValueChanged.connect(lambda param, value: 
                        [ch.show(value) for ch in param.children()] )  
              
        self.pRangeFrom = self.pLimitRange.addChild({
            'name': 'From',
            'type': 'float',
            'value':0,
            'limits':[0,2**24],
            'visible':False})  
        
        self.pRangeTo = self.pLimitRange.addChild({
            'name': 'To',
            'type': 'float',
            'value':2**16,
            'limits':[0,2**24],
            'visible':False}) 
        
        #update view when parameters changed:
        for p in (self.pLimitBins, self.pNBins, self.pLimitRange,
                  self.pRangeFrom, self.pRangeTo):
            p.sigValueChanged.connect(
                    lambda: [r.updateView() for r in  self.ROIs])
        

    def activate(self):
        slave = None
        ROI = _HistogramROIArea
        axes = (self.display.axes[0].duplicate(), 'N Pixels') 
        
        #USE THE LAST ROI SLAVE DISPLAY IF APPLICABLE:
        if self.ROI01Slave and self.ROI01Slave.isVisible():
            slave = self.ROI01Slave
                
        name = '%s[%s]' %(ROI.name, str(len(self.ROIs)+1))

        if slave is None:
            #CREATE A NEW SLAVE DISPLAY
            self.ROI01Slave = slave = self.display.workspace.addDisplay( 
                        axes=axes, 
                        title='%s of %s' %(name, self.display.shortName()) 
                                              )
        #SET DATA:
        w = self.display.widget
        index=None
        if not self.pPlotAll.value():
            index = w.currentIndex
        
        #take middle of current position
        r = self.display.widget.view.vb.viewRange()  
        p = ((r[0][0]+r[0][1])/2, (r[1][0]+r[1][1])/2)
        
        #CREATE NEW ROI:
        roi = ROI(self, 
                    self.display, 
                    slave, 
                    name, 
                    index=index,
                    pen=(len(self.ROIs)%6),
                    pos=p)
        self.ROIs.append(roi)
        return roi


    def getSymbol(self):
        s = self.img.shape
        if s[0] == 1 or len(s) == 2: #one point
            return 'o'



class _HistogramROIArea(ROIArea):
    '''
    a histogram of the image
    '''
    name = 'Histogram'
    def __init__(self, *args, **kwargs):
        self.plots = []
        ROIArea.__init__(self, *args, **kwargs)


    def setup(self):
        ROIArea.setup(self)
        self.addScaleHandle([1, 1], [0,0])

        for n in self.masterDisplay.layerNames():
            self.plots.append(self.slaveDisplay.addLayer(
                                                layer='%s - %s' %(self.name,n)))


    def updateView(self):
        #COORDS
        px,py = self.pos().x(), self.pos().y()
        r = self.boundingRect()
        x0,y0,x1,y1 = r.getCoords()
        x0 = max(0,int(round(x0+px)))
        x1 = int(round(x1+px))
        y0 = max(0,int(round(y0+py)))
        y1 = int(round(y1+py))

        self.text.setPos(px,py)
 
        simg = self.img
        if simg.ndim == 2:
            simg = [simg]

        f = self.tool.pRangeFrom.value()
        t = self.tool.pRangeTo.value()
       
        for img, plot in zip(simg, self.plots):
        #DATA
            try:
                img_cut = img[x0:x1, y0:y1]
                nBins = None
                if self.tool.pLimitRange.value():
                    img_cut[img_cut<f] = np.nan
                    img_cut[img_cut>t] = np.nan
                    nBins = int(t-f)
                
                if self.tool.pLimitBins.value():
                    nBins = self.tool.pNBins.value()
                
                elif not nBins:
                    nBins = int( np.max(img_cut)-np.min(img_cut) )
                    if nBins < 100:
                        #e.g. when scaling 0-1
                        nBins = 100   
                hist, bin_edges = np.histogram(img_cut, nBins)    
                #TODO: take mean of the bin edges
                plot.setData(y=hist, x=bin_edges[:-1])
    
            except (IndexError, ValueError),err:
                # out out bounds
                print err