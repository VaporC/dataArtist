from fancywidgets.pyqtgraphBased.Dock import Dock

from fancywidgets.pyQtBased.Table import Table
from fancywidgets.pyQtBased.FwMinimalTextEditor import FwMinimalTextEditor



class DockBase(Dock):
    
    def close(self):
        Dock.close(self)
        #Show text when all docks are closed  
        if not self.area.docks:
            self.area.text.show()


    
class DockTable(DockBase):
    '''create dock from table'''
    def __init__(self, name='unnamed table', text=None, *args, **kwargs):
        Dock.__init__(self, name, *args, **kwargs) 
        
        if text is not None:
            t = Table.fromText(text)
        else: 
            t = Table()
        self.addWidget(t)  



class DockTextEditor(DockBase):
    '''create dock from textEditor'''
    def __init__(self, name='unnamed text', text=None, *args, **kwargs):
        Dock.__init__(self, name, *args, **kwargs)  
        
        t = FwMinimalTextEditor()
        if text is not None:
            t.text.setText(text)
        self.addWidget(t)  