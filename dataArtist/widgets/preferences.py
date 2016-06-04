'''
Widgets handling all dataArtist preferences
'''

from pyqtgraph_karl.Qt import QtGui, QtCore
import pyqtgraph_karl

from dataArtist.components.RabbitMQServer import RabbitMQServer
from dataArtist.components.WatchFolder import WatchFolder



class PreferencesCommunication(QtGui.QWidget):
    '''
    Preferences for communication between dataArtist and other programs
     - this is at the moment done using a RabbitMQ server
    '''
    def __init__(self, gui):
        QtGui.QWidget.__init__(self)  

        self.gui = gui
        
        rab = self.rabbitMQServer = RabbitMQServer(gui)
        self._wf = wf = WatchFolder(gui)

        s = gui.app.session
        #CONNECT SAVE/RESTORE:
        s.sigSave.connect(self._save)
        s.sigRestore.connect(self._restore)  
        #CONNECT CLOSE
        gui.app.lastWindowClosed.connect(
                rab.stop)

        #LAYOUT:
        layout = QtGui.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

        #WATCH FOLDER
        #############
        self.cb_watchFolder = QtGui.QCheckBox('Watch folder')
        self.cb_watchFolder.toggled.connect(self._watchFolderChanged)
        layout.addWidget( self.cb_watchFolder )
        
        self._folder_opts = QtGui.QWidget()
        layout.addWidget(self._folder_opts)
        gl = QtGui.QGridLayout()
        self._folder_opts.setLayout(gl)
        self._folder_opts.hide()

        self._wf_folderEdit = QtGui.QLineEdit('-')
        self._wf_folderEdit.setReadOnly(True)
        gl.addWidget(self._wf_folderEdit, 0,0)
        btn = QtGui.QPushButton('Change')
        btn.clicked.connect(self._wf_folderChanged)
        gl.addWidget(btn, 0,1)
        
        self._cb_filesOnly = QtGui.QCheckBox('Files only')
        self._cb_filesOnly.setChecked(wf.opts['files only'])
        self.cb_watchFolder.toggled.connect(lambda val: 
                                wf.opts.__setitem__('files only', val))
        gl.addWidget(self._cb_filesOnly,1,0 )

        gl.addWidget(QtGui.QLabel('refreshrate [msec]'), 2,0)
        self._wf_refRate = QtGui.QSpinBox()
        self._wf_refRate.setRange(1,100000)
        self._wf_refRate.setValue(wf.opts['refreshrate'])
        self._wf_refRate.valueChanged.connect(self._wf_refRateChanged)
        gl.addWidget(self._wf_refRate, 2,1)       

        #RABBIT MQ
        ##########
        hlayout = QtGui.QHBoxLayout()
        layout.addLayout(hlayout)
        
        self.cb_allowRabbit = QtGui.QCheckBox('Allow inter-process communication\nusing the RabbitMQ server')
        self.cb_allowRabbit.toggled.connect(self._allowRabbitMQchanged)
        hlayout.addWidget( self.cb_allowRabbit )

        self.cb_confirm = QtGui.QCheckBox('Confirm received messages')
        self.cb_confirm.hide()
        self.cb_confirm.setChecked(rab.opts['corfirmPosts'])
        self.cb_confirm.toggled .connect(lambda val: rab.opts.__setitem__(
                                                    'corfirmPosts', val) )
        hlayout.addWidget( self.cb_confirm )

        self._rab_opts = QtGui.QWidget()
        layout.addWidget(self._rab_opts)
        gl = QtGui.QGridLayout()
        self._rab_opts.setLayout(gl)
        self._rab_opts.hide()
        
        gl.addWidget(QtGui.QLabel('refreshrate [msec]'), 0,0)
        self._rab_refRate = QtGui.QSpinBox()
        self._rab_refRate.setRange(1,1000)
        self._rab_refRate.setValue(rab.opts['refreshrate'])
        self._rab_refRate.valueChanged.connect(lambda val: rab.opts.__setitem__(
                                                    'refreshrate', val) )
        gl.addWidget(self._rab_refRate, 0,1)

        gl.addWidget(QtGui.QLabel('host'), 1,0)
        self.le_host = QtGui.QLineEdit()
        self.le_host.setText(rab.opts['host'])
        self.le_host.textChanged.connect(lambda val: 
                                rab.opts.__setitem__('host', val) )
        gl.addWidget(self.le_host, 1,1)
        
        gl.addWidget(QtGui.QLabel('timeout [msec]'), 2,0)
        self.sb_timeout = QtGui.QSpinBox()
        self.sb_timeout.setRange(0,1000)
        self.sb_timeout.setValue(rab.opts['timeout'])
        self.sb_timeout.valueChanged.connect(lambda val: 
                                rab.opts.__setitem__('timeout', val) )
        gl.addWidget(self.sb_timeout, 2,1)

        gl.addWidget(QtGui.QLabel('<b>....listen to queues named:</b>'), 3,0)
        for n, (queue, action) in enumerate(rab.listenTo.iteritems()):
            gl.addWidget(QtGui.QLabel(queue), 4+n,0)
            gl.addWidget(QtGui.QLabel(action.__doc__), 4+n,1)
 


    def _watchFolderChanged(self, checked):
        self._folder_opts.setVisible(checked)
        if checked and self._wf_folderEdit.text() != '-':
            self._wf.start()
        else:
            self._wf.stop()
      
      
    def _wf_refRateChanged(self, rate):
        self._wf.opts['refreshrate']
        self._wf.stop()
        self._wf.start()
        
        
    def _wf_folderChanged(self):
        t = self._wf_folderEdit.text()
        kwargs = {}
        if t != '-':
            kwargs['directory'] = t
        f = self.gui.dialogs.getExistingDirectory(**kwargs)
        if f:
            self._wf.opts['folder'] = f
            self._wf_folderEdit.setText(f)
            self._wf.stop()
            self._wf.start()            


    def _allowRabbitMQchanged(self, checked):
        if checked:
            try:
                self.rabbitMQServer.start()
            except Exception, err:
                #maybe rabbitMQ is not installed
                self._errm = QtGui.QErrorMessage() #needs to assign to self, otherwise garbage collected
                self._errm.showMessage(str(err))
                self.cb_allowRabbit.setChecked(False)
                self.cb_allowRabbit.setEnabled(False)
                return     
        else:
            self.rabbitMQServer.stop()        
        self._rab_opts.setVisible(checked)
        self.cb_confirm.setVisible(checked)
        self.adjustSize()


    def _save(self, state):
        #TODO: add server.opts.[activated]
        #TODO: only save server.opts
        #TODO. create def update to read from server.opts
#         session.addContentToSave({
        state['pcommunication'] = {
            'WatchFolderOpts': self._wf.opts,        
                                  
            'RMQ_refreshRate':self._rab_refRate.value(),
            'RMQ_host':str(self.le_host.text()),
            'RMQ_timeout':self.sb_timeout.value(),
            'RMQ_activated':self.cb_allowRabbit.isChecked(),
            'RMQ_confirmPosts':self.cb_confirm.isChecked(),
                                }
        
            
    def _restore(self, state):
        l = state['pcommunication']

        wf = l['WatchFolderOpts']
        self._wf_refRate.setValue(wf['refreshrate'])
        self._cb_filesOnly.setChecked(wf['files only'])
        self._wf_folderEdit.setText(wf['folder'])
        
        self._rab_refRate.setValue(l['RMQ_refreshRate'])
        self.le_host.setText(l['RMQ_host'])
        self.sb_timeout.setValue(l['RMQ_timeout'])
        self.cb_confirm.setChecked(l['RMQ_confirmPosts'])
        self.cb_allowRabbit.setChecked(l['RMQ_activated'])



class ChooseProfile(QtGui.QWidget):
    def __init__(self, session):
        QtGui.QWidget.__init__(self) 

        lab = QtGui.QLabel('Profile:')
        tt = '''The chosen profile influences the visibility of tool bars.
Changes are only effective after restarting the program.'''
        lab.setToolTip(tt)
        
        cb = QtGui.QComboBox()
        cb.setToolTip(tt)
        items = ( 'simple', 'electroluminescence')
        cb.addItems(items)
        try:
            cb.setCurrentIndex(items.index(session.app_opts['profile']))
        except KeyError:
            session.app_opts['profile'] = 'simple'
            pass
        cb.currentIndexChanged.connect(lambda i:
                                session.app_opts.__setitem__(
                                'profile', str(cb.currentText())))
        
        l = QtGui.QHBoxLayout()
        self.setLayout(l)
        
        l.addWidget(lab)
        l.addWidget(cb)



class PreferencesView(QtGui.QWidget):
    '''
    General view preferences, like the colour theme
    '''
    def __init__(self, gui):
        #TODO: make pyqtgraph optics(colortheme...) directly changeable - not just
        #      at reload
        QtGui.QWidget.__init__(self) 
        self.gui = gui
        session = gui.app.session
        #CONNECT SAVE/RESTORE:
        session.sigSave.connect(self._save)
        session.sigRestore.connect(self._restore)
        #LAYOUT:
        layout = QtGui.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

        hlayout = QtGui.QHBoxLayout()
        layout.addLayout(hlayout)
        self.label_colorTheme = QtGui.QLabel('Color theme') 
        hlayout.addWidget(self.label_colorTheme)
         
        self.combo_colorTheme = QtGui.QComboBox()
        hlayout.addWidget(self.combo_colorTheme)
        self.combo_colorTheme.addItems(( 'dark', 'bright'))
        self.combo_colorTheme.currentIndexChanged.connect(lambda i, self=self: 
                                self.setColorTheme(self.combo_colorTheme.currentText()))
        
        self.check_antialiasting = QtGui.QCheckBox('Antialiasting')
        layout.addWidget(self.check_antialiasting)
        self.check_antialiasting.stateChanged.connect(self._setAntialiasting)

        combo_profile = ChooseProfile(session)
        layout.addWidget(combo_profile)


    def _setAntialiasting(self, val):
        pyqtgraph_karl.setConfigOption('antialias', bool(val))
        for ws in self.gui.workspaces():
            ws.reload()


    def _save(self, state):
        state['pview'] = {
                    'colorTheme':self.combo_colorTheme.currentIndex()}

            
    def _restore(self, state):
        self.combo_colorTheme.setCurrentIndex(state['pview']['colorTheme'])


    def setColorTheme(self, theme):
        if theme == 'dark':
            pyqtgraph_karl.setConfigOption('foreground', 'w')
            pyqtgraph_karl.setConfigOption('background', 'k')
            
        elif theme == "bright":
            pyqtgraph_karl.setConfigOption('foreground', 'k')
            pyqtgraph_karl.setConfigOption('background', 'w')
        else:
            raise AttributeError('theme %s unknown' %theme)
        
        for ws in self.gui.workspaces():
            ws.reload()
#             for d in ws.displays():#doesn't acknowledge tools prefs
#                 d.reloadWidget()


class PreferencesImport(QtGui.QWidget):
    '''
    Preferences for importing files
    '''
    separated = 0
    together = 1
    inCurrentDisplay = 2
    inImportDisplay = 3
    importFilesPolicy = together
    showImportDialog = True
    loadImportedFiles = True
    
    def __init__(self, gui):
        QtGui.QWidget.__init__(self)
        self.gui = gui
        #CONNECT SAVE/RESTORE:
        gui.app.session.sigSave.connect(self._save)
        gui.app.session.sigRestore.connect(self._restore)
        #LAYOUT:
        layout = QtGui.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

        hlayout = QtGui.QHBoxLayout()
        layout.addLayout(hlayout)
        self.label_multifiles = QtGui.QLabel('Import multiple files') 
        hlayout.addWidget(self.label_multifiles)
        
        self.combo_import = QtGui.QComboBox()
        hlayout.addWidget(self.combo_import)
        self.combo_import.addItems(( 'separated', 'together',
                                     'in current display',
                                     'in import display'))
        self.combo_import.setCurrentIndex(self.importFilesPolicy)
        self.combo_import.currentIndexChanged.connect(self._importChanged)

        self.btn_loadFiles = QtGui.QCheckBox('load files')
        self.btn_loadFiles.setChecked(True)
        self.btn_loadFiles.toggled.connect(
            lambda checked, self=self: self.__setattr__(
                                    'loadImportedFiles', checked) )
        layout.addWidget(self.btn_loadFiles)

        self.btn_ask = QtGui.QCheckBox('Show import dialog')
        self.btn_ask.setChecked(self.showImportDialog)
        self.btn_ask.toggled.connect(
            lambda checked, self=self: self.__setattr__(
                                    'showImportDialog', checked) )
        layout.addWidget(self.btn_ask)


    def _importChanged(self, index):
        self.importFilesPolicy = index
        w = self.gui.currentWorkspace()
        if index == self.inImportDisplay:
            w.setCurrentDisplayToImportDisplay()   
        else:
            w.unsetImportDisplay()


    def _save(self, state):
        state['pimport'] = {
#         session.addContentToSave({
            'importOption':self.combo_import.currentIndex(),
            'loadFiles':self.btn_loadFiles.isChecked(),
            'showDialog':self.btn_ask.isChecked()}
#         , 'preferences','import.txt')

            
    def _restore(self, state):
        l =  state['pimport']#eval(session.getSavedContent('preferences','import.txt'))
        self.combo_import.setCurrentIndex(l['importOption'])
        self.btn_loadFiles.setChecked(l['loadFiles'])
        self.btn_ask.setChecked(l['showDialog'])


    def updateSettings(self, pref):
        '''
        update all setting to the given instance
        '''
        pref.combo_import.setCurrentIndex(
                    self.combo_import.currentIndex() )
        #pref.showImportDialog = self.related.btn_ask.isChecked()
        pref.btn_ask.setChecked(self.showImportDialog)
        #self.loadImportedFiles = self.related.btn_loadFiles.isChecked()
        pref.btn_loadFiles.setChecked(self.loadImportedFiles)