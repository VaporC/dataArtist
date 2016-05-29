from pyqtgraph_karl.Qt import QtGui
from pyqtgraph_karl.functions import mkPen, mkColor

from dataArtist.widgets.Tool import Tool


class Colors(Tool):
    '''
    Change the graphs color.
    '''
    icon = 'colors.svg'
    
    def __init__(self, plotDisplay):
        Tool.__init__(self, plotDisplay)
        self.setParameterMenu() 
        self._menu.aboutToShow.connect(self._updateMenu)


    def _updateMenu(self):
        '''
        add a parameter to change the graphs symbol for each layer
        '''
        self._menu.p.clearChildren()
        p = self._menu.p.addChild({
            'name':'Rainbow',
            'type':'action'}) 
        p.sigActivated.connect(self._setRainbowColors)
        p.sigActivated.connect(self._menu.hide)

        for n,c in enumerate(self.display.widget.curves):
            name = c.label.text
            if not name:
                name = 'Plot %s' %str(n+1)
            color = c.opts['pen']
            if isinstance(color, QtGui.QPen):
                color = color.color()
            p = self._menu.p.addChild({
                    'name':name,
                    'type':'color',
                    'autoIncrementName':True,
                    #set current colour as first option:
                    'value':color,
                    'curve':c}) 
            p.sigValueChanged.connect(self._changeColor)


    def _changeColor(self, param, val):
        c = param.opts['curve']
        pen = c.opts['pen']
        if not isinstance(pen, QtGui.QPen):
            pen = QtGui.QPen()   
        pen.setColor(val)
        c.setPen(pen)

   
    def _setRainbowColors(self):
        curves = self.display.widget.curves
        for n,c in enumerate(curves):
            pen = c.opts['pen']
            if isinstance(pen, QtGui.QPen):
                pen.setColor( mkColor( (n,len(curves)+1) ) )
            else:
                pen = mkPen(n,len(curves)+1)
            c.setPen(pen)