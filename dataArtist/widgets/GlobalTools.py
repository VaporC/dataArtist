from pyqtgraph_karl.Qt import QtGui


class GlobalTools(QtGui.QWidget):
    '''
    Widget containing all global tools
    '''

    def __init__(self):
        QtGui.QWidget.__init__(self)
        l = QtGui.QHBoxLayout()
        self.setLayout(l)
        l.setContentsMargins(0, 0, 0, 0)   
        l.setSpacing(0) 
        l.setDirection(QtGui.QBoxLayout.RightToLeft)
        
           
    def addWidget(self, w):
        self.layout().addWidget(w)
        #need to update size, otherwise first widget is displayed too small:
        p = self.parent()
        if p:
            p.adjustSize()


    def __iter__(self):
        '''
        return iterator containing all containing widgets
        '''
        l = self.layout()
        return (l.itemAt(i).widget() for i in range(l.count()))   