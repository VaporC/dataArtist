from pyqtgraph_karl.Qt import QtGui



class ChooseFileReaderDialog(QtGui.QDialog):
    '''
    If mutliple file readers are available for a given file type
    this dialog lets the user decide which one to take.
    '''
    index = 0


    def __init__(self, readers):
        QtGui.QDialog.__init__(self)
    
        labTxt = QtGui.QLabel(
        '''Multiple file reader are available for the chosen ftype:
(Hover for details)''')
        g = QtGui.QButtonGroup()

        l = QtGui.QVBoxLayout()
        self.setLayout(l)
        
        l.addWidget(labTxt)

        gl = QtGui.QGroupBox('Readers')
        l.addWidget(gl)

        b = QtGui.QPushButton('Done')
        b.clicked.connect(self.accept)
        l.addWidget(b)

        l = QtGui.QVBoxLayout()
        gl.setLayout(l)

        for n, r in enumerate(readers):
            btn = QtGui.QRadioButton(r.__name__)
            btn.clicked.connect(lambda checked, n=n: self.__setattr__('index',n))
            if r.__doc__ is not None:
                btn.setToolTip(r.__doc__)
            p = getattr(r, 'preferred', False)
            if p:
                btn.click()
            g.addButton(btn)
            l.addWidget(btn)
            
        g.setExclusive(True)