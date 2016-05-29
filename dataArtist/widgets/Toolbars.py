import traceback
import importlib
from pyqtgraph_karl.Qt import QtGui, QtCore 
import inspect

############################
# a typical tool-packages __init__.py file might look like that:
#from ToolMod1 import ToolCls1 
#from ToolMod2 import ToolCls2 
#
#position='top',
#show=True, # OR {"simple":True,"electroluminescence":False}
#secondRow=False,#show tools normally in first toolbar row
#tools=set(ToolCls1, Toolcls2 ...) #to define tool position in toolbar
#color=None OR 'red' ...
############################

TO_QT_POSITION = {'top':QtCore.Qt.TopToolBarArea,
                  'left':QtCore.Qt.LeftToolBarArea,
                  'right':QtCore.Qt.RightToolBarArea,
                  'bottom':QtCore.Qt.BottomToolBarArea}


def build(widget):
    '''
    create and return a list of toolbars for the given [displayWidget]
    '''
    #get name of the corresponding tools package:
    pkg_name = widget.__class__.__module__.split('.')[:-1]   
    pkg_name.append('tools')
    pkg_name = '.'.join(pkg_name)

    pkg = importlib.import_module(pkg_name)
    bars = inspect.getmembers(pkg, inspect.ismodule)

    l,l2 = [],[]
    for (bar_name, bar_mod) in bars:
        tools = getattr(bar_mod, 'tools', None)
        if tools is None: 
            tools = [t[1] for t in inspect.getmembers(bar_mod, inspect.isclass)]

        if len(tools):
        #EVERY FOLDER CONTAINING TOOLS BECOMES A TOOLBAR:
            toolbar = _ToolBar(bar_name, widget, bar_mod, tools)
            
            if getattr(bar_mod, 'secondRow', False):
                #put all toolbars ment to be shown in a second row in other list:
                l2.append(toolbar)
            else:
                l.append(toolbar)
    
    #create the second row:
    if l2:
        l2[0].hasBreak = True
        l.extend(l2)
    
    return l



class _ToolBar(QtGui.QToolBar):
    '''
    A ToolBar remembering it's position
    and whether it's selected.
    This allows to use one the same set of toolBars
    for different display widgets of the same kind
    '''
    def __init__(self, name, widget, pkg, toolClasses):
        QtGui.QToolBar.__init__(self, name)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._openContextMenu)
    
        name[0].islower()
        f = name[0]
        if f.islower():
            name = f.upper() + name[1:]
        
        self.name = name
        self.widget = widget
        self.toolClasses = toolClasses
        self._toolsCreated = False
        
        # there is a central setup for the visibility of all 
        # toolbars that have the same display widget:
        show = getattr(pkg, 'show', True)
        if isinstance(show, dict):
            #whether to show/hide a toolbar depends on the chosen profile:
            session = QtGui.QApplication.instance().session
            profile = session.app_opts.get('profile',None)
            show = show.get(profile, False)
        if self.widget.__class__.selectedToolbars.get(name, None) is None:
            self.widget.__class__.selectedToolbars[name] = [
                            show,
                            TO_QT_POSITION[getattr(pkg, 'position','top')], 
                            False]#->hasBreak

#         #add logo to toolbar:
#         icon  = getattr(pkg, 'icon', None)
#         if icon:
#             #icon can ge given as direct path
#             if not os.path.exists(icon):
#                 #otherwise it is assumed that 
#                 #the icon is to be found in the icon directory:
#                 icon = ICONFOLDER.join(icon) 
#             s = ToolBarIcon(self, icon)
            
            tip = getattr(pkg, '__doc__', None)
            ttname = name
            if tip:
                ttname += '\n\t%s' %tip
            self.setToolTip(ttname)
       
        #BACKGROUND COLOR:
        c = getattr(pkg, 'color', None)
        if not c is None:
            #create a semi-transparent colour from
            #normal background color (grey)
            #and given color:
            a = 0.9
            b = 1-a
            p = self.palette()
            bg = p.color(self.backgroundRole())
            c = QtGui.QColor(c)
            bg.setRed(a*bg.red()+b*c.red())
            bg.setGreen(a*bg.green()+b*c.green())
            bg.setBlue(a*bg.blue()+b*c.blue())
            self.setBackgroundRole(QtGui.QPalette.Window)       
            p.setColor(self.backgroundRole(), bg)
            self.setPalette(p)
            self.setAutoFillBackground(True)

        self.actionSelect = QtGui.QAction(name, self)
        self.actionSelect.setCheckable(True)
        self.actionSelect.setChecked(show)
        self.actionSelect.triggered.connect(self.setSelected)


    @property
    def position(self):
        return self.widget.__class__.selectedToolbars[self.name][1]
    @position.setter
    def position(self, val):
        if val == QtCore.Qt.NoToolBarArea:
            val = QtCore.Qt.TopToolBarArea
        self.widget.__class__.selectedToolbars[self.name][1] = val  


    @property
    def hasBreak(self):
        return self.widget.__class__.selectedToolbars[self.name][2]
    @hasBreak.setter
    def hasBreak(self, val):
        self.widget.__class__.selectedToolbars[self.name][2] = val  


    def _openContextMenu(self, pos):
        m = QtGui.QMenu()
        #title:
        a = QtGui.QAction(self.name, self)
        a.setSoftKeyRole(QtGui.QAction.NoSoftKey)
        f = a.font()
        f.setBold(True)
        a.setFont(f)
        m.addAction(a)
        m.addSeparator()
        
        m.addAction("Remove").triggered.connect(self.actionSelect.trigger)
        m.exec_(self.mapToGlobal(pos))

            
    def addTools(self):
        if not self._toolsCreated:
            #TO ALL TOOLS IN PACKAGE:
            for cls in self.toolClasses:
                try:
                    #CREATE TOOL
                    tool = cls(self.widget.display)
                    self.widget.tools[cls.__name__] = tool
                    #ADD TOOL
                    self.addWidget(tool)
                except Exception:
                    print "ERROR loading toolbutton: ", traceback.print_exc()
            self._toolsCreated = True
   
    
    def removeTools(self):
        #REMOVE TOOL TO FREE SOME MEMORY
        #TODO: REMOVING A TOOL DOESN'T FREE MEMORY AT THE MOMENT
        #      WHY? gc.collect(), tool.close(), tool.deletLater()...
        #      nothing works!

        #TODO: also remove this toolbar in other displays
        for cls in self.toolClasses:
            try:
                tool = self.widget.tools.pop(cls.__name__)
                del tool
            except KeyError:
                pass #tool no created yet
        for toolAction in self.findChildren(QtGui.QAction):
            self.removeAction(toolAction)
            del toolAction

        self._toolsCreated = False
                  
  
    def show(self):
        #ensure that all tools are loaded:
        QtGui.QToolBar.show(self)
        self.addTools()

 
#     def hide(self):
#         if not self.isSelected():
#             self.removeTools()
#         QtGui.QToolBar.hide(self)    


    def toggleViewAction(self):
        '''
        return an action to show/hide the toolbar
        '''
        self.actionSelect.setChecked(self.isVisible())
        return self.actionSelect


    def setSelected(self, select):
        '''
        store whether is selected to restore when toolbar is changed
        '''
#         if self.widget.__class__.selectedToolbars[self.name][0] == select:
#             return
        if self.isSelected() == select:
            return
        self.widget.__class__.selectedToolbars[self.name][0] = select
        if select:
            #self.addTools()
#             if not self._toolsCreated:
            self.show()
        else:
            self.hide()
            self.removeTools()


    def isSelected(self):
        return self.widget.__class__.selectedToolbars[self.name][0]