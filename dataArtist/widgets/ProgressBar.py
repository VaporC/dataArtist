from pyqtgraph_karl.Qt import QtGui



class ProgressBar(QtGui.QWidget):
    '''
    A general propose procress bar 
    e.g. used when files are imported or tools are executed.
    '''
    
    def __init__(self, statusbar):
        QtGui.QWidget.__init__(self)
        
        self.statusbar = statusbar
        
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.bar = QtGui.QProgressBar()
        self.cancel = QtGui.QPushButton('Cancel')
        self.label = QtGui.QLabel()
        layout.addWidget(self.label)
        layout.addWidget(self.bar)
        layout.addWidget(self.cancel)
        self.statusbar.addPermanentWidget(self , stretch=1)
        
        self.hide()
        
        
    def show(self):
        self.statusbar.clearMessage()
        QtGui.QWidget.show(self)