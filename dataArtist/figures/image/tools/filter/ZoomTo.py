import numpy as np
from pyqtgraph_karl.Qt import QtGui, QtCore

#OWN 
from dataArtist.widgets.Tool import Tool


class ZoomTo(Tool):
    '''
    Zoom to a certain area that fulfils a given criterion
    '''
    icon = 'find.svg'

    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)
        
        pa = self.setParameterMenu() 
        
        self.pSizeX = pa.addChild({
            'name': 'X-size',
            'type': 'int',
            'value':300,
            'limits':[1,1e6]}) 

        self.pSizeY = pa.addChild({
            'name': 'Y-size',
            'type': 'int',
            'value':300,
            'limits':[1,1e6]}) 
        
        self.pObject = pa.addChild({
            'name': 'Object',
            'type': 'list',
            'limits':['current image', 'current color layer']})        
                
        self.pCriterion =  pa.addChild({
            'name': 'Criterion',
            'type': 'list',
            'limits':['==', '>', '<']}) 
        
        self.pValue =  pa.addChild({
            'name': 'Value',
            'type': 'float',
            'value': 100}) 


    def activate(self):  
        obj = self.pObject.value()
        w = self.display.widget
        if obj == 'current image':
            img = w.image
            if img.ndim == 3:
                img = img[w.currentIndex]
        elif obj == 'current color layer':
            img = w.cItems.values()[0].image
        
        s = 'img %s %s' %(self.pCriterion.value(), self.pValue.value())
        indices = eval(s)
        self.positions = np.nonzero(indices)
        self.n = 0
                    
        self.control = _ControlWidget(self.previous, self.next)
        self.control.show()


    def previous(self):
        if self.n > 0:
            self.n -= 1
            self._goToPosition()


    def next(self):
        if self.n < len(self.positions[0]) -1:
            self.n += 1
            self._goToPosition()
        
            
    def _goToPosition(self):
        cx = self.positions[0][self.n]
        cy = self.positions[1][self.n]
        hx = self.pSizeX.value()
        hy = self.pSizeY.value()

        self.display.widget.view.vb.setRange(
                xRange=(cx-0.5*hx,cx+0.5*hx),
                yRange=(cy-0.5*hy,cy+0.5*hy)
                )


    def deactivate(self):
        self.control.close()



class _ControlWidget(QtGui.QWidget):
    '''
    A draggable control window with:
    * Button 'Previous'
    * Button 'Next'
    to be connected with the given functions
    '''
    def __init__(self, fnPrevious, fnNext):
        QtGui.QWidget.__init__(self)
        #make frameles:
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)

        btn_previous = QtGui.QPushButton('Previous')  
        btn_previous.clicked.connect(fnPrevious)   
        btn_next = QtGui.QPushButton('Next')
        btn_next.clicked.connect(fnNext)   

        layout.addWidget(btn_previous)
        layout.addWidget(btn_next)


    #make draggable:
    def mousePressEvent(self, event):
        self.offset = event.pos()
    
    
    def mouseMoveEvent(self, event):
        x = event.globalX()
        y = event.globalY()
        x_w = self.offset.x()
        y_w = self.offset.y()
        self.move(x-x_w, y-y_w)
