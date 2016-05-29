from dataArtist.widgets.Tool import Tool
 

class Axes(Tool):
    '''
    Show/Hide the image axes
    '''
    icon = 'axes.svg'
    reinit = True
    
    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)
        self.setChecked(True)


    def activate(self):
        self.display.widget.view.showAxis('bottom')
        self.display.widget.view.showAxis('left')


    def deactivate(self):
        self.display.widget.view.hideAxis('bottom')
        self.display.widget.view.hideAxis('left')