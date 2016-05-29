import pyqtgraph_karl as pg
from pyqtgraph_karl.Qt import QtGui

from dataArtist.widgets.Tool import Tool



class LineWidth(Tool):
    '''
    change the graphs line width
    '''
    icon = 'lineWidth.svg'
    
    def __init__(self, plotDisplay):
        Tool.__init__(self, plotDisplay)

        pa = self.setParameterMenu() 
        self._menu.aboutToShow.connect(self._updateMenu)

        p = pa.addChild({
                'name':'[All]',
                'type':'int',
                'value':1}) 
        p.sigValueChanged.connect(self._pAllChanged)


    def _pAllChanged(self, param, val):
        for ch in self._menu.p.childs[1:]:
            ch.setValue(val)

 
    def clear(self):
        for ch in self._menu.p.childs[1:]:
            self._menu.p.removeChild(ch)


    def _updateMenu(self):
        '''
        add a parameter to change the graphs symbol for each layer
        '''
        
        self.clear()
        curves = self.display.widget.curves

        for n,item in enumerate(curves):
            name = item.label.text
            if not name:
                name = 'Plot %s' %str(n+1)
            pen = item.opts['pen']
            if not isinstance(pen, QtGui.QPen):
                pen = pg.mkPen(pen)
            p = self._menu.p.addChild({
                    'name':name,
                    'type':'int',
                    'autoIncrementName':True,
                    #set current color as first option:
                    'value':pen.width()}) 
            #SET COLOR:
            p.sigValueChanged.connect(
                lambda param, val, item=item, pen=pen: 
                [pen.setWidth(val), item.setPen(pen)])