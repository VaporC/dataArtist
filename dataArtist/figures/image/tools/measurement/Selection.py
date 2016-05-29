import numpy as np

from pyqtgraph_karl.functions import mkPen, mkBrush
from pyqtgraph_karl.Qt import QtCore, QtGui
import pyqtgraph_karl as pg
import cv2


#OWN
from dataArtist.widgets.Tool import Tool
from dataArtist.items.FreehandItem import FreehandItem
from dataArtist.items.QPainterPath import QPainterPath
from dataArtist.items.GridROI import GridROI



class Selection(Tool):
    '''
    Mark and measure image features using various selection types, like
        freehand and rectangle
    '''
    icon = 'selection.svg'
    
    def __init__(self, display):
        Tool.__init__(self, display)

        self.paths = []
        #min time difference to add a line to qpainterpath 
        #when drawing in [ms]:
        self.MIN_DT = 25
        self._timer = QtCore.QTime()
       
        self.pa = self.setParameterMenu()
        self.pa.sigChildRemoved.connect(self._removePath)

        self.pType = self.pa.addChild({
            'name': 'Type',
            'type': 'list',
            'value':'Freehand',
            'limits':['Freehand', 'Rectangle', 'Grid', 'Isolines','Ellipse']}) 

        self.pNew = self.pa.addChild({
            'name': 'New',
            'type': 'action',
            'value':True}) 
        self.pNew.sigActivated.connect(self._new)
        self.pNew.sigActivated.connect(self._menu.resizeToContent)

        pMask = self.pa.addChild({
            'name': 'Create Mask',
            'type': 'action'})
        pMask.sigActivated.connect(self._createMaskFromSelection)

        pArea = self.pa.addChild({
            'name': 'Measure areas',
            'type': 'action'})
        pArea.sigActivated.connect(self._measurePath)

        self.pMask = pArea.addChild({
            'name': 'Relative to selection',
            'type': 'list',
            'value':'-',
            'limits':['-']})
        self.pMask.items.keys()[0].widget.showPopup = self._updatePMask


    def _updatePMask(self):
        l = ['-']
        l.extend([p.name() for p in self.pa.childs[3:]])
        self.pMask.setLimits(l)
        i = self.pMask.items.keys()[0].widget
        i.__class__.showPopup(i)


    def _new(self):
        pen = mkPen(10, len(self.paths)+2)
        name = typ = self.pType.value()
        self._add(typ,name, {'pen':pen})


    def _add(self, typ, name, state):
        self.curIndex = -1

        p = self.pa.addChild({
            'name': '[%i] %s' %(len(self.paths)+1,name),
            'type': 'empty',
            'isGroup':True,
            'removable':True,
            'renamable':True,
            'autoIncrementName':True}) 
        
        if typ == 'Freehand':
            path = self._addFreehand(p,state)
            if path.isEmpty():
                self._initFreehand()
        elif typ == 'Grid':
            path = self._addGrid(p, state)
        elif typ == 'Isolines':
            path = self._addIso(p, state)
        elif typ == 'Rectangle':
            path = self._addROI(_Rect, p, state)
        elif typ == 'Ellipse':
            path = self._addROI(_Ellipse, p, state)

        self.paths.append(path)

        color = state['pen'].color()
        
        pLineColor = p.addChild({
            'name':'Line color',
            'type':'color',
            'value':color,
            'path':path}) 
        pLineColor.sigValueChanged.connect(self._changeLineColor)

        if 'brush' in state:
            br = state['brush'].color()
        else:
            br = QtGui.QColor(color)
            br.setAlpha(25)
            path.setBrush(br)
        
        pFillColor = p.addChild({
            'name':'Fill color',
            'type':'color',
            'value':br,
            'path':path}) 
        pFillColor.sigValueChanged.connect(self._changeFillColor)

        self.setChecked(True)
        

    def _initFreehand(self):
        w = self.display.widget
        self._mouseDragEvent = w.view.vb.mouseDragEvent
        w.view.vb.mouseDragEvent = self._drawFreehand
        self._timer.start()


    def _changeLineColor(self, param, val):
        p = param.opts['path']
        p.setPen(val)


    def _changeFillColor(self, param, val):
        c = param.opts['path']
        c.setBrush(val)


    def _getPathIndex(self, param):
        i = param.parent().childs.index(param)
        return i-4


    def _modifyFreehand(self, param):
        path = self.paths[self._getPathIndex(param.parent())]
        if path.isModify:
            param.setName('Modify')
            path.setModify(False)
        else:
            param.setName('Done Modify')
            path.setModify(True)


    def _setFreehandIsArea(self, param, value):
        path = self.paths[self._getPathIndex(param.parent())]
        path.is_area = value
    
    
    def _addOrStopFreehand(self, param, forceStop=False):
        self.curIndex = self._getPathIndex(param.parent())
        if not forceStop and param.name() == 'Add':
            param.setName('Done Add')
            self.pNew.hide()
            self._initFreehand()
        else:
            param.setName('Add')
            self.pNew.show()
            self._endFreehand()


    def _endFreehand(self):
        w = self.display.widget
        p = self.paths[self.curIndex]
        p.closePath()
        w.view.vb.mouseDragEvent = self._mouseDragEvent


    def _drawFreehand(self, ev, axis=None):
        ev.accept()
        
        ## Scale or translate based on mouse button
        if ev.button() & QtCore.Qt.MidButton:
            return self._mouseDragEvent(ev, axis)
        if ev.button() & QtCore.Qt.LeftButton:
            pos = self.mouseCoord(ev)
            p = self.paths[self.curIndex]

            if self._timer.elapsed() > self.MIN_DT:
                self._timer.restart()

                if ev.isStart():
                    p.startPath(pos)
                    #when viewbox view changed before (mouse drag)
                    #path wont be visible -> force update:
                    self.display.widget.view.vb.update()
                else:
                    p.continuePath(pos)


    def _removePath(self, parent, child, index):
        w = self.display.widget
        path =  self.paths.pop(index-3)
        if isinstance(path, _IsoCurve):
            try:            
                w.ui.histogram.vb.removeItem(path.isoLine)
            except ValueError:
                #TODO:
                pass #this method is called twice for some reason
        try:
            path.close()
        except AttributeError:
            w.view.vb.removeItem(path)


    def activate(self):
        for c in self.paths:
            c.show()


    def deactivate(self):
        for c in self.paths:
            c.hide()
        try:
            #reset draw event // in case freehand tool still activated
            self.display.widget.view.vb.mouseDragEvent = self._mouseDragEvent
        except AttributeError:
            pass



    def _savePaths(self):
        l = []
        for p, path in zip(self.pa.childs[4:], self.paths):
            name = p.name()
            state = path.saveState()
            typ = {FreehandItem:'Freehand', 
                   _Rect:'Rectangle', 
                   GridROI:'Grid', 
                   _IsoCurve:'Isolines',
                   _Ellipse:'Ellipse'
                   }[path.__class__]
            state['pen'] = p.param('Line color').value().getRgb()
            state['brush'] = p.param('Fill color').value().getRgb()
            l.append((typ,name,state))
        return l


    def saveState(self, state={}):
        state['activated'] = self.isChecked()
        state['paths'] = self._savePaths()
        return state


    def restoreState(self, state):
        for typ,name,s in state['paths']:
            s['pen'] = mkPen(state['pen'])
            s['brush'] = mkBrush(state['brush'])
            self._add(typ, name, s)   
        self.setChecked(state['activated'])



#     def save(self, session, path):
#         l = {}
#         l['activated'] = self.isChecked()
#         l['paths'] = self._savePaths()
#         session.addContentToSave(l, *path+('general.txt',))
# 
# 
#     def restore(self, session, path):
#         l =  eval(session.getSavedContent(*path +('general.txt',) ))
#         for typ,name,state in l['paths']:
#             state['pen'] = mkPen(state['pen'])
#             state['brush'] = mkBrush(state['brush'])
#             self._add(typ, name, state)   
#         self.setChecked(l['activated'])


    def _createMaskFromSelection(self):
        img = self.display.widget.image
        assert img is not None, 'need image defined'

        out = np.zeros(img.shape[1:3], dtype=np.uint8)
        for n, p in enumerate(self.paths):
            assert isinstance(p,FreehandItem), 'TODO: make work for other items as well'
            cv2.fillPoly(out, np.array([p.elements()],dtype=np.int32), n+1)
   
        self.handleOutput([out.T], title='selection')


    def _measurePath(self):
        mask = None
        v = self.pMask.value()
        if v != '-':
            for i, ch in enumerate(self.pa.childs[3:]):
                if ch.name() == v:
                    break
            mask = self.paths[i].painterPath()
        #TODO: mean + ...
            #mask area:
            ma = mask.calcArea()

        for n, p in enumerate(self.paths):
            a = p.painterPath()
            name = self.pa.childs[n+3].name()
            if mask is None or i == n:
                print '%s. %s - Area:%s | Length: %s' %(
                        n+1, name, a.calcArea(), a.length())
            else:
                ia = QPainterPath(mask.intersected(a)).calcArea()
                print '%s. %s - Area:(%s, area intersection: %s, relative %s) | Length:%s' %(
                        n+1, name, a.calcArea(), ia, ia/ma, a.length())


    def _addIso(self, p, state):
        w = self.display.widget
        
        pGauss = p.addChild({
            'name': 'Smooth kernel size',
            'type': 'float',
            'value':0}) 

        hist = w.ui.histogram
        mn,mx = hist.getLevels()
        lev = (mn+mx)/2
 
        # Isocurve drawing
        iso = _IsoCurve(level=lev,**state)

        iso.setParentItem(w.imageItem)
        iso.setZValue(5)#todo
        # build isocurves from smoothed data
        #connect
        pGauss.sigValueChanged.connect(self._isolinePGaussChanged)
        fn = lambda v=pGauss.value(), p=pGauss: self._isolinePGaussChanged(p, v)
        w.imageItem.sigImageChanged.connect(fn)
        w.sigTimeChanged.connect(fn)
        
        # Draggable line for setting isocurve level
        isoLine = pg.InfiniteLine(angle=0, movable=True, pen=state['pen'])
        iso.isoLine = isoLine
        hist.vb.addItem(isoLine)
        isoLine.setValue(lev)
        isoLine.setZValue(1000) # bring iso line above contrast controls
        #connect
        fn2 = lambda isoLine, iso=iso: iso.setLevel(isoLine.value()) 
        isoLine.sigDragged.connect(fn2)
        p.opts['iso'] = iso
        fn()
        return iso


    def _isolinePGaussChanged(self, p, v):
        w = self.display.widget
        if v > 0:
            d = pg.gaussianFilter(w.image[w.currentIndex], (v, v))
        else:
            d = w.image[w.currentIndex]
        p.parent().opts['iso'].setData(d)


    def _addROI(self, cls, param, state):
        w = self.display.widget
        r = w.view.vb.viewRange()  
        if not 'pos' in state:
            state['pos'] = ((r[0][0]+r[0][1])/2, (r[1][0]+r[1][1])/2)
            state['size'] = [(r[0][1]-r[0][0])*0.2, (r[1][1]-r[1][0])*0.2]
            state['angle'] = 0.0
        path = cls(**state)
        w.view.vb.addItem(path)    
        return path


    def _addFreehand(self, param, state):
        w = self.display.widget
        path = FreehandItem(w.imageItem, **state)

        pAdd = param.addChild({
            'name': 'Done Add',
            'type': 'action',
            }) 
        pMod = param.addChild({
            'name': 'Modify',
            'type': 'action'})

        pArea = param.addChild({
            'name': 'Is area',
            'type': 'bool',
            'value':True})
        
        pAdd.sigActivated.connect(self._addOrStopFreehand)
        pAdd.sigActivated.connect(self._menu.hide)
        
        pMod.sigActivated.connect(self._modifyFreehand)
        pMod.sigActivated.connect(self._menu.hide)
        
        pArea.sigValueChanged.connect(self._setFreehandIsArea)
        
        self.pNew.hide()
        
        print('''Press the left mouse button to draw.
Change the view using the middle mouse button
Click on 'Done Add' to stop drawing
''')
        return path


    def _addGrid(self, param, state):
        w = self.display.widget
        
        if 'size' not in state:
            state['size'] = w.image.shape[1:3]
        if 'pos' not in state:
            state['pos'] =[0, 0]
        
        path = GridROI(**state)
        
        path.setViewBox(w.view.vb)
        #TODO:
#         pFit = param.addChild({
#             'name': 'Fit shape to image',
#             'type': 'action',
#             'tip': 'Not implemented at the moment'
#             }) 
        #pFit.sigActivated.connect(lambda: raise NotImplemented('shape fitting is not implemented at the moment')

        pCells = param.addChild({
            'name':'Cells',
            'type':'empty',
            'isGroup':True})
         
        pX = pCells.addChild({
            'name':'x',
            'type':'int',
            'value':4,
            'limits':[1,1000]})
 
        pY = pCells.addChild({
            'name':'y',
            'type':'int',
            'value':5,
            'limits':[1,1000]})
         
        pShape = param.addChild({
            'name':'Shape',
            'type':'list',
            'value':'rect',
            'limits':['Rect','Circle', 'Pseudosquare']}) 
 
        pRatio = pShape.addChild({
            'name':'Ratio Circle/Square',
            'type':'float',
            'value':1.2,
            'limits':[1,1.41],
            'visible':False})  
    
        pShape.sigValueChanged.connect(lambda param, val:
                        pRatio.show(val=='Pseudosquare') )  
        pX.sigValueChanged.connect(lambda p,v, grid=path, py=pY: 
                        grid.setGrid(v, py.value()))          
        pY.sigValueChanged.connect(lambda p,v, grid=path, px=pX: 
                        grid.setGrid(px.value(),v)) 
        pShape.sigValueChanged.connect(lambda p,v, grid=path: 
                        grid.setCellShape(v)) 
        pRatio.sigValueChanged.connect(lambda p,v, grid=path: 
                        [c.setRatioEllispeRect(v) for c in grid.cells])
        return path



class _Rect(pg.ROI):
    def __init__(self, *args, **kwargs):
        if 'brush' in kwargs:
            self.brush = kwargs.pop('brush')
        pg.ROI.__init__(self, *args, **kwargs)
        self.addScaleHandle([1, 1], [0,0])


    def painterPath(self):
        p = self.state['pos']
        s = self.state['size']
        path = QPainterPath()
        path.addRect(QtCore.QRectF(p[0], p[1], s[0], s[1]))
        return path
    
    def setBrush(self, brush):
        self.brush = brush
        self.update()

    def paint(self, p, opt, widget):
        if self.brush:
            p.setBrush(self.brush)
        return pg.ROI.paint(self, p, opt, widget) 



class _Ellipse(pg.EllipseROI):
    def __init__(self, *args, **kwargs):
        if 'brush' in kwargs:
            self.brush = kwargs.pop('brush')
        pg.EllipseROI.__init__(self, *args, **kwargs)
        
        
    def painterPath(self):
        p = self.state['pos']
        s = self.state['size']
        path = QPainterPath()
        path.addEllipse(QtCore.QRectF(p[0], p[1], s[0], s[1]))
        return path
    
    
    def setBrush(self, brush):
        self.brush = brush
        self.update()


    def paint(self, p, opt, widget):
        if self.brush:
            p.setBrush(self.brush)
        return pg.EllipseROI.paint(self, p, opt, widget) 



class _IsoCurve(pg.IsocurveItem):
    
    def __init__(self, *args, **kwargs):
        self.brush = kwargs.pop('brush', None)
        elements = None
        if 'elements' in kwargs:
            elements = kwargs.pop('elements')
        
        pg.IsocurveItem.__init__(self, *args, **kwargs)
        
        self.setElements(elements)


    def setData(self, data, level=None):
        if data is not None:
            if data.ndim > 2:
                raise Exception('cannot create iso lines on color image at the moment')
            pg.IsocurveItem.setData(self, data, level)


    def setElements(self, elem):
        self.path = QPainterPath()
        if elem:
            self.path.moveTo(*elem[0])
            for e in elem[1:]:
                self.path.lineTo(*e)
            self.update()


    def elements(self):
        elem = []
        for i in range(self.path.elementCount()-1):
            e = self.path.elementAt(i)
            elem.append((e.x,e.y))
        return elem
 
 
    def painterPath(self):
        return QPainterPath(self.path)


    def paint(self, p, *args):
        if self.data is None:
            return
        if self.path is None:
            self.generatePath()
        p.setPen(self.pen)
        if self.brush:
            p.setBrush(self.brush)
        p.drawPath(self.path)


    def saveState(self):
        return {'elements': self.elements()}