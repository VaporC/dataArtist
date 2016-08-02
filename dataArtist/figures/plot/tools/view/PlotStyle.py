import pyqtgraph_karl as pg
from pyqtgraph_karl.Qt import QtGui, QtCore

from dataArtist.widgets.Tool import Tool

PLOT_SYMBOLS = {'None': None,
                'Disk': 'o', 
                'Square': 's', 
                'Triangle': 't', 
                'Diamond': 'd', 
                '+': '+', 
                'Cross': 'x'}


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



class PlotStyle(Tool):
    '''
    change the graphs line style
    '''
    icon = 'plotStyle.svg'
    
    def __init__(self, plotDisplay):
        Tool.__init__(self, plotDisplay)

        pa = self.setParameterMenu() 

        self._menu.aboutToShow.connect(self._updateMenu)
        #self._menu.aboutToHide.connect(self.clear)

        pAll = pa.addChild({
                'name':'[All]',
                'type':'empty',
                'expanded': False})

        #LINE
        pLine = pAll.addChild({
                'name':'Line',
                'type':'empty'}) 

        p = pLine.addChild({
                'name':'Style',
                'index':(0,0),
                'type':'list',
                'value': 'SolidLine',
                'limits':ENUM2STYLE.values()}) 
        p.sigValueChanged.connect(self._pAllChanged)

        p = pLine.addChild({
                'name':'Width',
                'index':(0,1),
                'type':'int',
                'value': 1}) 
        p.sigValueChanged.connect(self._pAllChanged)

        p = pLine.addChild({
                'name':'Color',
                'type':'color',
                'value':pg.mkColor('r'),
                'index':(0,2),
                }) 
        p.sigValueChanged.connect(self._pAllChanged)

        p = p.addChild({
                'name':'Rainbow',
                'type':'action'}) 
        p.sigActivated.connect(self._setLineRainbowColors)

        pSymbol = pAll.addChild({
                'name':'Symbol',
                'type':'empty'}) 

            #SYMBOL TYPE
        p = pSymbol.addChild({
                'name':'Type',
                'type':'list',
                'limits':PLOT_SYMBOLS.keys(),
                'value':PLOT_SYMBOLS.keys()[0],
                'index':(1,0)}) 
        p.sigValueChanged.connect(self._pAllChanged)


        p = pSymbol.addChild({
                'name':'Color',
                'index':(1,1),
                'type':'color',
                'value': pg.mkColor('r')}) 
        p.sigValueChanged.connect(self._pAllChanged)

        p = p.addChild({
                'name':'Rainbow',
                'type':'action'}) 
        p.sigActivated.connect(self._setSymbolRainbowColors)


    def _setLineRainbowColors(self):
        curves = self.display.widget.curves
        for n,c in enumerate(curves):
            pen = c.opts['pen']
            if isinstance(pen, QtGui.QPen):
                pen.setColor( pg.mkColor( (n,len(curves)+1) ) )
            else:
                pen = pg.mkPen(n,len(curves)+1)
            c.setPen(pen)


    def _setSymbolRainbowColors(self):
        curves = self.display.widget.curves
        for n,c in enumerate(curves):
            c.setSymbolBrush((n,len(curves)+1))


    def _pAllChanged(self, param, val):
        i,j = param.opts['index']
        for ch in self._menu.p.childs[1:]:
            ch.childs[i].childs[j].setValue(val)

 
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
            
            pPlot = self._menu.p.addChild({
                'name':name,
                'type':'empty',
                'autoIncrementName':True,
                'expanded':False}) 
            #LINE
            pLine = pPlot.addChild({
                'name':'Line',
                'type':'empty'}) 

            #LINE STYLE                 
            pen = item.opts['pen']
            if not isinstance(pen, QtGui.QPen):
                pen = pg.mkPen(pen)
            p = pLine.addChild({
                    'name':'Style',
                    'type':'list',
                    #set current color as first option:
                    'value': ENUM2STYLE[pen.style()],
                    'limits':ENUM2STYLE.values(),
                    'itemPen':(item,pen)}) 
            p.sigValueChanged.connect(self._setLineStyle)
            
            #LINE WIDTH
            p = pLine.addChild({
                    'name':'Width',
                    'type':'int',
                    #set current color as first option:
                    'value':pen.width(),
                    'itemPen':(item,pen)}) 
            p.sigValueChanged.connect(self._setLineWidth)

            color = pen
            if isinstance(color, QtGui.QPen):
                color = color.color()
            
            #LINE COLOR
            p = pLine.addChild({
                    'name':'Color',
                    'type':'color',
                    #set current color as first option:
                    'value':color,
                    'itemPen':(item,pen)}) 
            p.sigValueChanged.connect(self._setLineColor)

            #Symbol
            pSymbol = pPlot.addChild({
                'name':'Symbol',
                'type':'empty'}) 

            #SYMBOL COLOR
            brush = item.opts['symbolBrush']
            if isinstance(brush, QtGui.QBrush):
                color = brush.color()
            else:
                color = brush
                
            #SYMBOL TYPE
            p = pSymbol.addChild({
                    'name':'Type',
                    'type':'list',
                    'limits':PLOT_SYMBOLS.keys(),
                    'item':item,
                    #set current symbol as first option:
                    'value':item.opts['symbol']}) 
            p.sigValueChanged.connect(self._setSymbolType)

            #SYMBOL COLOR
            p = pSymbol.addChild({
                    'name':'Color',
                    'type':'color',
                    'autoIncrementName':True,
                    #set current colour as first option:
                    'value':color,
                    'item':item}) 
            p.sigValueChanged.connect(self._setSymbolColor)


    def _setLineColor(self, param, val):
        item, pen = param.opts['itemPen']
        pen.setColor(val)
        item.setPen(pen)


    def _setSymbolType(self, param, val):
        c =  param.opts['item']
        c.setSymbol(PLOT_SYMBOLS[val])


    def _setLineStyle(self, param, val):
        item, pen = param.opts['itemPen']
        pen.setStyle(STYLE2ENUM[val])
        item.setPen(pen)


    def _setLineWidth(self, param, val):
        item, pen = param.opts['itemPen']
        pen.setWidth(val)
        item.setPen(pen)


    def _setSymbolColor(self, param, val):
        c = param.opts['item']
        c.setSymbolBrush(val)