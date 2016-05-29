from dataArtist.widgets.Tool import Tool


class GlobalTool(Tool):
    '''
    Tool, accessible for all display widgets of the same class.
    to be shown in the top right corner of the gui
    '''

    def __init__(self, display):
        Tool.__init__(self, display)
        self._display = display
        self.gui = display.workspace.gui

    
    @property
    def display(self):
        '''
        return the current of the last valid display
        '''
        d = self.gui.currentWorkspace().getCurrentDisplay()
        if self._display.isClosed() or d.__class__ == self._display.__class__:
            self._display = d
        return self._display
    
    
    @display.setter
    def display(self, d):
        #display cannot be changed
        pass