from fancywidgets.pyqtgraphBased.DockArea import DockArea

from pyqtgraph_karl.Qt import QtGui


class MiddleDockArea(DockArea):
    '''
    Main area of the gui which shows some text 
    when there are no displays
    '''
    
    def __init__(self, max_docks_xy=(2,2), *args, **kwargs):
        DockArea.__init__(self,  max_docks_xy, *args, **kwargs)
        
        self.text = QtGui.QLabel('''<html>
            <p>Just <strong>drag and drop</strong> ...</p>
        <p> &nbsp;</p><ul>
            <li>one or more <strong>files </strong>or <strong>folders</strong></li>
            <li><strong>number-fields</strong> from clipboard</li>
            <li><strong>images </strong>from clipboard</li>
        </ul><p>&nbsp;</p> <p>
            over this area to open it</p></html>''')
        self.layout.addWidget(self.text,  stretch=1)
        
          
    def addDock(self, dock, *args, **kwargs):
        self.text.hide()
        return DockArea.addDock(self, dock, *args, **kwargs)