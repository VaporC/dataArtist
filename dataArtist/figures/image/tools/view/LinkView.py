from  pyqtgraph_karl.Qt import QtGui

#OWN
from dataArtist.widgets.Tool import Tool
 


class LinkView(Tool):
    '''
    Link the current view range to another display
    '''
    icon = 'linkView.svg'
    
    def __init__(self, display):
        Tool.__init__(self, display)

        self._linked_display = None

        self._menu = QtGui.QMenu()
        self.setMenu(self._menu)
        self._menu.aboutToShow.connect(self._buildMenu)


    def _buildMenu(self):
        '''
        Add an action for all other displays and connect it to
        self._linkView
        '''
        self._menu.clear()
                
        ag = QtGui.QActionGroup(self._menu, exclusive=True)

        for d in self.display.workspace.displays():
            if d != self.display:
                
                a = ag.addAction(QtGui.QAction(d.name(),self._menu, checkable=True))
                self._menu.addAction(a)

                a.triggered.connect(lambda checked, d=d, self=self: 
                                    self._linkView(d, checked))
                if d == self._linked_display:
                    a.setChecked(True)


    def _linkView(self, display, link=True):
        master = self.display.widget.view
        slave = display.widget.view
        if link:
            self.setChecked(True)
            self._linked_display = display
        else:
            slave = None
        master.setXLink(slave)
        master.setYLink(slave)  
        #if aspect ration of both displays is locked there is a flickering
        #in the slave-display, so...
        if master.vb.state['aspectLocked']:
            slave.vb.setAspectLocked(False)  


    def activate(self):
        for d in self.display.workspace.displays():
            if d != self.display:
                self._linkView(d, True)
                return
        self.setChecked(False)
                

    def deactivate(self):
        v = self.display.widget.view
        v.setXLink(None)
        v.setYLink(None)
        self._linked_display = None