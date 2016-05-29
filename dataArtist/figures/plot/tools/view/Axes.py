from dataArtist.widgets.Tool import Tool
 

class Axes(Tool):
    '''
    Show/Hide the plot axes
    '''
    icon = 'axes.svg'
    
    def __init__(self, plotDisplay):
        Tool.__init__(self, plotDisplay)
        self.setChecked(True)


    def activate(self):
        self.display.widget.view.showAxis('bottom')
        self.display.widget.view.showAxis('left')


    def deactivate(self):
        self.display.widget.view.hideAxis('bottom')
        self.display.widget.view.hideAxis('left')