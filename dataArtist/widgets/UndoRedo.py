from pyqtgraph_karl.Qt import QtGui


     
class UndoRedo(QtGui.QWidget):
    '''
    Widget containing an undo and redo button + 
    tool-button menu to choose the current step in history
    '''
    
    def __init__(self, MEDIA_FOLDER):
        QtGui.QWidget.__init__(self)
        
        self.is_active = True
        self.max_hist_len = 5
        self._c = 0#count all added backups
        
        self.reset()
        self.setContentsMargins (0, 0, 0, 0)

        #HISTORY MENU
        self.menu = QtGui.QMenu()
        self.menu.aboutToShow.connect(self._showMenu)

        hl = QtGui.QHBoxLayout()
        hl.setContentsMargins (0, 0, 0, 0)

        self.setLayout(hl)

        icon_path = MEDIA_FOLDER.join("icons")
        
        #UNDO BUTTON
        self.btn_undo = QtGui.QToolButton()
        self.btn_undo.setAutoRaise(True)
        self.btn_undo.setToolTip('Undo')
        self.btn_undo.setIcon(QtGui.QIcon(icon_path.join('undo.svg')))
        self.btn_undo.setShortcut (QtGui.QKeySequence.Undo)
        self.btn_undo.clicked.connect(self.undo)
        self.btn_undo.setEnabled(False)
        
        #MENU BUTTON
        self.btn_menu = QtGui.QToolButton()
        self.btn_menu.setAutoRaise(True)
        self.btn_menu.setFixedWidth(9)
        self.btn_menu.setToolTip('Undo/Redo options')
        self.btn_menu.setMenu(self.menu)
        self.btn_menu.setPopupMode(QtGui.QToolButton.InstantPopup)
        
        self.menu_options = _MenuOptions()
        self.menu_options.activate.stateChanged.connect(self.setActive)
        
        action = QtGui.QWidgetAction(self)
        action.setDefaultWidget(self.menu_options)
        self.menu.addAction(action)      

        #REDO BUTTON
        self.btn_redo = QtGui.QToolButton()
        self.btn_redo.setAutoRaise(True)
        self.btn_redo.setToolTip('Redo')
        self.btn_redo.setIcon(QtGui.QIcon(icon_path.join('redo.svg')))
        self.btn_redo.clicked.connect(self.redo)
        self.btn_redo.setShortcut (QtGui.QKeySequence.Redo)
        self.btn_redo.setEnabled(False)

        hl.addWidget(self.btn_undo)
        hl.addWidget(self.btn_menu)
        hl.addWidget(self.btn_redo)


    def setActive(self, active):
        if not active:
            self.reset()
            self.cleanMenu()
            self.btn_undo.setEnabled(False)
            self.btn_redo.setEnabled(False)


    def reset(self):
        #step within undo/redo:
        self.position = 0
        #_list = list of (display, name, method)
        self._list = []
        #arguments to be captured before redo:
        self.data_args = []   


    def displayClosed(self, display):
        '''
        remove all undos/redos from the closed display
        '''
        for i in range(len(self._list)-1,-1,-1):
            if self._list[i][0] == display:
                self._list.pop(i)
        if len(self._list) == 0:
            self.btn_undo.setEnabled(False)
            self.btn_redo.setEnabled(False)
            

    def saveState(self):
        return {'activate': self.menu_options.activate.isChecked(),
                'lenHistory': self.menu_options.lenHistory.value()}
#         session.addContentToSave(l, 'undoRedo.txt')



    def restoreState(self, state):
#         l = eval(session.getSavedContent('undoRedo.txt'))
        self.menu_options.activate.setChecked(state['activate'])
        self.menu_options.lenHistory.setValue(state['lenHistory'])


    def cleanMenu(self):
        for a in self.menu.actions()[1:]:
            self.menu.removeAction(a)
         
            
    def _showMenu(self):#, point):
        #### current state <bold> and without connected action
        self.cleanMenu()
        if len(self._list):
            #build menu
            for n,r in enumerate(self._list):
                name = r[1]
                a = self.menu.addAction(name)
                if n < self.position:
                    #UNDO
                    dn = self.position - n
                    a.triggered.connect(
                        #execute undo n times:
                        lambda _, dn=dn: [self.undo() for _ in range(dn)])
                elif n > self.position:
                    #REDO
                    dn = n - self.position
                    a.triggered.connect(
                        #execute redo n times:
                        lambda _, dn=dn: [self.redo() for _ in range(dn)])
                else:
                    #CURRENT position
                    f = a.font()
                    f.setBold(True)
                    a.setFont(f)
            a = self.menu.addAction('Current')
            if self.position == len(self._list):
                f = a.font()
                f.setBold(True)
                a.setFont(f)
            else:
                dn = n +1 - self.position
                a.triggered.connect(
                        #execute redo n times:
                        lambda _, dn=dn: [self.redo() for _ in range(dn)])
                
    
    def isActive(self):
        return self.is_active and self.menu_options.activate.isChecked()
     
     
    def add(self, display, name, undoFn, redoFn, dataFn=None):  
        self._c += 1
        #remove all old redos:
        l = len(self._list)
        for n in range(l-1,self.position,-1):
            self._list.pop(n)                
        if l == self.menu_options.lenHistory.value():
            self._list.pop(0)
        
        self._list.append((display, '%s | %s' %(self._c,name), undoFn, redoFn, dataFn))
        
        self.btn_undo.setEnabled(True)
        self.btn_redo.setEnabled(False)

        self.position = len(self._list)


    def undo(self):
        #capture arg for redo
        current = False
        if self.position == len(self._list):
            #no undos done so far
            self.position -= 1
            current=True   
        data = self._list[self.position][4]
        if data:
            data = data()
        self.data_args.insert(0,data)
        #create redo
        self.btn_redo.setEnabled(True)

        #DO UNDO
        self.is_active = False
        self._list[self.position][2]()
        self.is_active = True
        
        if self.position > 0:
            if not current:
                self.position-=1
        else:
            self.btn_undo.setEnabled(False)
        self.is_active = True


    def redo(self):
        arg = self.data_args.pop(0)
        #DO REDO
        self.is_active = False
        fn = self._list[self.position][3]
        if arg is not None:
            fn(arg)
        else:
            fn()
        self.is_active = True

        self.btn_undo.setEnabled(True)
        if self.position == len(self._list)-1:
            self.btn_redo.setEnabled(False)
        if self.position < len(self._list):
            self.position += 1


     
class _MenuOptions(QtGui.QWidget): 
    '''
    Display last history steps and activate button
    '''
    def __init__(self):
        QtGui.QWidget.__init__(self)  
        
        l = QtGui.QVBoxLayout()
        self.setLayout(l)
        
        title = QtGui.QLabel('<b>Undo / Redo</b>')
        
        self.activate = QtGui.QCheckBox('Activate')
        self.activate.setChecked(True)
        
        self.activate.stateChanged.connect(self._enableLenHistory)

        self._label_lenHist = QtGui.QLabel('History Length')
        self.lenHistory = QtGui.QSpinBox()
        self.lenHistory.setRange(1, 100)
        self.lenHistory.setValue(5)
        
        l_history = QtGui.QHBoxLayout()
        l_history.addWidget(self._label_lenHist)
        l_history.addWidget(self.lenHistory)
        
        l.addWidget(title)
        l.addWidget(self.activate)
        l.addLayout(l_history)
        
        
    def _enableLenHistory(self, active):
        self._label_lenHist.setEnabled(active)
        self.lenHistory.setEnabled(active)