from dataArtist.widgets.Tool import Tool
 


class TimeLine(Tool):
    '''
    Show/Hide the time line
    '''
    icon = 'timeLine.svg'
    
    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)
        self.setChecked(True)


    def activate(self):
        self.display.widget.showTimeline(True)


    def deactivate(self):
        self.display.widget.showTimeline(False)
