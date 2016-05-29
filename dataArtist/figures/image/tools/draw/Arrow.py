import pyqtgraph_karl as pg
from pyqtgraph_karl.Qt import QtCore
from pyqtgraph_karl import functions as fn

from math import atan2, degrees

from dataArtist.widgets.Tool import Tool


class Arrow(Tool):
    '''
    Draw arrows.
    Click on 'Add' and within the image two times to define the 
    arrow start and end
    '''
    icon = 'arrow.svg'
    
    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)

        self.arrows = []

        pa = self.setParameterMenu() 

        pAdd = pa.addChild({
            'name': 'Add',
            'type': 'action'}) 
        pAdd.sigActivated.connect(lambda:
              self.view.scene().sigMouseClicked.connect(self._arrowStart) )   
        pAdd.sigActivated.connect(self._menu.hide)  

        pClear = pa.addChild({
            'name': 'Clear',
            'type': 'action'}) 
        pClear.sigActivated.connect(self._clear)   

        pColor = pa.addChild({
            'name': 'Color',
            'type': 'empty',
            'igroup':True}) 

        self.pPen = pColor.addChild({
            'name': 'Pen',
            'type': 'color',
            'value':'r'}) 

        self.pPenWidth = self.pPen.addChild({
            'name': 'Width',
            'type': 'int',
            'value':2,
            'limits':[1,1e6]}) 
        
        fn = lambda p,v: self.arrows[-1].setStyle(
                        pen={'color': self.pPen.value(),
                            'width': self.pPenWidth.value()}
                        if self.arrows else False)
        self.pPen.sigValueChanged.connect(fn)
        self.pPenWidth.sigValueChanged.connect(fn)

        self.pBrush = pColor.addChild({
            'name': 'Brush',
            'type': 'color',
            'value':'r'}) 
        self.pBrush.sigValueChanged.connect(lambda p,v:
                self.arrows[-1].setStyle(brush=v) if self.arrows else False)

        self.pTailWidth = pa.addChild({
            'name': 'Width',
            'type':'int',
            'value':10,
            'limits':[1,100]}) 
        self.pTailWidth.sigValueChanged.connect(lambda p,v:
                self.arrows[-1].setStyle(tailWidth=v) if self.arrows else False)

        self.pHeadLen = pa.addChild({
            'name': 'Head length',
            'type':'int',
            'value':40,
            'limits':[1,100]}) 
        self.pHeadLen.sigValueChanged.connect(lambda p,v:
                self.arrows[-1].setStyle(headLen=v) if self.arrows else False)

        self.pTipAngle = pa.addChild({
            'name': 'Tip angle [DEG]',
            'type':'int',
            'value':60,
            'limits':[1,100]}) 
        self.pTipAngle.sigValueChanged.connect(lambda p,v:
                        self.arrows[-1].setStyle(tipAngle=v))


    def _clear(self):
        for a in self.arrows:
            self.view.removeItem(a)  
        self.arrows = []


    def activate(self):
        for a in self.arrows:
            a.show()


    def _arrowStart(self, evt):
        self.setChecked(True)
        
        a = pg.ArrowItem(angle=-160, 
                       tipAngle=60, 
                       headLen=self.pHeadLen.value(), 
                       tailLen=0, 
                       tailWidth=self.pTailWidth.value(), 
                       pen={'color': self.pPen.value(),
                            'width': self.pPenWidth.value()},
                       brush=self.pBrush.value() ,
                       pxMode=False
                         )
        
        self._startX,self._startY  = self.mouseCoord(evt)
        self.arrows.append(a)
        a.setPos(self._startX,self._startY)
        self.view.addItem(a)
        
        s = self.view.scene()
        s.sigMouseClicked.disconnect(self._arrowStart)
        s.sigMouseMoved.connect(self._arrowMove)        
        s.sigMouseClicked.connect(self._arrowStop)        


    def _arrowMove(self, evt):
        x,y = self.mouseCoord(evt)

        a = self.arrows[-1]
        
        dx = x-self._startX
        dy = y-self._startY
        
        l = (dx**2+dy**2)**0.5 - a.opts['headLen']
        if l < 0:
            l = 0
        angle = 180+degrees(atan2(dy,dx))
        
        a.opts.update({'tailLen':l,
                       'angle':angle
                      })
        opt = dict([(k,a.opts[k]) for k in ['headLen', 'tipAngle', 'baseAngle', 
                                            'tailLen', 'tailWidth']])
        a.path = fn.makeArrowPath(**opt)
        a.setPath(a.path)
        a.setRotation(a.opts['angle'])


    def _arrowStop(self, evt):
        self.view.scene().sigMouseMoved.disconnect(self._arrowMove)        
        self.view.scene().sigMouseClicked.disconnect(self._arrowStop) 
     
        
    def deactivate(self):
        for a in self.arrows:
            a.hide()



class _ArrowItem(pg.ArrowItem):
    def hoverEvent(self, ev):
        ev.acceptDrags(QtCore.Qt.LeftButton)
        
    def mouseDragEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            dpos = ev.pos() - ev.lastPos()
            self.autoAnchor(self.pos() + dpos)