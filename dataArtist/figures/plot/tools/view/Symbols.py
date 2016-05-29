from dataArtist.widgets.Tool import Tool


PLOT_SYMBOLS = ['None','o', 's', 't', 'd', '+', 'x']


class Symbols(Tool):
    '''
    change the graphs symbol
    '''
    icon = 'symbol.svg'
    
    def __init__(self, plotDisplay):
        Tool.__init__(self, plotDisplay)

        self.setParameterMenu() 
        self._menu.aboutToShow.connect(self._updateMenu)

 
    def clear(self):
        self._menu.p.clearChildren()   
        #self._menu.aboutToHide.connect(lambda: self._menu.p.clearChildren())


    def _updateMenu(self):
        '''
        add a parameter to change the graphs symbol for each layer
        '''
        
        self.clear()
        curves = self.display.widget.curves

        for n,c in enumerate(curves):
            name = c.label.text
            if not name:
                name = 'Plot %s' %str(n+1)
            p = self._menu.p.addChild({
                    'name':name,
                    'type':'list',
                    'limits':PLOT_SYMBOLS,
                    'autoIncrementName':True,
                    #set current symbol as first option:
                    'value':c.opts['symbol']}) 
            #SET SYMBOL:
            p.sigValueChanged.connect(
                lambda param, val, c=c: 
                c.setSymbol(val) if val != 'None' else c.setSymbol(None))