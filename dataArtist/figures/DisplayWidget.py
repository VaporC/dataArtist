import weakref

from dataArtist.widgets import  Toolbars



class DisplayWidget(object):
    '''
    Base class for all display.widget
    '''
    selectedToolbars = {}
    shows_one_layer_at_a_time = False
    
    def __init__(self, toolbars=None):
        self.tools = {}
        if toolbars is not None:
            self.toolbars = toolbars
        else:
            self.toolbars = Toolbars.build(weakref.proxy(self))


    def saveState(self):
        state={}
        state['toolbars'] = [t.isSelected() for t in self.toolbars]
        #tools
        state['tools'] = t = {}
        for name, tool in self.tools.iteritems():
            t[name] = tool.saveState()
        return state
        
        
    def restoreState(self, state):
        #toolbars
        for t,sel in zip(self.toolbars, state['toolbars']):
            t.setSelected(sel)
        #tools
        t = state['tools']
        for name, tool in self.tools.iteritems():
            try:
                tool.restoreState(t[name])
            except KeyError:
                pass