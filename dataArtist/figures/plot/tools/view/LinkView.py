from collections import OrderedDict

from dataArtist.widgets.Tool import Tool
 


class LinkView(Tool):
    '''
    Link the current view range to another display
    '''
    icon = 'linkView.svg'
    
    def __init__(self, display):
        Tool.__init__(self, display)

        self._d = None
        pa = self.setParameterMenu() 
        
        self.pX = pa.addChild({
            'name':'x',
            'type':'list'})
        self.pY = pa.addChild({
            'name':'y',
            'type':'list'})
        self._menu.aboutToShow.connect(self._buildMenu)


    def _buildMenu(self):
        '''
        Add an action for all other displays and connect it to
        self._linkView
        '''
        self._d = OrderedDict()
        self._d['-'] = None
        for d in self.displayworkspace.displays():
            if d != self.display:
                self._d[d.name()] = d

        n = self._d.keys()
        for p in (self.pX, self.pY):
            p.setLimits(n)
            if p.value() not in n:
                p.setValue(n[0])


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
        #flickering occurs, if aspect ration of both displays is locked, so:
        if master.vb.state['aspectLocked']:
            slave.vb.setAspectLocked(False)  


    def activate(self):
        if self._d is not None:
            v = self.display.widget.view
            dx = self._d[self.pX.value()]
            if dx is not None:
                v.setXLink(dx.widget.view)
            dy = self._d[self.pY.value()]
            if dy is not None:
                v.setYLink(dy.widget.view)


    def deactivate(self):
        v = self.display.widget.view
        v.setXLink(None)
        v.setYLink(None)
