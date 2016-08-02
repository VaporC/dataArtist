from pyqtgraph.Qt import QtGui


from dataArtist.widgets.Tool import Tool


class LockView(Tool):
    '''
    Lock the aspect ratio of the current view
    '''
    icon = 'aspectRatio.svg'
    
    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)
        
#         self._linked_display = None

        self.setChecked(self.display.widget.view.vb.state['aspectLocked'])

        pa = self.setParameterMenu() 

        pSync = pa.addChild({
            'name':'Synchronize',
            'value':'Display',
            'type':'menu',
            'highlight':True
            })
        pSync.aboutToShow.connect(self._buildLinkView)

        pRange = pa.addChild({
            'name': 'autoRange',
            'type': 'bool',
            'value':True,
            'tip':'''whether to fit view every time the input changes'''})
        pRange.sigValueChanged.connect(lambda param, value: 
                                self.display.widget.setOpts(autoRange=value))


    def _buildLinkView(self, menu):
        '''
        Add an action for all other displays and connect it to
        self._linkView
        '''
        menu.clear()
        vb =  self.display.widget.view.vb
        vb_linked = vb.state['linkedViews'][0]
        if vb_linked: 
            #get object from weakref
            vb_linked = vb_linked()
#         ag = QtGui.QActionGroup(menu, exclusive=True)

        for d in self.display.workspace.displays():
            if d.name() != self.display.name():
#                 a = ag.addAction(QtGui.QAction(d.name(),menu, checkable=True))
                a = QtGui.QAction(d.name(),menu, checkable=True)
                menu.addAction(a)
                #IS LINKED?:
                vb2 = d.widget.view.vb
                vb2_linked = vb2.state['linkedViews'][0]
                if vb2_linked: 
                    #get object from weakref
                    vb2_linked = vb2_linked()
                linked = False
                if (vb_linked == vb2) or (vb2_linked == vb):
                    linked = True
                    a.setChecked(True)

                a.triggered.connect(lambda checked, d=d,linked=linked: 
                                    self._linkView(d, linked))


    def _linkView(self, display, linked):
        master = self.display.widget.view
        slave = display.widget.view
        if not linked:
            #if aspect ration of both displays is locked there is a flickering
            #in the slave-display, so...
            if master.vb.state['aspectLocked']:
                slave.vb.setAspectLocked(False)  
            master.setXLink(slave)
            master.setYLink(slave)  
        else:
            slave.setXLink(None)
            slave.setYLink(None)
            master.setXLink(None)
            master.setYLink(None)  


    def activate(self):
        self.display.widget.view.vb.setAspectLocked(True)
        

    def deactivate(self):
        self.display.widget.view.vb.setAspectLocked(False)