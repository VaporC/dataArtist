from dataArtist.widgets.Tool import Tool



class Legend(Tool):
    '''
    show/hide the legend or its frame
    '''
    icon = 'legend.svg'
    
    def __init__(self, plotDisplay):
        Tool.__init__(self, plotDisplay)

        pa = self.setParameterMenu() 

        pFrame = pa.addChild({
            'name':'Show frame',
            'type':'bool',
            'value':True})
        pFrame.sigValueChanged.connect(self._drawFrame) 
        
        pOrientation = pa.addChild({
            'name':'N Columns',
            'type':'int',
            'value':1})
        pOrientation.sigValueChanged.connect(lambda param, value: 
                    self.display.widget.view.legend.setColumnCount(value)) 

        self.setChecked(True)
        
        
    def _drawFrame(self, param, show):
        l = self.display.widget.view.legend
        l.drawFrame = show
        l.update()


    def activate(self):
        self.display.widget.view.legend.show()
      
            
    def deactivate(self):
        self.display.widget.view.legend.hide()     