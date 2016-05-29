from pyqtgraph_karl.functions import mkPen
from pyqtgraph_karl.Qt import QtCore, QtGui

#OWN
from dataArtist.widgets.Tool import Tool
from dataArtist.items.FreehandItem import FreehandItem



class Freehand(Tool):

    icon = 'freehand.svg'
    
    def __init__(self, display):
        Tool.__init__(self, display)

        self.paths = []
        #min time difference to add a line to qpainterpath 
        #when drawing in [ms]:
        self.MIN_DT = 25 
        self._timer = QtCore.QTime()

        self.pa = self.setParameterMenu()
        self.pa.sigChildRemoved.connect(self._removePath)

        pNew = self.pa.addChild({
            'name': 'New',
            'type': 'action',
            'value':True}) 
        pNew.sigActivated.connect(self._newCurve)
        pNew.sigActivated.connect(self._menu.hide)


    def _newCurve(self):
        w = self.display.widget
       
        pen = mkPen(10, len(self.paths)+2)

        self.curIndex = -1
        
        p = self.pa.addChild({
            'name': str(len(self.paths)+1),
            'type': 'empty',
            'isGroup':True,
            'removable':True,
            'renamable':True,
            'autoIncrementName':True
            }) 

        path = FreehandItem(w.imageItem, pen)

        pAdd = p.addChild({
            'name': 'Add',
            'type': 'action',
            }) 
        pAdd.sigActivated.connect(self._appendToPath)
        pAdd.sigActivated.connect(self._menu.hide)

        pMod = p.addChild({
            'name': 'Modify',
            'type': 'action'}) 
        pMod.sigActivated.connect(self._modifyPath)
        pMod.sigActivated.connect(self._menu.hide)
        
        self._initDraw()

        self.paths.append(path)

        color = pen.color()
        pLineColor = p.addChild({
            'name':'Line color',
            'type':'color',
            'value':color,
            'path':path}) 
        pLineColor.sigValueChanged.connect(self._changeLineColor)

        br = QtGui.QColor(color)
        br.setAlpha(0)
        path.setBrush(br)
        
        pFillColor = p.addChild({
            'name':'Fill color',
            'type':'color',
            'value':br,
            'path':path}) 
        pFillColor.sigValueChanged.connect(self._changeFillColor)

        self.setChecked(True)
        

    def _initDraw(self):
        w = self.display.widget
        self._mouseDragEvent = w.view.vb.mouseDragEvent
        w.view.vb.mouseDragEvent = self._draw
        self._timer.start()


    def _changeLineColor(self, param, val):
        c = param.opts['path']
        c.setPen(val)


    def _changeFillColor(self, param, val):
        c = param.opts['path']
        c.setBrush(val)


    def _modifyPath(self, param):
        path = self.paths[self._getPathIndex(param.parent())]
        if path.isModify:
            param.setName('Modify')
            path.setModify(False)
        else:
            param.setName('Done Modify')
            path.setModify(True)


    def _getPathIndex(self, param):
        i = param.parent().childs.index(param)
        return i-1
    
    
    def _appendToPath(self, param):
        self.curIndex = self._getPathIndex(param.parent())
        self._initDraw()


    def _draw(self, ev, axis=None):
        ev.accept()
        
        ## Scale or translate based on mouse button
        if ev.button() & (QtCore.Qt.LeftButton | QtCore.Qt.MidButton):
            pos = self.mouseCoord(ev)
            p = self.paths[self.curIndex]
            w = self.display.widget
            
            if ev.isFinish():  ## This is the final move in the drag; change the view scale now
                #p.closePath()
                w.view.vb.mouseDragEvent = self._mouseDragEvent
                #del self._mouseDragEvent
            else:
                if self._timer.elapsed() > self.MIN_DT:
                    self._timer.restart()

                    if ev.isStart():
                        p.startPath(pos)
                    else:
                        p.continuePath(pos)


    def _removePath(self, parent, child, index):
        path =  self.paths.pop(index-3)
        w = self.display.widget
        w.view.vb.removeItem(path)


    def activate(self):
        for c in self.paths:
            c.show()


    def deactivate(self):
        for c in self.paths:
            c.hide()