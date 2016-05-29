from pyqtgraph_karl.Qt import QtGui, QtCore



class StatusBar(QtGui.QStatusBar):
    def __init__(self):
        QtGui.QStatusBar.__init__(self)
        
        #do not resize mainWindow when a longer message is displayed:
        self.setMinimumWidth(2)
        self.setFixedHeight(self.sizeHint().height()+5)
        l = self.layout()
        l.setSpacing(0)
        l.setContentsMargins(0, 0, 0, 0)
        
        #QLabel displaying error messages:
        self._errLabel = QtGui.QLabel()
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground,QtCore.Qt.red)
        self._errLabel.setPalette(palette)
        #respective timer for that label:
        self._error_timer = QtCore.QTimer()
        self._error_timer.setSingleShot(True)
        self._error_timer.timeout.connect(self._errLabel.hide)
        
        
    def showError(self, msg, time_ms):
        '''
        Show error message in red color
        '''
        ###limit size otherwise gui would be resized:
        self.clearMessage()
        
        #if error message starts with something like C:\...[file].py - remove that 
        #to only show the important info here:
#         i = msg.indexOf('.py:')
#         if i != -1:
#             msg = msg[i+5:]
            
        msg = msg[:-1] #remove \n
            
        self._errLabel.setText(msg)#[:50])
        
        self._error_timer.stop()
        self._error_timer.setInterval(time_ms)
        self._error_timer.start()
        
        self.addWidget(self._errLabel, stretch=1)
        self._errLabel.show()