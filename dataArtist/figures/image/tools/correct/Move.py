import numpy as np
from pyqtgraph_karl import JoystickButton

#OWN
from dataArtist.widgets.Tool import Tool



class Move(Tool):
    '''
    Move current image in x,y direction
    '''
    icon = 'move.svg'
    
    def __init__(self, display):
        Tool.__init__(self, display)

        self._lastVal = [0,0]

        pa = self.setParameterMenu() 

        joy = JoystickButton()
        joy.sigStateChanged.connect(self._joystickChanged)
        self._menu.content.layout().insertWidget(1,joy)

        self.pX = pa.addChild({
            'name': 'X',
            'type': 'int',
            'value':0,}) 
        self._pxChanged = lambda param, val, axis=0: self.pXYChanged(val, axis)
        self.pX.sigValueChanged.connect(self._pxChanged)

        self.pY = pa.addChild({
            'name': 'Y',
            'type': 'int',
            'value':0,}) 
        self._pyChanged = lambda param, val, axis=1: self.pXYChanged(val, axis)
        self.pY.sigValueChanged.connect(self._pyChanged)
        
        pAccept = pa.addChild({
            'name': 'Accept',
            'type': 'action'}) 
        pAccept.sigActivated.connect(self.acceptChanges)
        
        pReset = pa.addChild({
            'name': 'Reset',
            'type': 'action'})
        pReset.sigActivated.connect(self.resetChanges)
        

    def _joystickChanged(self, joystick, xy):
        self.pX.setValue(self.pX.value() + int(xy[0]*10))
        self.pY.setValue(self.pY.value() + int(xy[1]*10))
 

    def pXYChanged(self, value, axis):
        w = self.display.widget
        c = w.currentIndex
        im = w.image
        stack=False
        if im.ndim == 3:
            stack=True
            im = im[c]
        #MOve:
        im = np.roll(im, value-self._lastVal[axis], axis)
        if stack:
            w.image[c] = im
        else:
            w.image = im
        w.imageItem.updateImage(im)
        self._lastVal[axis] = value
       
       

    def acceptChanges(self):
        self.pX.setValue(0, blockSignal=self._pxChanged)
        self.pY.setValue(0, blockSignal=self._pyChanged)
        self._lastVal = [0,0]


    def resetChanges(self):
        self.pX.setValue(0)
        self.pY.setValue(0)