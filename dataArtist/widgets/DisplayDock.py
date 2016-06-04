import time
import inspect
import weakref
import numpy as np

from pyqtgraph_karl.Qt import QtGui, QtCore

from fancywidgets.pyqtgraphBased.parametertree import ParameterTree, Parameter
from fancywidgets.pyqtgraphBased.parametertree.parameterTypes \
                        import GroupParameter, ListParameter

from fancytools.os.PathStr import PathStr
from fancytools.fcollections.removeDuplicates import removeDuplicates

#METADATA reader:
# from hachoir_core.error import HachoirError
# from hachoir_core.cmd_line import unicodeFilename
# from hachoir_parser import createParser
# from hachoir_metadata import extractMetadata

#OWN
from dataArtist.widgets.Automation import Automation
from dataArtist.input.getFileReader import getFileReader
from dataArtist.items.axis import AxesContainer
from dataArtist.widgets.docks import DockBase as Dock

from dataArtist import figures
FIGURES = inspect.getmembers(figures, inspect.isclass)
del figures



class DisplayDock(Dock):
    '''
    A Dock container to...
    
    * OPEN and DISPLAY given input within a fitting display widget 
         (e.g. display.Image for images)
    * adding, (re)moving, copying input LAYERS (e.g. multiple plots 
         or images of the same size)
    * choosing the right TOOLS for the corresponding display widget
    * creating PREFERENCES in INFORMATION about the input 
    '''
    clicked = QtCore.pyqtSignal(object) #self
    closed = QtCore.pyqtSignal(object) #self
    sigLayerChanged = QtCore.pyqtSignal(object) #self
    sigNewLayer = QtCore.pyqtSignal(object) #self
    
    def __init__(self, number, workspace, origin=None, index=None, 
                 names=None, title='', data=None, axes=None, info=None, 
                 changes=None, openfiles=True):
        '''
        ============   ===============================================
        Arguments      Description
        ============   ===============================================        
        number         The display number, like 1,2...
        workspace      The workspace within the display is
        names          Path(s) of input files to open
        title          ... of the DisplayDock
        data           ... to display within the corresponding widget
        axes           Instance of AxesContainer with names and scales
                       for the axes scaling the data
        origin         The origin display
        index          The index of the origin layer
        info           informational text about the input
        changes        Additional changes done to the data
        openfiles      [True/False] whether to open the files
                       given in [filenames]
        ============   ===============================================
        '''
        self.workspace = workspace  
        self.number = number

        self.widget = None

        self._isclosed = False

        #GET VALUES FROM ORIGIN DISPLAY
        data, names, axes, title = self._extractInfoFromOrigin(origin, index, 
                                                               data, names, axes, title)
        if data is None and names is None and axes is None:
            raise Exception('either filenames, data or axes must be given')
        one_layer = False
        
        #FORMAT FILENAMES TO A LIST OF FILENAMES:
        if names is None:
            if data is not None:
                names = [None]*len(data)
            else:
                names = []
        elif isinstance(names, basestring):
            names = [names]
            one_layer = True

        docktitle = self._getDockTitle(title, number,names)

        #INIT SUPER CLASS
        Dock.__init__(self, docktitle)

        #SETUP FILE READER:
        self.reader = None
        if names and data is None:#-->load input from file
            self.reader = getFileReader(names)
            self.reader = self.reader(weakref.proxy(self))
            #GET AXES FROM INPUT READER IF NOT DEFINED YET:
            if axes is None: 
                axes = self.reader.axes
        #CREATE/FORMAT AXES IF INPUT GIVES AS DATA:
        if axes is None: 
            axes = ['x', 'y', '', 'i','j'][:data[0].ndim+1]
        elif type(axes) == int:
            axes = ['x', 'y', '', 'i','j'][:axes]

        self.stack = _StackParameter(weakref.proxy(self))

        #PARAMETERS:
        self.p = Parameter.create(
                    name='', 
                    type='empty')

        #TAB DISPLAYING PREFERENCES AND INPUT INFORMATION:
        self.tab = _DisplayTab(weakref.proxy(self))
        #FILL PARAMETERS:
        self.pTitle = self.p.addChild({
                    'name':'Title',
                    'type':'str',
                    'value':''})
        self.pTitle.sigValueChanged.connect(self._setWidgetTitle)                        
        pSize = self.pTitle.addChild({
                    'name':'Size',
                    'type':'int',
                    'value':11})
        pSize.sigValueChanged.connect(lambda param, size: self.widget.setTitleSize(size))  

        self.pTitleFromLayer = self.pTitle.addChild({
                    'name':'From layer',
                    'type':'bool',
                    'value':False})
        self.pTitleFromLayer.sigValueChanged.connect(self._pTitleFromLayerChanged)  


        self.pLimitLayers = self.p.addChild({
                  'name':'Limit Layers',
                  'type':'bool',
                  'value':False})
        self.pLimitLayers.sigValueChanged.connect(self._pLimitLayersChanged)

        self.pMaxLayers = self.pLimitLayers.addChild({
                    'name':'Max. Layers',
                    'type':'int',
                    'value':10,
                    'visible':False,
                    'limits':[1,1e4]})
        
        self.pMaxLayers.sigValueChanged.connect(self._limitLayers)
 
        #HANDLING THE INPUT LAYERS:
        self.p.addChild(self.stack)
        self.axes = AxesContainer(weakref.proxy(self), axes, 
                                  weakref.proxy(self.stack))
        #ADD AXES PARAMETERS:
        self.p.addChild(self.axes.p)
        #LIST OF ALL FITTING DISPLAY FIGURES:
        widgetList = _DisplayFigureList(self)

        #UPDATE DATA FROM FILE USING SPECIFIED PREFERENCES: 
        #TODO: 'update' should only update file based data and no processed data
        if self.reader:
            pUpdate = Parameter.create(**{
                        'type':'action',
                        'name':'Update',
                        })
            if self.reader.preferences:
                pUpdate.addChild(self.reader.preferences)
            pUpdate.sigActivated.connect(self.updateInput)
            self.p.addChild(pUpdate)

        self.p.addChild(widgetList)
      
        #INIT WIDGET
        self.changeWidget(widgetList.getWidget())#, data, names)
        #ADD DATA
        if len(names):
            if data is None and PathStr(names[0]).isfile():
                self.addFiles(names, openfiles)
            #TODO: what to do with mixed file/non file input?
            else:
                if one_layer:
                    self.addLayer(data, names[0], origin=origin)
                else:
                    self.addLayers(data, names, origin=origin)


    def _limitLayers(self, param, val):
        #remove surplus layers
        for _ in range(len(self.stack.childs) - val):
            self.stack.children()[0].remove()  


    def _pLimitLayersChanged(self, p,val):
        p = self.pMaxLayers
        p.show(val)
        if val:
            self._limitLayers(None, p.value())
        

    def _pTitleFromLayerChanged(self, param, val):
        self.pTitle.setOpts(readonly=val)
        w = self.widget
        if val: 
            w.sigTimeChanged.connect(self._setTitleFromCurrentLayer)
            self._setTitleFromCurrentLayer(w.currentIndex)
        else:
            try:
                w.sigTimeChanged.disconnect(self._setTitleFromCurrentLayer)
                self._setWidgetTitle(None, self.pTitle.value())
            except:
                pass
    

    def _setWidgetTitle(self, param, title):
        if not title:
            title = None
        self.widget.setTitle(title)


    def _setTitleFromCurrentLayer(self, index):
        try:
            self.widget.setTitle(
                self.stack.childs[index].name())
        except IndexError:
            pass #there are no layers


    @staticmethod
    def _getDockTitle(title, number, names):
        '''
        create a title for this display dock

        names -> list instances of PathStr
        '''
        docktitle = '[%s] ' %number
        if title:
            docktitle += title
        if len(names) > 1:
            #if multiple files imported:
            #FOLDER IN TITLE
            dirname = PathStr(names[0]).dirname()
            if len(dirname) > 20:
                dirname = '~'+dirname[-20:]
            docktitle += "%s files from %s" %(len(names), dirname)
        elif names and names != [None]:
            #FILENAME IN TITLE
            name = PathStr(names[0]).basename()
            if len(name) > 20:
                name = name[:8]+'(...)'+name[-8:]
            docktitle += name
        return docktitle
        

    def _extractInfoFromOrigin(self, origin, index, 
                               data, names, axes, docktitle):
        '''
        get data, filenames, axes from the origin display
        if there value is None
        '''
        
        if origin:
            ch = origin.stack.childs
            if index is None:
                if data is None:
                    data = origin.widget.getData()
            else:
                if data is None:
                    data = [origin.widget.getData(index)]

                ch = [ch[index]]

            if names is None:
                names = [c.name() for c in ch]
                if index is not None:
                    names = names[0]
            if axes is None:
                axes = origin.axes.copy()
            if not docktitle:
                docktitle = 'Child'
            docktitle = '%s of %s' %(docktitle, origin.shortName())
        return data, names, axes, docktitle


    def shortName(self):
        return '[%s]' %self.number


    def _getNDataLayers(self, axes, data):
        '''
        define number of data layers interpreting [data] and it's [axes]
        '''
        l = len(axes)
        #get number of dimensions (nDim) and shape without the need of an ndarray:
        try:
            x = data
            shape = []
            while True:
                shape.append(len(x))
                x = x[0]
        except TypeError:
            ndim = len(shape)
        except IndexError:
            #has no layers jet
            return 0
        if l == ndim + 1:
            #stack with one layer or no stack:
            nlayers = 1
        elif l == ndim or l == ndim-1:
            #multiple layers:
            nlayers = shape[0]
        else:
            raise Exception("number of axes doesn't fit to data shape")
        return nlayers


    def mousePressEvent(self, event):
        '''
        emits the signal 'clicked' if it is activated
        '''
        self.clicked.emit(weakref.proxy(self))


    def close(self):
        '''
        emits the signal 'closed'
        '''
        Dock.close(self)
        self._isclosed = True
        self.workspace.gui.undoRedo.displayClosed(self)
        self.closed.emit(self)
        self.widget.close()


    def isClosed(self):
        return self._isclosed


    def __getattr__(self, attr):
        '''
        this method is to access display layers easily in the built-in python shell
        
        if attribute cannot be found:
        return data or data-layer if attribute = 'l' or 'l0'...'l[layerNumber]'
        '''
        try:
            Dock.__getattr__(self, attr)
        except AttributeError:
            if attr[0] == 'l':
                a = attr[1:]
                if a != '':
                    if not a.isdigit():
                        raise AttributeError("display %s doesn't has attribute %s" 
                                        %(self.name(), attr))
                    a = int(a)
                    return self.widget.getData(a)
                return self.widget.getData()
            else:
                raise AttributeError("display %s doesn't has attribute %s" 
                                        %(self.name(), attr))
        
        
    def __setattr__(self, attr, value):
        '''
        this method is to access display layers easily in the built-in python shell

        if attribute is 'l' or 'l0'...'l[layerNumber]':
            set all data of a certain data layer to [value]  
        '''
        if attr[0] == 'l':
            a = attr[1:]
            if not a:
                #make sure that this display is updated through automation:
                self.tab.automation.checkWidgetIsActive(self.widget)
                
                nLayers = len(self.stack.childs)
                # CASE 'l'
                n = self._getNDataLayers(self.axes, value)
                if nLayers == n:
                    #print value
                    return self.widget.update(value)

                if nLayers != 0:
                    #remove old layers:
                    for i in range(nLayers):
                        self.removeLayer(i)
                if n > 1:
                    for layer in value:
                        self.addLayer(data=layer)
                else: 
                    return self.addLayer(data=value)
            elif a.isdigit():
                #make sure that this display is updated through automation:
                self.tab.automation.checkWidgetIsActive(self.widget)

                nLayers = len(self.stack.childs)
                # CASE 'l0'...'l[n]' 
                a = int(a)
                if a == nLayers:
                    #this index doesn't exist jet - so add a new layer
                    return self.addLayer(data=value)
                return self.widget.update(value, index=a)
        Dock.__setattr__(self, attr, value)


    def duplicate(self):
        '''
        create a new display with the same data and axes
        '''
        d = self.workspace.addDisplay(
            origin=self,
            title='Duplicate')
        d.p.restoreState(self.p.saveState())
        d.widget.restoreState(self.widget.saveState())
        return d


    def adaptParamsToWidget(self):
        s = self.widget.shows_one_layer_at_a_time

        self.pTitleFromLayer.show(s)
        if not s:
            #cannot set title from layer if all layers are displayed
            #at the same time
            self._pTitleFromLayerChanged(None, False)


    def changeWidget(self, widgetCls):
        '''
        change the display widget class and setup the toolbar
        '''
        self._reloadWidgetCls(widgetCls)
        #to init the new toolbars:
        self.clicked.emit(self) 

        self.adaptParamsToWidget()


    def reloadWidget(self):
        self._reloadWidgetCls(self.widget.__class__)


    def _reloadWidgetCls(self, widgetCls):
        data = None 
        state = None  
        toolbars = None     
        if self.widget:
            data = self.widget.getData()
            state = self.widget.saveState()
            toolbars = self.widget.toolbars

        names=self.layerNames()
        self.widget = widgetCls(weakref.proxy(self), self.axes, 
                                data=data, names=names, toolbars=toolbars)
        if state:
            self.widget.restoreState(state)
             
        Dock.setWidget(self, self.widget)    
        

    def insertRemovedLayer(self, index):
        '''
        Insert a layer moved to [index]
        '''
        self.widget.insertMovedLayer(index)


    def removeLayers(self):
        self.stack.clearChildren()
        self.widget.clear()
        self.filenames[:] = []


    def removeLayer(self, index, toMove=False):
        '''
        remove a data layer
        toMove=True => this layer will be moved within the stack 
        '''
        self.widget.removeLayer(index, toMove)


    def copyLayerToOtherDisplay(self, index, display):
        display.addLayer(origin=self, index=index)


    def moveLayerToOtherDisplay(self, index, display):
        display.addLayer(origin=self, index=index)
        self.stack.childs[index].remove()


    def copyLayerToNewDisplay(self, index):
        self.workspace.addDisplay(
            origin=self,
            index=index) 


    def moveLayerToNewDisplay(self, index):
        self.copyLayerToNewDisplay(index)
        self.stack.childs[index].remove()


    def layerNames(self):
        '''
        return the names of all data layers
        '''
        return [ch.name() for ch in self.stack.children()]


    @staticmethod
    def _getLayerLabel(fname, label):
        if fname is None:
            if label is None:
                return 'unknown'
            return label
        if PathStr(fname).isfile():
            fname = PathStr(fname).basename()
        if label is not None:
            return '%s - %s' %(label, fname)
        return fname
        

    def addLayer(self, data=None, filename=None, label=None, origin=None, 
                 index=None, info=None, changes=None, **kwargs):
        '''
        Add a new layer to the stack
        '''
        data, filename,  _, _ = self._extractInfoFromOrigin(origin, index, 
                                    data, filename, False, False)

        name = self._getLayerLabel(filename, label)
        #ADD TO PARAMETER TREE
        self.stack.buildLayer(filename,label=label, name=name, 
                              data=data, 
                              origin=origin.stack if origin else None, 
                              index=index, info=info, changes=changes)
        #WIDGET
        layer = self.widget.addLayer(name=name, data=data, **kwargs)
        if not self.widget.moveLayerToNewImage is None:
            print 'Move this layer to new display'
            #couldn't add new layer to stack: create a new display to show it            
            self.workspace.addDisplay(
                origin=self,
                index=len(self.filenames)-1, 
                data=[data]) 
            self.stack.childs[-1].remove()
        else:
            #LIMIT LAYERS
            if ( self.pLimitLayers.value() 
                and len(self.stack.childs) > self.pMaxLayers.value() ):
                self.stack.childs[0].remove()
            #AUTOMATION
            self.sigNewLayer.emit(self)
            return layer


    def backupChangedLayer(self, backup=None, changes=None, index=None, **kwargs):
        #UNDO/REDO
        ur = self.workspace.gui.undoRedo
        if ur.isActive():
            #index = kwargs.get('index', None)
            widget = self.widget
            if backup is None:
                data = widget.getData(index)
                if data is None:
                    return
                backup = data.copy()
            name = self.shortName()
            if index is not None:
                name += "-%s" %index
            name += ": %s" %changes

            ur.add(
                display=self, 
                name=name, 
                undoFn=lambda i=index, d=backup: 
                            self.changeLayer(data=d, changes='undo', index=i, 
                                             backup=False),
                redoFn=lambda d, i=index: 
                            self.changeLayer(data=d, changes='redo', index=i, 
                                             backup=False),
                dataFn=lambda i=index,w=widget: 
                    w.getData(i).copy()
                )


    def changeAllLayers(self, data=None, changes=None, backup=True, **kwargs):
        if backup:
            self.backupChangedLayer(data, changes, **kwargs)        
        self.widget.update(data, **kwargs)
        self.widget.updateView()
        for index in range(len(self.stack.childs)):
            self.stack.addChange(changes, index=index)
        self.sigLayerChanged.emit(self)


    def changeLayer(self, data=None, changes=None, index=None, backup=True, **kwargs):
        if backup:
            self.backupChangedLayer(data, changes, index, **kwargs)
        self.widget.update(data, index=index, **kwargs)
        self.widget.updateView()
        self.stack.addChange(changes, index=index)
        self.sigLayerChanged.emit(self)
            
            
    def showToolBar(self, name):
        '''
        show an other toolbar of the same display.widget
        if hidden
        '''
        #make given toolbar tool visible
        found = False
        for t in self.widget.toolbars:
            if t.name.lower() == name.lower():
                t.setSelected(True)
                found = True
                break
        if not found:
            raise Exception('Toolbar [%s] doesnt exist' %name)
        else:
            return t


    def changeLayerFiles(self):
        filt = '*.'+ ' *.'.join(self.reader.ftypes)
        fnames =  self.workspace.gui.dialogs.getOpenFileNames(filter=filt)
        if fnames:
            self.removeLayers()
            self.addFiles(fnames)


    def changeLayerFile(self, index):
        '''
        change the origin file of layer of [index]
        '''

        filt = '*.'+ ' *.'.join(self.reader.ftypes)
        fname =  self.workspace.gui.dialogs.getOpenFileName(
                    filter=filt, directory=self.filenames[index].dirname())        
        if fname is not None:
            self._readFiles([fname], self._updateFiles)


    @property
    def filenames(self):
        return removeDuplicates([c.opts['filename'] for c in self.stack.childs])


    def layerIndex(self, filename, layername):
        for n, ch in enumerate(self.stack.childs):
            if ch.opts['filename'] == filename and ch.opts['layername'] == layername:
                return n
        return None

                 
    def updateInput(self):
        '''
        Update the input coming from file
        '''
        self._readFiles(self.filenames, self._updateFiles)


    def _updateFiles(self, data, fnames, labels):        
        old_fnames = [c.opts['filename'] for c in self.stack.childs]
        old_labels = [c.opts['layername'] for c in self.stack.childs]
        changes = 'reloaded at ' + time.strftime("%c")
        
        if fnames == old_fnames and labels == old_labels:
            self.changeAllLayers(data, changes=changes, backup=True)
        else:
            #layers cannot be easily exchanged, so:
            for d, f, l in zip(data,fnames, labels):
                index = self.layerIndex(f, l)
                if index is not None:      
                    self.changeLayer(d, 
                        changes='reloaded at ' + time.strftime("%c"),
                        index=index)
                else:
                    #TODO: insert layer behind last filename layer
                    self.addLayer(filename=f, label=l, data=d)
                

    def addLayers(self, datas, fnames, labels=None, **kwargs):
        if labels is None:
            labels = [None]*len(fnames)
        for l,f,d in zip(labels, fnames, datas):
            self.addLayer(data=d, filename=f, label=l, **kwargs)


    def addFiles(self, fnames, openfiles=True):
        '''
        Add input from file(s) to the stack
        -> read input
        -> add layer
        '''
        ff = self.filenames
        for f in list(fnames):
            if f in ff:
                print "file '%s' already in display '%s'" %(f, self.name())
                #fnames.remove(f)
        if fnames:
            if not self.reader:
                self.reader = getFileReader(fnames)
                self.reader = self.reader(self)
            if openfiles:
                self._readFiles(fnames, self.addLayers)
            else:
                d = [None]*len(fnames)
                self.addLayers(d, fnames, d)


    def saveState(self):
        state = {}
#         path += ('display',str(self.number))
        #layers
        state['stack'] = self.stack.saveState()
        #automation
        state['automation'] = self.tab.automation.saveState() 
        #parameters
        state['parameters'] =  self.p.saveState()    
#         session.addContentToSave(self.p.saveState(), *path+('parameters.txt',))
        #dock
        state['dock'] = self.label.maximized
#         session.addContentToSave(self.label.maximized, *path+('dock.txt',))
        #to init the current toolbars:
        self.clicked.emit(self) 
        #widget
        state['widget'] = self.widget.saveState()
        return state
   
   
    @property
    def tools(self):
        return self.widget.tools


    def restoreState(self, state):
        #layers
        self.stack.restoreState(state['stack'])
        #automation
        self.tab.automation.restoreState(state['automation'])  
        #parameters
        #TODO: this is not clean - stack is mentioned above and already restore its parameters...
        self.stack._valuesChanged()
        self.p.restoreState(state['parameters'])
        #widget
        self.widget.restoreState(state['widget'])
        #dock
        if state['dock']:
            self.maximize()


    def openFilesFunctions(self):
        return [lambda f=f: self.reader.open(f)[0] for f in self.filenames]


    def _readFiles(self, filenames, dataFunction):
        try:
            self.reader.done.disconnect()
        except TypeError:
            pass # nothing connected so far
        self.reader.done.connect(dataFunction)
        self.reader.start(filenames)



class _DisplayTab(QtGui.QSplitter):
    '''
    A QSplitter containing...
    * Automation
    * Display Preferences 
    '''
    def __init__(self, display):
        QtGui.QSplitter.__init__(self, QtCore.Qt.Orientation(0))#0=horiz, 1=vert) 
        self.display = display
        self.automation = Automation(display, self)
        self.prefs = _PreferencesWidget(display)
        self.addWidget(self.automation)
        self.addWidget(self.prefs)



class _PreferencesWidget(QtGui.QWidget):
    '''
    Format 'Preferences'-ParameterTree
    and add a Title on top 
    '''
    def __init__(self, display):
        QtGui.QWidget.__init__(self)
        l = QtGui.QVBoxLayout()
        self.setLayout(l)
        #PAREMETERTREE
        pref = ParameterTree(display.p, showHeader=False) 
        h = pref.header()
        h.setResizeMode(0,QtGui.QHeaderView.Stretch)
        h.setStretchLastSection(False)
        #TITLE
        l.addWidget(QtGui.QLabel('<b>Preferences</b'))
        l.addWidget(pref) 



class _DisplayFigureList(ListParameter):
    '''
    ListParameter showing all display FIGURES available 
    for the dimensions of the input
    '''
    def __init__(self, display):
        self.display = display

        names, icons = self.getWidgetList()

        ListParameter.__init__(self, **{
                    'name':'Figure',
                    'limits':names,
                    'icons':icons})
   
        self.sigValueChanged.connect(lambda param, value: 
            self.display.changeWidget(self._name_to_figure[value]))

       
    def getWidget(self):
        '''
        return the first widget in the list
        '''
        return self._name_to_figure[self._name_to_figure.keys()[0]]
     

    def getWidgetList(self):
        self._name_to_figure = {}
        icons = []
        #create a list with all possible displays according to the number of dimensions
        for name, cls in FIGURES:
            dimensions = getattr(cls, 'dimensions', None)
            if dimensions:
                #is this display able to display our data?
                if len(self.display.axes) in dimensions: 
                    self._name_to_figure[name] = cls
                    icons.append( getattr(cls, 'icon', None) )                    
            else:
                print "%s doens't have needed attribute 'dimensions'" %cls.__name__
        return self._name_to_figure.keys(), icons
      


class _StackParameter(GroupParameter):
    '''
    Parameter containing information about all input layers and 
    allowing to change their position within the stack
    '''
    sigValuesChanged = QtCore.pyqtSignal(object) #values
    sigLayerNameChanged = QtCore.pyqtSignal(int, object)#index, name

    def __init__(self, display):
        self.display = display

        mAll = QtGui.QMenu('All layers')
        mAll.addAction('Change').triggered.connect(self.display.changeLayerFiles)
        mAll.addAction('Remove').triggered.connect(self.display.removeLayers)

        GroupParameter.__init__(self, **{
                    'name':'   Layers',
                    'sliding':True,
                    'addToContextMenu':[mAll]})
        #IF A LAYER IS MOVED:
        self.sigChildRemoved.connect(lambda parent, child, index, self=self: 
                        self.display.removeLayer(index, 
                                                 self.opts.get('aboutToMove', False)))
        self._fnInsertRemovedLayer = lambda parent, child, index, self=self: \
                                        self.display.insertRemovedLayer(index)
        self.sigChildAdded.connect(self._fnInsertRemovedLayer)
        self.sigChildAdded.connect(self._valuesChanged)
        self.sigChildRemoved.connect(self._valuesChanged)
        

    def _extractFromOrigin(self, origin, index, 
                           info, changes):
        '''
        get 'Info' and 'Changes' from origin StackParameter
        append origin-changes with new changes
        '''
        if origin:
            ch = origin.children()
            if not info:
                info = [c.param('Info').value() for c in ch]
                if index is not None:
                    info = info[index]
                else:
                    info = '\n---\n'.join(info)
            origin_changes = ''
            for c in ch:
                v = c.param('Changes').value()
                if len(v):
                    origin_changes += ';%s ' %v
            if changes:
                if type(changes) in (tuple, list):  
                    changes = changes[index]
                changes += '\n%s' %origin_changes
            else:
                changes = origin_changes  
        return info, changes


    def _valuesChanged(self):
        '''
        all layers create an additional stack-dimension with it's own values
        e.g. a set of images, where every layer represents an image at another excitation time
           could have stack.values = [1,5,10,15,20] [s] 
           as soon as the position of a layer changed or a layer is removed
           these values (e.g.excitation times) have to updated as well
        '''
        self.values = np.array( [ch.value() for ch in self.childs] )
        self.sigValuesChanged.emit(self.values)

# 
#     def save(self, session, path):
#         '''
#         save parameter values to file 'stack.txt'
#         '''
#         session.addContentToSave(self.saveState(), *path+('stack.txt',))
#      
 
    def restoreState(self, state, **kwargs):
        '''
        set parameter values using file 'stack.txt'
        '''
        #DON'T DO ANYTHING WHILE THE STACK IS UPDATED:
        self.blockSignals(True)
        self.clearChildren()
        self.blockSignals(False)
        self.sigChildAdded.disconnect(self._fnInsertRemovedLayer)
        #REBUILD STACK:
#         l =  eval(session.getSavedContent(*path +('stack.txt',) )  )
        GroupParameter.restoreState(self, state, **kwargs)
        self.sigChildAdded.connect(self._fnInsertRemovedLayer)


    def buildLayer(self, fname, label, name, data, origin=None, index=None, 
                         info=None, changes=None):
        '''
        for every layer of the stack add a parameter containing ...
        * it's stack value
        * an layer info field
        * a layer changed field
        '''
        info, changes = self._extractFromOrigin(origin, index, info, changes)
        try:
            self.sigChildAdded.disconnect(self._fnInsertRemovedLayer)
        except TypeError:
            pass
        
        #ADD OPTIONS TO THE CONTEXT MENU:
        mCopy = QtGui.QMenu('Copy')
        mMove = QtGui.QMenu('Move')

        if not fname or not PathStr(fname).isfile():
            fname = None

        menu_entries = [mCopy, mMove]
        if self.display.reader is not None:
            aFile = QtGui.QAction('Change File', self)
            aFile.triggered.connect(lambda checked, i=len(self.childs): 
                                        self.display.changeLayerFile(i))
            menu_entries.append(aFile)
        #CREATE AND ADD COPY-LAYER-TO OPTION TO PARAMETER:
        pLayer = self.addChild({
                'type':'float',
                'isGroup':True,
                'name':name,
                'value':self.display.axes.stackAxis.getNextStackValue(
                                            PathStr(fname).basename()),
                'expanded':False,
                'removable':True,
                'autoIncrementName':True,
                'renamable':True,
                'readonly':True,
                'addToContextMenu':menu_entries,
                
                'filename':fname,
                'layername':label,
                })
        mCopy.aboutToShow.connect(lambda pLayer=pLayer, mCopy=mCopy, self=self: 
                    self.buildCopyToDisplayMenu(mCopy, pLayer, 'copy'))
        mMove.aboutToShow.connect(lambda pLayer=pLayer, mMove=mMove, self=self: 
                    self.buildCopyToDisplayMenu(mMove, pLayer, 'move'))
                
        #UPDATE STACK VALUES:
        pLayer.sigValueChanged.connect(self._valuesChanged)
        #EMIT LAYERNAMESCHANGED:
        pLayer.sigNameChanged.connect(lambda param, val, self=self: 
                    self.sigLayerNameChanged.emit(param.parent().children().index(param), val) )
        #CHECK WHETHER INSERTED LAYER COMES FROM A MOVED ONE:
        self.sigChildAdded.connect(self._fnInsertRemovedLayer)
        #ADD LAYER INFO
        if info is None:
            finfo = ''
            if fname is not None:
                try:
                    #read info from file:
                    finfo += self.getFileInfo(fname) + '\n'# + self.getMetaData(name)              
                except AttributeError:
                    pass
                #    finfo = '' #not possible to read from file because maybe not a filename
            dinfo = ''
            if data is not None:
                try:
                    dinfo = 'shape:\t%s\ndtype:\t%s' %(data.shape, data.dtype)
                except AttributeError:
                    #data in not array
                    dinfo = 'length: %s' %len(data)
            info = '%s---\n%s' %(finfo, dinfo)
            
        if isinstance(info, Parameter):
            #CASE: layer was duplicated and [info] is a parameter
            for ch in info.children():
                pLayer.addChild(ch.duplicate())
        else:
            #info is given as text
            #LAYER INFO
            pLayer.addChild({
                'type':'text',
                'name':'Info',
                'value':info if info !=None else '',
                'readonly':True})
        #LAYER CHANGES
        pLayer.addChild({
            'type':'text',
            'name':'Changes',
            #'TODO: every change through a tool/scripts operation to be added here',
            'value':changes if changes else '',
            #'readonly':True
            'expanded': bool(changes)
            })


    def addChange(self, change, index=None):
        if change is not None:
            ch = self.children()
            if index is not None:
                ch = [ch[index]]
     
            if type(change) not in (tuple, list):
                change = [change] * len(ch)
    
            for n,c in enumerate(ch):    
                p = c.param('Changes') 
                v = p.value()
                if not v:
                    p.setValue(change[n])
                    p.setOpts(expanded=True)
                else:
                    p.setValue('%s\n%s' %(p.value(), change[n]))


    def buildCopyToDisplayMenu(self, menuCopy, paramFile, method):
        '''
        clear the context menu 'copy'
        add 'NEW' to copy a layer to a new display
        add names of all other displays
        connect all actions to respective display methods
        '''
        menuCopy.clear()
        
        #NEW:
        if method=='copy':
            m = self.display.copyLayerToNewDisplay
        else:
            m = self.display.moveLayerToNewDisplay
        
        menuCopy.addAction('NEW').triggered.connect(
            lambda checked,  paramFile=paramFile, m=m:
                m(paramFile.parent().children().index(paramFile) ) )
        
        #OTHER DISPLAYS:      
        if method=='copy':
            m = self.display.copyLayerToOtherDisplay
        else:
            m = self.display.moveLayerToOtherDisplay
        
        for d in self.display.workspace.displays():
            if d != self.display and d.widget.__class__ == self.display.widget.__class__:
                menuCopy.addAction( d.name() ).triggered.connect(
                    lambda checked, paramFile=paramFile, d=d, m=m: 
                        m(paramFile.parent().children().index(paramFile), d)
                                                                 )


    def getFileInfo(self, filename):
        '''
        return general information of the given [filename], like it's size
        '''
        f = QtCore.QFileInfo(filename)
        size = f.size()
        size_type = ['Byte', 'kB', 'MB', 'GB', 'TB', 'PB']
        size_index = 0
        while size > 1024:
            size /= 1024.0
            size_index += 1
            
        size = "%.3g %s" % (round(size,3), size_type[size_index])
        n = f.fileName()
        return '''File name:\t%s
Folder:\t%s
File type:\t%s
File size:\t%s
Last changed:\t%s''' %(n,f.filePath()[:-len(n)],
                       f.suffix(), 
                       size, 
                       f.lastModified().toString())

    #TODO: not used at the moment
    #but useful
#     def getMetaData(self, filename):
#         '''
#         Find and format the meta data of [filename]
#         '''
#         text = ""
#         if  filename.filetype().lower() not in ('tif', 'tiff'):
#             #for all files except TIF
#             filename, realname = unicodeFilename(filename), filename
#             parser = createParser(filename, realname)  
#             if not parser:
#                 print  "Unable to parse file"
#             try:
#                 metadata = extractMetadata(parser)
#             except HachoirError, err:
#                 #AttributeError because hachoir uses  
#                 print "Metadata extraction error: %s" % unicode(err)
#                 metadata = None
#             if not metadata:
#                 print "Unable to extract metadata"
#             else:
#                 text = "\n".join(metadata.exportPlaintext())
#         else:
#             #for TIF images
#             import exifread
#             # Open image file for reading (binary mode)
#             f = open(filename, 'rb')
#             # Return Exif tags
#             tag_dict = exifread.process_file(f)
#             for key, value in tag_dict.iteritems():
#                 text += "%s: %s\n" %(key, value)
#         return text