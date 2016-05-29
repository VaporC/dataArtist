'''
This module is still in development
... sometimes in the future it will give
a base class for all 3d display widgets
... or alternatively use something provided by pyqtgraph
'''

import pyqtgraph_karl.opengl as gl
import pyqtgraph_karl as pg
from pyqtgraph_karl import QtGui, QtCore

class Grid(object):
    def __init__(self, parent):
        fc = pg.getConfigOption('foreground')
        self.x = gl.GLGridItem(color=fc)
        self.x.rotate(90, 0, 1, 0)
        self.x.translate(-10, 0, 0)
        parent.addItem(self.x)
        #y
        self.y = gl.GLGridItem(color=fc)
        self.y.rotate(90, 1, 0, 0)
        self.y.translate(0, -10, 0)
        parent.addItem(self.y)
        #z
        self.z = gl.GLGridItem(color=fc)
        self.z.translate(0, 0, -10)
        parent.addItem(self.z)

    def show(self):
        for plane in (self.x, self.y, self.z):
            plane.show()      

    def hide(self):
        for plane in (self.x, self.y, self.z):
            plane.hide() 







class View3d(gl.GLViewWidget):
    def __init__(self):
        gl.GLViewWidget.__init__(self)
        self.setBackgroundColor(pg.getConfigOption('background'))
        self.setCameraPosition(distance=40)
        self.grid = Grid(self)
        
        

if __name__ == '__main__':
    app = QtGui.QApplication([])
    w = View3d()
    w.show()
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()