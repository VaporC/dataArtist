from pyqtgraph_karl.Qt import QtGui

from dataArtist.widgets.Tool import Tool



class SymbolColor(Tool):
    '''
    change the graphs symbol color
    '''
    icon = 'symbolColor.svg'
    
    def __init__(self, plotDisplay):
        Tool.__init__(self, plotDisplay)
 
        self.setParameterMenu() 
        self._menu.aboutToShow.connect(self._updateMenu)
        #self._menu.aboutToHide.connect(self.clear)


    def clear(self):
        self._menu.p.clearChildren()


    def _updateMenu(self):
        '''
        add a parameter to change the graphs symbol for each layer
        '''
        curves = self.display.widget.curves
        
        self.clear()
        p = self._menu.p.addChild({
            'name':'Rainbow',
            'type':'action'}) 
        p.sigActivated.connect(self._setRainbowColors)
        
        for n,c in enumerate(curves):
            name = c.label.text
            if not name:
                name = 'Plot %s' %str(n+1)
            brush = c.opts['symbolBrush']
            if isinstance(brush, QtGui.QBrush):
                color = brush.color()
            else:
                color = brush
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
        c.setSymbolBrush(val)

   
    def _setRainbowColors(self):
        curves = self.display.widget.curves
        for n,c in enumerate(curves):
            c.setSymbolBrush((n,len(curves)+1))