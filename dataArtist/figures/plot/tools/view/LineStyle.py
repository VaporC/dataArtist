import pyqtgraph_karl as pg
from pyqtgraph_karl.Qt import QtGui, QtCore

from dataArtist.widgets.Tool import Tool



STYLE2ENUM = {'SolidLine':QtCore.Qt.SolidLine,
         'DashLine': QtCore.Qt.DashLine,
         'DotLine': QtCore.Qt.DotLine,
         'DashDotLine': QtCore.Qt.DashDotLine,
         'DashDotDotLine': QtCore.Qt.DashDotDotLine,
         #'CustomDashLine': QtCore.Qt.CustomDashLine,
         }
ENUM2STYLE = {}
for key, val in STYLE2ENUM.iteritems():
    ENUM2STYLE[val] = key



class LineStyle(Tool):
    '''
    change the graphs line style
    '''
    icon = 'lineStyle.svg'
    
    def __init__(self, plotDisplay):
        Tool.__init__(self, plotDisplay)

        pa = self.setParameterMenu() 

        self._menu.aboutToShow.connect(self._updateMenu)
        #self._menu.aboutToHide.connect(self.clear)

        p = pa.addChild({
                'name':'[All]',
                'type':'list',
                'value': 'SolidLine',
                'limits':ENUM2STYLE.values()}) 
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
                    'type':'list',
                    'autoIncrementName':True,
                    #set current color as first option:
                    'value': ENUM2STYLE[pen.style()],
                    'limits':ENUM2STYLE.values()}) 
            #SET COLOR:
            p.sigValueChanged.connect(
                lambda param, val, item=item, pen=pen: 
                [pen.setStyle(STYLE2ENUM[val]), item.setPen(pen)])