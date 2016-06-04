from pyqtgraph_karl.Qt import QtGui

from fancywidgets.pyqtgraphBased.parametertree import ParameterTree, Parameter



class ParameterMenu(QtGui.QMenu):
    '''
    A QMenu embedding a ParameterTree
    '''
    def __init__(self, tool):
        QtGui.QMenu.__init__(self, tool)
        #embed parameterTree as a QWidgetAction:
        a = QtGui.QWidgetAction(self)
        
        self.content = _MenuContent(tool)
        self.pTree = self.content.pTree
#         self.header = self.content.header

        a.setDefaultWidget(self.content)
        self.addAction(a)
        self.p = self.pTree.p

        self.p.opts['master'] = tool
        tool.param = self.p.param

        self.aboutToShow.connect(self.resizeToContent)

    
#     def save(self, session, path):
#         l = self.p.saveState()
#         session.addContentToSave(l, *path+('parameters.txt',))
# 
# 
#     def restore(self, session, path):
#         l =  eval(session.getSavedContent(*path +('parameters.txt',) ), 
#                   {'OrderedDict':OrderedDict})
#         self.p.restoreState(l)
    
    
    def resizeToContent(self):
        '''
        set a fixed minimum width and calculate the height from 
        the height of all rows
        '''
        width = 350
        heightMax = 600
        height = 6
        _iter = QtGui.QTreeWidgetItemIterator(self.pTree)
        while _iter.value():
            item = _iter.value()
            height +=self.pTree.visualItemRect(item).height()
            _iter += 1
        #limit height
        if height >= heightMax:
            height = heightMax   
        self.pTree.setMinimumSize(width,height)
        self.setMinimumSize(width,height+22)



class _MenuContent(QtGui.QWidget):
    '''
    Show: 
    Tool name - info sign  and activate button
    on top of the parameterTree
    '''
    
    def __init__(self, tool):
        QtGui.QWidget.__init__(self)

        l= QtGui.QVBoxLayout()
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(2)

        self.setLayout(l)
        
        self.header = header = QtGui.QHBoxLayout()
        header.setContentsMargins(5, 0, 5, 0)

        label = QtGui.QLabel('<b> %s</b>' %tool.__class__.__name__)

        self.pTree = _Parameters(tool)

        header.addWidget(label)
        doc = getattr(tool, '__doc__', None)
        if doc:
            doclabel = QtGui.QLabel('<i>   (?)</i>')
            doclabel.setToolTip (doc)
            header.addWidget(doclabel, stretch=1)

        if hasattr(tool, 'activate'):
            btn = QtGui.QPushButton('activate')
            btn.clicked.connect(tool.click)
            btn.setFixedHeight(15)
            btn.setFixedWidth(50)
            header.addWidget(btn)
 
        l.addLayout(header)
        l.addWidget(self.pTree)
        


class _Parameters(ParameterTree):

    def __init__(self, tool):
        self.p = Parameter.create(
                    name='', 
                    type='empty')
        ParameterTree.__init__(self, self.p)