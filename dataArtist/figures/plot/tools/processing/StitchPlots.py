from pyqtgraph_karl.Qt import QtGui
import numpy as np

from dataArtist.widgets.Tool import Tool



class StitchPlots(Tool):
    '''
    Stitch 2 plots together
    '''
    icon = 'stitchPlots.svg'
    
    def __init__(self, plotDisplay):
        Tool.__init__(self, plotDisplay)

        self.mDisplay = QtGui.QMenu('from display')
        self.setMenu(self.mDisplay)
        self.mDisplay.aboutToShow.connect(self._buildMenu)


    def _buildMenu(self):
        self.mDisplay.clear()
        for d in self.display.workspace.displays():
            if d != self.display and d.widget.__class__ == self.display.widget.__class__:
                a = self.mDisplay.addAction(d.name())
                a.triggered.connect(
                    lambda checked, d=d: 
                        self.activate(d) )


    def activate(self, display=None):
        if display is None:
            return
        for curve,foreignCurve in zip(self.display.widget.curves, 
                                      display.widget.curves):
            x,y = curve.xData, curve.yData
            x = np.append(x,foreignCurve.xData)
            y = np.append(y,foreignCurve.yData)
            curve.setData(x,y)         
        self.setChecked(True)        