from dataArtist.widgets.Tool import Tool
from pyqtgraph_karl.graphicsItems.ImageItem import ImageItem
from imgProcessor.transformations import toGray, isColor



class SwitchBetweenGridAndStackedView(Tool):
    '''
    Switch between stacked view, where every image layer
    is made visible through changing the time axis
    
    and a grid view, were every image layer is shown as a grid cell
    '''
    icon = 'stackToGrid.svg'

    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)

        pa = self.setParameterMenu() 

        self.pRNRows = pa.addChild({
            'name': 'N rows',
            'type': 'int',
            'value':2,
            'limits':[1,100]})
        self.pRNRows.sigValueChanged.connect(self._gridParamChanged)

        self.pSpace = pa.addChild({
            'name': 'Space inbetween',
            'type': 'int',
            'value':30,
            'limits':[0,1e5]})        
        self.pSpace.sigValueChanged.connect(self._gridParamChanged)


    def _gridParamChanged(self):
        if self.isChecked():
            for item, (dx,dy) in zip(self._items, 
                                     self._positions()):
                x,y = item.pos()
                item.moveBy(dx-x, dy-y)
            

    def _positions(self):
        w = self.display.widget
        nr = self.pRNRows.value()
        s = self.pSpace.value()
        
        s0,s1 = w.image.shape[1:3]

        dx,dy = 0,0
        ir = 1 #row index
        
        while True:
            if ir < nr:
                dx +=s0+s
            yield dx,dy
            
            #update grid position coords:
            ir += 1
#             dx += s0+s
            if ir >= nr:
                ir = 0
                dx = -s0-s
                dy += s1+s     





    def activate(self):
        
        self._items = []
        self._fns = []
        

        w = self.display.widget
        vb = w.view.vb
        
        if len(w.image) < 2:
            self.setChecked(False)
            raise Exception('needs multiple images for grid view')
        
        w.setCurrentIndex(0)
        w.display.widget.showTimeline(False)
        
        hist = w.ui.histogram

        for img, (px,py) in zip(w.image[1:], self._positions()):

            if isColor(img):
                #TODO: I dont know why it returns an error on color ...find out
                print 'only works on grayscale images at the moment'
                img = toGray(img)
            
            item = ImageItem(img)

            #link colorbar
            fn1 = lambda hist, i=item: i.setLookupTable(hist.getLookupTable)  
            fn2 = lambda hist, i=item: i.setLevels(hist.region.getRegion() ) 
            hist.sigLookupTableChanged.connect(fn1)
            hist.sigLevelsChanged.connect(fn2)

#             s0,s1 = img.shape[:2]
            item.moveBy(px,py)
            vb.addItem(item)
   
        
            self._items.append(item)
            self._fns.append((fn1,fn2))

        hist.sigLookupTableChanged.emit(hist)
        hist.sigLevelsChanged.emit(hist)

        ar = vb.state['autoRange']
        vb.state['autoRange'] = [True,True]
        vb.updateAutoRange()
        vb.state['autoRange'] = ar


    def deactivate(self):
        w = self.display.widget
        vb = w.view.vb
        
        w.setCurrentIndex(0)
        w.display.widget.showTimeline(True)
        
        hist = w.ui.histogram
        for item, (fn1, fn2) in zip(self._items, self._fns):
            hist.sigLookupTableChanged.disconnect(fn1)
            hist.sigLevelsChanged.disconnect(fn2)
            
            vb.removeItem(item)
            
        self._items = []
        self._fns = []
  
        ar = vb.state['autoRange']
        vb.state['autoRange'] = [True,True]
        vb.updateAutoRange()
        vb.state['autoRange'] = ar