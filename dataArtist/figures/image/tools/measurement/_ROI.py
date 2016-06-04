import pyqtgraph_karl as pg

from dataArtist.widgets.Tool import Tool



class ROITool(Tool):
    '''
    Base class for AverageROI and HistogramROI
    '''
    def __init__(self, display):
        Tool.__init__(self, display)

        self.ROIs = []

        pa = self.setParameterMenu() 

        self.pPlotAll = pa.addChild({
            'name': 'Plot from all Img layers',
            'type': 'bool',
            'value':True}) 
        
        pShow = pa.addChild({
            'name': 'Show ROIs',
            'type': 'bool',
            'value':True})
        pShow.sigValueChanged.connect(lambda param, val, self=self: 
                        [roi.show(val) for roi in self.ROIs])

        pShowLabels = pa.addChild({
            'name': 'Show ROI labels',
            'type': 'bool',
            'value':True})
        pShowLabels.sigValueChanged.connect(lambda param, val, self=self: 
                        [roi.showLabels(val) for roi in self.ROIs])
        
        pDelete = pa.addChild({
            'name': 'Delete ROIs',
            'type': 'action',
            'value':True})
        pDelete.sigActivated.connect(lambda param: 
                        [roi.close() for roi in self.ROIs])

        self.pROIs = pa.addChild({
            'name': 'ROIs',
            'type': 'empty',
            'isGroup':True}) 
        
        self._menu.aboutToShow.connect(self._buildROIMenu)


    def _buildROIMenu(self):
        self.pROIs.clearChildren()
        for roi in self.ROIs:
            p = self.pROIs.addChild({
            'name': roi.roiName(),
            'renamable':True,
            'removable':True,
            'type': 'empty',
            'isgroup':True})
            p.sigNameChanged.connect(lambda param, value, roi=roi: 
                                            roi.setName(value))
            p.sigRemoved.connect(lambda roi=roi: 
                                            roi.close())
            pos = p.addChild({
            'name': 'Position',
            'type': 'str',
            'value':str(tuple([round(s,1) for s in roi.pos()]))})
            pos.sigValueChanged.connect(lambda param, value, roi=roi: 
                                            roi.setPos(eval(value)))
            size = p.addChild({
            'name': 'Size',
            'type': 'str',
            'value':str(tuple([round(s,1) for s in roi.state['size']]))})
            size.sigValueChanged.connect(lambda param, value, roi=roi: 
                                            roi.setSize(eval(value)))
  


class ROIArea(pg.ROI):
    '''
    Base ROI object including a text item
    '''

    def __init__(self, tool, masterDisplay, slaveDisplay, name, 
                 index, pen='r', pos=[10,10], size=[50,50]):

        self.text = pg.TextItem(
                        text=name, 
                        color=(0,0,0), 
                        html=None, 
                        anchor=(0, 0), 
                        border=None, 
                        fill=pg.mkBrush(255, 255, 255, 80), 
                        angle=0)

        pg.ROI.__init__(self, pos=pos, size=size, angle=0.0, pen=pen)
 
        self.tool = tool
        self.masterDisplay = masterDisplay
        self.master = masterDisplay.widget
        self.slaveDisplay = slaveDisplay
        self.index = index
        self._pen = pen

        #CONNECT SIGNALS:
        self.masterDisplay.closed.connect(self._masterClosed) 
        self.master.item.sigImageChanged.connect(self.updateView) 
        #display closed:       
        self.slaveDisplay.closed.connect(self.close)
        #TODO: layer removed:
        #if index != None:
        #self.slaveDisplay.stack.childs[].sigClosed...
        self.sigRegionChanged.connect(self.updateView)
        self.tool.pPlotAll.sigValueChanged.connect(self.setup)
        self.tool.display.stack.sigValuesChanged.connect(self.updateView)
        
        #FURTHER METHODS:
        self.setup()
        self.updateView()


    def _masterClosed(self):
        '''
        roi still exists but doesnt listen to changes in the master display
        '''
        try:
            self.master.item.sigImageChanged.disconnect(self.updateView) 
        except TypeError:
            pass #'instancemethod' object is not connected
        self.sigRegionChanged.disconnect(self.updateView)
        self.tool.display.stack.sigValuesChanged.disconnect(self.updateView)


    @property
    def img(self):
        img = self.masterDisplay.widget.image
        if self.index != None:
            return img[self.index]
        return img
            

    def setup(self):
        self.master.addItem(self.text)
        self.master.addItem(self)
    

    def showLabels(self, value):
        if value:
            self.text.show()
        else:
            self.text.hide()


    def roiName(self):
        return unicode(self.text.textItem.toPlainText())


    def setName(self, name):
        return self.text.setText(name)


    def setPos(self, pos, **kwargs):
        '''
        include the textitem
        '''
        self.text.setPos(pos[0],pos[1])
        pg.ROI.setPos(self, pos, **kwargs)


    def setupUpdateView(self, dummy):
        pass


    def show(self, show):
        '''
        show/hide ROI area and its textItem
        '''
        if show:
            self.text.show()
            pg.ROI.show(self)
        else:
            self.text.hide()
            pg.ROI.hide(self)           


    def close(self):
        '''
        Close ROI area and disconnect all combined methods
        '''
        self.slaveDisplay.closed.disconnect(self.close)
        try: self.master.item.sigImageChanged.disconnect(self.updateView)
        except TypeError: pass 
        self.tool.pPlotAll.sigValueChanged.disconnect(self.setup)
        self.tool.display.stack.sigValuesChanged.disconnect(self.updateView)
        self.master.removeItem(self)
        self.master.removeItem(self.text)
        self.tool.ROIs.remove(self)