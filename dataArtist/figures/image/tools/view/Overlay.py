from pyqtgraph_karl.Qt import QtGui
#OWN
from dataArtist.widgets.Tool import Tool



class Overlay(Tool):
    '''
    manage multiple single color overlays
    '''
    icon = 'overlay.svg'
    
    def __init__(self, display):
        Tool.__init__(self, display)

        pa = self.setParameterMenu() 
        
        #make some space for the color layer names:
        self._menu.pTree.header().setResizeMode(QtGui.QHeaderView.Fixed)
        self._menu.pTree.setColumnWidth (0, 270)

        self.pAdd = pa.addChild({
                    'name':'add',
                    'value':'from display',
                    'type':'menu'})
        self.pAdd.aboutToShow.connect(self.buildAddMenu)
        
        pa.sigChildRemoved.connect(self.removeLayer)
        
        w = self.display.widget
        w.sigOverlayAdded.connect(self.addLayerControl)
        w.sigOverlayRemoved.connect(self.removeLayerControl)


    def addLayerFromOtherDisplay(self, display, layernumber, layername):
        im = display.widget.image
        im = im[layernumber]
        self.display.widget.addColorLayer(im, layername, tip='')


    def buildAddMenu(self, menu):
        '''
        add an action for all layers of other ImageDisplays
        '''
        menu.clear()
        for d in self.display.workspace.displays():
            if d.widget.__class__ == self.display.widget.__class__:
                m = menu.addMenu(d.name())
                for n,l in enumerate(d.layerNames()):
                    m.addAction(l).triggered.connect(
                    lambda checked, d=d, n=n,l=l: 
                        self.addLayerFromOtherDisplay(d, n, l) )


    def removeLayer(self, parent, child):
        if child != self.pAdd:
            self.display.widget.removeColorLayer(child.name())
            if len(parent.children()[1:]) == 0:
                self.setChecked(False)


    def _exportLayerToNewDisplay(self, name):
        for ch in self._menu.p.childs:
            if name == ch.name():
                item = ch.opts['item']
                break
        self.display.workspace.addDisplay(
                    origin=self.display,
                    axes=self.display.axes.copy(),
                    data=[item.image], 
                    title='Color overlay (%s)' %name ) 


    def removeLayerControl(self, item):
        '''
        remove color button in parameter menu if an overlay is removed
        '''
        for ch in self._menu.p.children()[1:]:
            i = ch.opts.get('item',None) #can be None, when called from restore
            if i == item:
                self._menu.p.sigChildRemoved.disconnect(self.removeLayer)
                ch.opts['item']=None
                ch.remove()
                self._menu.p.sigChildRemoved.connect(self.removeLayer)
                break
        if len(self._menu.p.children()[1:]) == 0:
            self.setChecked(False)            


    def addLayerControl(self, item, name, tip=''):
        '''
        add color button in parameter menu if an overlay is added
        '''

        aExport = QtGui.QAction('Export to new display', self._menu.p)
        aExport.triggered.connect(lambda c, n=name:
                                  self._exportLayerToNewDisplay(n))
        
        p = self._menu.p.addChild({
                    'name':name,
                    'isGroup':True,
                    'type':'color',
                    'tip':tip,
                    'removable':True,
                    'autoIncrementName':True,
                    'addToContextMenu':[aExport],
                    #TODO:
                   # 'sliding':True
                   'item':item
                    })
        p.setValue(item.getQColor())
        p.sigValueChanged.connect(
                lambda param, val: param.opts['item'].setQColor(val) ) 
        
        self.setChecked(True)     


    def saveState(self):
        state = Tool.saveState(self)
        #save the layers to file
        for n, ch in enumerate(self._menu.p.children()[1:]):
            state['c_layer_%i' %n] = ch.opts['item'].image
        return state


    def restoreState(self, state):
        Tool.restoreState(self, state)
        old_ch = list(self._menu.p.childs[1:])

        #remove old param:
        pa = self._menu.p
        pa.sigChildRemoved.disconnect(self.removeLayer)
        for ch in old_ch:
            pa.removeChild(ch)
        pa.sigChildRemoved.connect(self.removeLayer)
        
        for n, ch in enumerate(old_ch):
            #load layers from file
            img = state['c_layer_%i' %n]
            self.display.widget.addColorLayer(img, name=ch.opts['name'], tip=ch.opts['name'])


#     def save(self, session, path):
#         Tool.save(self, session, path)
#         #save the layers to file
#         for n, ch in enumerate(self._menu.p.children()[1:]):
#             p = session.createSavePath(*path+('colorLayer_%s.npy' %n,))
#             np.save(p,ch.opts['item'].image)
# 
# 
#     def restore(self, session, path):
#         Tool.restore(self, session, path)
#         old_ch = list(self._menu.p.childs[1:])
# 
#         #remove old param:
#         pa = self._menu.p
#         pa.sigChildRemoved.disconnect(self.removeLayer)
#         for ch in old_ch:
#             pa.removeChild(ch)
#         pa.sigChildRemoved.connect(self.removeLayer)
#         
#         for n, ch in enumerate(old_ch):
#             #load layers from file
#             p = session.getSavedFile(*path+('colorLayer_%s.npy' %n,))
#             img = np.load(p)
#             self.display.widget.addColorLayer(img, name=ch.opts['name'], tip=ch.opts['name'])


    def activate(self):
        '''
        show all color layers
        '''
        for ch in self._menu.p.children()[1:]:
            ch.opts['item'].show()


    def deactivate(self):
        '''
        hide all color layers
        '''
        for ch in self._menu.p.children()[1:]:
            ch.opts['item'].hide()