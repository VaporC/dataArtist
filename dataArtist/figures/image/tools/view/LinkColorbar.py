from  pyqtgraph_karl.Qt import QtGui

#OWN
from dataArtist.widgets.Tool import Tool
 


class LinkColorbar(Tool):
    '''
    Link the color bar gradient and range to another display
    '''
    icon = 'linkColorbar.svg'
    
    def __init__(self, display):
        Tool.__init__(self, display)

        self._linked_displays = []
        self._actions = []
        
        self._menu = QtGui.QMenu()
        self.setMenu(self._menu)
        self._menu.aboutToShow.connect(self._buildMenu)


    def _buildMenu(self):
        self._menu.clear()
        self._actions = []
        
        for d in self.display.workspace.displays():
            # add an action for all imageDisplays:
            if d != self.display and d.__class__ == self.display.__class__:
                a = QtGui.QAction(d.name(),self._menu, checkable=True)
                self._menu.addAction(a)
                self._actions.append(a)

                if d in self._linked_displays:
                    a.setChecked(True)

                a.triggered.connect(lambda checked, d=d, self=self: 
                                    self._linkColorbar(d, checked))



    def _linkColorbar(self, display, dolink=True):
        '''
        Link gradient and range from this display to the given slave display
        '''
        master = self.display.widget.ui.histogram
        slave = display.widget.ui.histogram
        
        if dolink:
            self.setChecked(True)
            self._linked_displays.append(display)
            master.linkHistogram(slave, connect=True)
            master.gradient.linkGradient(slave.gradient, connect=True)
        else:
            self._linked_displays.remove(display)
            #undo linking:
            master.linkHistogram(slave, connect=False)
            master.gradient.linkGradient(slave.gradient, connect=False)
            #check whether at least on of the other links is still active, 
            #      else: uncheck
            inactive = True
            for a in self._actions:
                if a.isChecked():
                    inactive = False
                    break
            if inactive:
                self.setChecked(False)


    def activate(self):
        for d in self.display.workspace.displays():
            if d != self.display:
                self._linkColorbar(d, True)
                return
        self.setChecked(False)


    def deactivate(self):
        self._buildMenu()
        for a in self._actions:
            if a.isChecked():
                a.trigger()