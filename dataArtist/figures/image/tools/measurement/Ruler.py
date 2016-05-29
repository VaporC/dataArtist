import numpy as np
import pyqtgraph_karl as pg
from pyqtgraph_karl.Qt import QtGui, QtCore

#OWN
from dataArtist.widgets.Tool import Tool

 

class Ruler(Tool):
    '''
    Measure the length of a given distance
    Left-click to mark the start and end point
    
    Optional: Scale the image axes
    '''
    icon = 'ruler.svg'
    def __init__(self, display):
        Tool.__init__(self, display)

        self.scene = self.display.widget.view.scene()
        self.rulers = []
        self.rulersLen = []
        self.scale = 1
        self.scaleEditor = _ScaleEditor(self)
        
        p = self.setParameterMenu()

        pShow = p.addChild({
            'name': 'Show',
            'type': 'bool',
            'value':True}) 
        pShow.sigValueChanged.connect(self.toggleShow)

        self.pAngle = p.addChild({
            'name': 'Show angle',
            'type': 'bool',
            'value':False}) 

        self.pColor = p.addChild({
            'name': 'Color',
            'type': 'color',
            'value': (255, 0, 0, 130)})

        self.pSetScale = p.addChild({
            'name': 'Set Scale',
            'type': 'bool',
            'value':False})
        
        self.pRatio = self.pSetScale.addChild({
            'name': 'Aspect Ratio = 1',
            'type': 'bool',
            'value':True,
            'visible':False}) 
        
        self.pSetScale.sigValueChanged.connect(lambda param, val:
                    [ch.show(val) for ch in param.children()])

        pReset = p.addChild({
            'name': 'reset',
            'type': 'action',
            'value':True}) 
        pReset.sigActivated.connect(self.reset)


    def activate(self):
        self.scene.sigMouseClicked.connect(self._startruler)


    def deactivate(self):
        try: #case init ruler 
            self.scene.sigMouseClicked.disconnect(self._startruler)

        except TypeError: #case ruler moving
            self.scene.sigMouseMoved.disconnect(self._moveruler)
            self.scene.sigMouseClicked.disconnect(self._stopruler)
            item = self.rulersLen.pop(-1)
            self.view.removeItem(item)
            item = self.rulers.pop(-1)         
            self.view.removeItem(item)


    def toggleShow(self, param, value):
        if value:
            for r in self.rulers:
                r.show()
            for l in self.rulersLen:
                l.show()
        else: 
            for r in self.rulers:
                r.hide()
            for l in self.rulersLen:
                l.hide()        


    def reset(self):
        for l in self.rulers:
            self.view.removeItem(l)
        self.rulers = []
        for l in self.rulersLen:
            self.view.removeItem(l)
        self.rulersLen = []
        self.scale = 1
 
 
    def transpose(self):
        #TODO
        raise NotImplemented()


    def _startruler(self, evt):
        self.scene.sigMouseClicked.disconnect(self._startruler)

        self.rulers.append(pg.PlotDataItem(
                    symbol='+', 
                    pen=pg.mkPen(color=self.pColor.value(), width=2),
                    symbolSize=16,
                    symbolBrush=pg.mkBrush(self.pColor.value() )
                     ) )
        self.rulersLen.append(pg.TextItem(
                    text='', 
                    color=(0,0,0), 
                    html=None, 
                    anchor=(0, 0), 
                    border=None, 
                    fill=pg.mkBrush(self.pColor.value()), 
                    angle=0
                     ) )
        self.view.addItem(self.rulers[-1])
        self.view.addItem(self.rulersLen[-1])

        self.rulersStartX,self.rulersStartY = self.mouseCoord(evt)
        self.rulersLen[-1].setPos(self.rulersStartX,self.rulersStartY)
        self.scene.sigMouseMoved.connect(self._moveruler)
        self.scene.sigMouseClicked.connect(self._stopruler)


    def _moveruler(self, evt):
        x,y = self.mouseCoord(evt)
        txtPosX = (self.rulersStartX+x)*0.5
        txtPosY = (self.rulersStartY+y)*0.5
        dx = x-self.rulersStartX
        dy = y-self.rulersStartY
        lenruler =  (dx**2 + dy**2)**0.5
        lenruler *= self.scale
        self.rulersLen[-1].setPos(txtPosX,txtPosY)
        if lenruler >1:
            txt = '%.3f' %lenruler
        else:
            txt = '%s' %lenruler
        if self.pAngle.value():
            txt += ';  angle=%.2f DEG' %np.degrees(np.arctan2(-dy,dx))
        self.rulersLen[-1].setText(txt)
        self.rulers[-1].setData(
            (self.rulersStartX,x),
            (self.rulersStartY,y))


    def _stopruler(self, evt):
        self.scene.sigMouseMoved.disconnect(self._moveruler)
        self.scene.sigMouseClicked.disconnect(self._stopruler)
        self.scene.sigMouseClicked.connect(self._startruler)

        if self.pSetScale.value():
            x  = self.rulers[-1].xData
            y = self.rulers[-1].yData
            dx = np.diff(x)[0]
            dy = np.diff(y)[0]
            self.scaleEditor.activate(dx, dy, self.pRatio.value(), self.rulersLen[-1])
            self.deactivate()
            self.setChecked(False)



class _ScaleEditor(QtGui.QWidget):
    '''
    Editor to define measured length and concerning axis
    '''
    def __init__(self, tool):
        QtGui.QWidget.__init__(self)
        self.tool = tool
        self.display = tool.display

        l = QtGui.QHBoxLayout()
        self.setLayout(l)
        
        d = QtGui.QLabel('Set distance in')
        self.combo = QtGui.QComboBox()
        self.combo.addItems(['x','y', 'distance'])
        self.editor = QtGui.QLineEdit()
        self.editor.setValidator(QtGui.QDoubleValidator(0.0, 9999.0, 3))
        l.addWidget(d)        
        l.addWidget(self.combo)
        l.addWidget(self.editor)
        
        self.setGeometry(100,100,200,40)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.lightGray)
        self.setPalette(p)
            
        self.hide()


    def activate(self, dx, dy, equalAspectRatio, textItem):
        self.dx = dx
        self.dy = dy
        self.equalAspectRatio = equalAspectRatio
        self.textItem = textItem
        #TODO: move to right position:
        self.show()
        self.editor.editingFinished.connect(self.setScale)
        
        
    def setScale(self):
        if self.combo.currentText() == 'x':
            a = self.display.axes[0]
            a2 = self.display.axes[1]
            l1 = abs(self.dx)

        elif self.combo.currentText() == 'y':
            a = self.display.axes[1]
            a2 = self.display.axes[0]
            l1 = abs(self.dy)
        else:
            a = self.display.axes[1]
            a2 = self.display.axes[0]
            l1 = ( self.dx**2 + self.dy**2 ) **0.5
        
        l2 =  float(self.editor.text())
        
        scale = l2 / l1
        self.tool.scale = scale
        self.textItem.setText('~ %s (scale:%s)' %(l2, scale))

        a.pScale.setValue(scale)
        if self.equalAspectRatio:
            a2.pScale.setValue(scale)
            
        self.tool.pSetScale.setValue(False)
        self.hide()