#!/usr/bin/env python

import sys 
import os


from pyqtgraph_karl.Qt import QtGui, QtCore

#FIXME: many array indices in pyqtgraph are not int
#therefore numpy 1.11 shows many VisibleDeprecationWarning...
import warnings
warnings.simplefilter("ignore", DeprecationWarning)

from appbase.MultiWorkspaceWindow import MultiWorkspaceWindow
from appbase.Application import Application
from fancytools.os.PathStr import PathStr
# from interactiveTutorial.TutorialMenu import TutorialMenu

#OWN
import dataArtist
from dataArtist.input.html2data import html2data
from dataArtist.widgets.preferences \
        import PreferencesView, PreferencesImport, PreferencesCommunication
from dataArtist.widgets.Workspace import Workspace
from dataArtist.widgets.UndoRedo import UndoRedo
from dataArtist.widgets.ProgressBar import ProgressBar
from dataArtist.widgets.dialogs.FirstStartDialog import FirstStartDialog
from dataArtist.widgets.GlobalTools import GlobalTools
from dataArtist.widgets.StatusBar import StatusBar


##########
#to allow to execute py code from a frozen environment
#type e.g. gui.exe -exec print(4+4)
if '-exec' in sys.argv:
    try:
        exec(sys.argv[-1])
    except Exception, err:
        raw_input('-exec failed! --> %s' %err)
    sys.exit()
##########


MEDIA_FOLDER = PathStr(dataArtist.__file__).dirname().join('media')
HELP_FILE = MEDIA_FOLDER.join('USER_MANUAL.pdf')


def _showActionToolTipInMenu(menu, action):
    #show tooltip on the right side of [menu]
    ###QMenu normaly doesnt allow QActions to show tooltips...
    tip = action.toolTip()
#             QtGui.QToolTip.showText(QtGui.QCursor.pos(), tip)
    p = menu.pos()
    p.setX(p.x()+105)
    p.setY(p.y()-21)
    if tip != action.text():
        QtGui.QToolTip.showText(p, tip)


class Gui(MultiWorkspaceWindow):
    '''
    The main class to be called to create an instance of dataArtist
    '''
    def __init__(self, title='dataArtist'):
        MultiWorkspaceWindow.__init__(self, Workspace, title)

        s = self.app.session
        self.resize(605,550)
        #ALLOW DRAGnDROP        
        self.setAcceptDrops(True)
        #INIT CHILD PARTS:
        self.dialogs = s.dialogs
        self.pref_import = PreferencesImport(self)
        
        self._appendMenubarAndPreferences()
        #CONNECT OWN SAVE/RESTORE FUNCTIONS TO THE SESSION:
        s.sigSave.connect(self._save)
        s.sigRestore.connect(self._restore)
        st = StatusBar()
        self.setStatusBar(st)
    
#         def showOut(msg):
#             if msg != '\n':
#                 # after every message this new line character is emitted 
#                 # showing this hides the real message
#                 st.showMessage(msg,9000)
#         def showErr(msg):
#             if msg != '\n':
#                 st.showError(msg, 9000)
        s.streamOut.message.connect(st.showMessage)#showOut)
        s.streamErr.message.connect(st.showError)#showErr)

        self.framelessDisplays = {} # contain all displays that are unbounded 
                                    # from the main window and showed frameless

        self.addWorkspace()
        #PROGRESS BAR:
        self.progressBar = ProgressBar(st)
        st.setSizeGripEnabled(False)


    def isEmpty(self):
        return ( self.centralWidget().count()==1 
                and not self.currentWorkspace().displays() )


    def _save(self, state):
        state['gui'] = self.saveState()
    
    
    def _restore(self, state):
        return self.restoreState(state['gui'])

    def saveState(self):
        l = {}
        i = self.size()
        l['size'] = (i.width(),i.height()) 
        c = self.centralWidget()
        l['nWorkspaces'] = c.count()
        l['currentWorkspace'] = c.indexOf(self.currentWorkspace())
        l['maximized'] = self.isMaximized()
        l['fullscreen'] = self.menuBar().ckBox_fullscreen.isChecked()
        l['showTools'] = self.menu_toolbars.a_show.isChecked()
#         session.addContentToSave(l, 'gui.txt')
        #WORKSPACES
        sw = l['workspaces'] = {}
        for w in self.workspaces():
            sw[w.number()] = w.saveState()
        
        l['undoRedo'] = self.undoRedo.saveState()
        return l
    
                    
    def restoreState(self, l):
        self.resize(*l['size'])  
        self.menuBar().setFullscreen(l['fullscreen'])
        if l['maximized']:
            self.showMaximized()
        else:
            self.showNormal()
        #WORKSPACES
        c = self.centralWidget()
        n = l['nWorkspaces']
            #CLOSE OLD:
        for w in self.workspaces():
            self.closeWorkspace(w)
            #ADD NEW:
        for _ in range(n - c.count()):
            self.addWorkspace()
            #RESTORE:
        self.showWorkspace(l['currentWorkspace'])  
        lw = l['workspaces']
        for number, w in zip(lw, self.workspaces()):
            w.restoreState(lw[number])
            
        self.menu_toolbars.a_show.setChecked(l['showTools'])
        self._toggleShowSelectedToolbars(l['showTools'])
        
        self.undoRedo.restoreState(l['undoRedo'])

    
    def addFilePath(self, filepath):
        '''
        create a new display for one ore more given file paths
        '''
        if filepath:
            return self.currentWorkspace().addFiles([PathStr(filepath)])


    def openFile(self):
        '''
        create a new display for one ore more  files 
        '''
        filepaths = self.dialogs.getOpenFileNames()
        if filepaths:
            return self.currentWorkspace().addFiles(filepaths)

  
    def showDisplay(self, arg):
        '''
        show display as frame-less window 
        '[displaynumber], [area]' = (x,y,width,height)
        '''
        displaynumber,pos = eval(arg)
        if not pos:
            return self.hideDisplay(displaynumber)
        else:
            (x,y,width,height) = pos
        d = self.framelessDisplays.get(displaynumber,None)
        if not d:
            try:
                d = self.currentWorkspace().displaydict()[displaynumber]
                d.release()
                d.hideTitleBar()
                d.setWindowFlags(QtCore.Qt.FramelessWindowHint | 
                                 QtCore.Qt.WindowStaysOnTopHint)
                self.framelessDisplays[displaynumber] = d
            except KeyError:
                print('displaynumber [%s] not known' %displaynumber)
                return
        d.move(QtCore.QPoint(x,y))
        d.resize(width, height)
        d.show()


    def hideDisplay(self, displaynumber):
        '''
        close frame-less display
        [displaynumber]
        '''
        d = self.framelessDisplays.pop(displaynumber,None)
        if d:
            d.showTitleBar()
            d.embedd()
        else:
            print('displaynumber [%s] not known' %displaynumber) 
 
 
    def runScriptFromName(self, name):
        '''
        run a console script identified by name
        in the current display 
        '''
        w = self.currentWorkspace().getCurrentDisplay(
                                ).tab.automation.tabs.widgetByName(name)
        if not w:
            raise Exception('couldnt find script [%s] in the current display' %name)
        w.thread.start()
    
    
    def _appendMenubarAndPreferences(self):
        m = self.menuBar()
        m.setFixedHeight(25)
#         m.setMaximumHeight(25)

        m.aboutWidget.setModule(dataArtist)
        m.aboutWidget.setInstitutionLogo(MEDIA_FOLDER.join('institution_logo.svg'))
        
        #hide the menu so toolbars can only be show/hidden via gui->view->toolbars:
        m.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)

        self.undoRedo = UndoRedo(MEDIA_FOLDER)

        self.gTools = GlobalTools()
        self.gTools.addWidget(self.undoRedo)

        m.setCornerWidget(self.gTools)
        
        #APPEND PREFERENCES
        t = m.file_preferences.tabs        
        t.addTab(PreferencesView(self), 'View')
        t.addTab(self.pref_import, 'Import')
        t.addTab(PreferencesCommunication(self), 'Communication')
        #APPEND MENUBAR
            #MENU - FILE
        f = m.menu_file
        p = f.action_preferences 
        action_file = QtGui.QAction('&Import', f)
        action_file.triggered.connect(self.openFile)
        action_file.setShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_I))
        f.insertAction(p,action_file)
        f.insertSeparator(p)
            #MENU VIEW
        v = m.menu_view
                #ACTION PRINT VIEW
        aPrintView = QtGui.QAction('Print view', v)
        aPrintView.setCheckable(True)
        aPrintView.triggered.connect(
                lambda checked: self.currentWorkspace().setPrintView(checked) ) 
        v.addAction(aPrintView)
                
                #SHOW/HIDE history
        aHistory = QtGui.QAction('Program history', v)
        aHistory.setShortcut(QtCore.Qt.Key_F4)

        aHistory.setCheckable(True)     
        
        def showhideHistory(checked):
            s = self.currentWorkspace().middle_splitter
            r = s.getRange(1)[1]
            if checked:
                r/= 1.5
            return s.moveSplitter(r,1)
        
        def isHistoryVisible():
            s = self.currentWorkspace().middle_splitter
            aHistory.setChecked(s.sizes()[1] != 0)
                
        aHistory.triggered.connect(showhideHistory) 
        v.aboutToShow.connect(isHistoryVisible)
        v.addAction(aHistory)     
               
                #SHOW/HIDE preferences
        aPref= QtGui.QAction('Dock preferences', v)
        aPref.setShortcut(QtCore.Qt.Key_F3)
        aPref.setCheckable(True)     
        
        def showhidePref(checked):
            s = self.currentWorkspace().vert_splitter
            r = s.getRange(1)[1]
            if checked:
                r/= 3
            else:
                r = 0
            return s.moveSplitter(r,1)
        
        def isPrefVisible():
            w = self.currentWorkspace()
            s = w.vert_splitter
            aPref.setChecked(s.sizes()[0]!=0)
            aPref.setEnabled(w.displayPrefTabs.isVisible())
                
        aPref.triggered.connect(showhidePref) 
        v.aboutToShow.connect(isPrefVisible)
        v.addAction(aPref)  

                #ACTION VIEW2CLIPBOARD
        aClipboard = QtGui.QAction('Copy view to clipboard', v)
        aClipboard.triggered.connect(
                lambda checked: self.currentWorkspace().copyViewToClipboard() ) 
        v.addAction(aClipboard)
                #ACTION Display2CLIPBOARD
        aClipboard = QtGui.QAction('Copy active display to clipboard', v)
        aClipboard.triggered.connect(
                lambda checked: self.currentWorkspace().copyCurrentDisplayToClipboard() ) 
        v.addAction(aClipboard)
            #MENU - TOOLS   
        t = m.menu_tools = QtGui.QMenu('Dock')
        m.insertMenuBefore(m.menu_workspace, t)
            #ADD DISPLAY
        mDisplay = t.addMenu('Add Display')
        for i, name in ( #(1, 'Dot'), 
                         (2, 'Graph'), 
                         (3, 'Image/Video'),
                         #(4, 'Surface')
                         #TODO: 
                         #(4, 'TODO: Surface'), 
                         #(5, 'TODO: Volume') 
                         ):
                mDisplay.addAction('%sD - %s' %(i-1, name)).triggered.connect(
                        lambda checked, i=i: self.currentWorkspace().addDisplay(axes=i) )
            #ADD TABLE
        t.addAction('Add Table').triggered.connect(
                lambda: self.currentWorkspace().addTableDock() ) 
            #ADD NOTEPAD
        t.addAction('Add Notepad').triggered.connect(
                lambda: self.currentWorkspace().addTextDock() ) 
        t.addSeparator()
        #DUPLICATE CURRENT DOCK
        t.addAction('Duplicate current display').triggered.connect(
                self._duplicateCurrentDiplay ) 
        self._m_duplDisp = t.addMenu('Move current display to other workspace')
        self._m_duplDisp.aboutToShow.connect(self._fillMenuDuplicateToOtherWS ) 
            #MENU - TOOLBARS                
        self.menu_toolbars = QtGui.QMenu('Toolbars', m)
        self.connect(self.menu_toolbars, QtCore.SIGNAL("hovered(QAction *)"),
                     lambda action, m=self.menu_toolbars: 
                        _showActionToolTipInMenu(m, action))
        
            #SHOW ALL TOOLBARS - ACTION
        a = self.menu_toolbars.a_show = QtGui.QAction('show', m)
        f = a.font()
        f.setBold(True)   
        a.setFont(f)
        a.setCheckable(True)
        a.setChecked(True)
        a.triggered.connect(self._toggleShowSelectedToolbars)

        self.menu_toolbars.aboutToShow.connect(self._listToolbarsInMenu)
        m.insertMenuBefore( m.menu_workspace, self.menu_toolbars)       
            #MENU HELP
        m.menu_help.addAction('User manual').triggered.connect(
            lambda checked: os.startfile(HELP_FILE))
            #TUTORIALS
        ####not used at the moment
#         self.m_tutorials = TutorialMenu(
#                         tutorialFolder=PathStr.getcwd('dataArtist').join('tutorials'), 
#                         openFunction=self._openFnForTutorial,
#                         saveFunction=self.app.session.blockingSave)
#         m.menu_help.addMenu(self.m_tutorials)

        m.menu_help.addAction('Online tutorials').triggered.connect(
            lambda checked: os.startfile(
            'http://www.youtube.com/channel/UCjjngrC3jPdx1HL8zJ8yqLQ'))
        m.menu_help.addAction('Support').triggered.connect(
            lambda checked: os.startfile(
            'https://github.com/radjkarl/dataArtist/issues'))        
        
        
    def _duplicateCurrentDiplay(self):
        d = self.currentWorkspace().getCurrentDisplay()
        if not d:
            raise Exception('no display chosen')
        d.duplicate()


    def _moveCurrentDiplayToWorkspace(self, i):
        w = self.currentWorkspace()
        ws = self.workspaces(i)
        w.moveCurrentDisplayToOtherWorkspace(ws)


    def _fillMenuDuplicateToOtherWS(self):
        c = self.centralWidget()
        self._m_duplDisp.clear()
        for i in range(c.count()):
            if i != c.currentIndex():
                t = '[%s]'%str(i+1)
                a = QtGui.QAction(t, self._m_duplDisp)
                a.triggered.connect(lambda clicked, i=i, self=self: 
                        self._moveCurrentDiplayToWorkspace(i))
                self._m_duplDisp.addAction(a)


    def _openFnForTutorial(self, path):
        self.app.session.setSessionPath(path) 
        self.app.session.restoreCurrentState()
  

    def _listToolbarsInMenu(self):        
        m = self.menu_toolbars
        #REMOVE OLD:
        m.clear()
        m.addAction(m.a_show)
        if m.a_show.isChecked():
            self.currentWorkspace().addShowToolBarAction(m)
            

        
    def _toggleShowSelectedToolbars(self, checked):
        self.currentWorkspace().toggleShowSelectedToolbars(checked)

                
    #DRAG AND GROP
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Paste):
            self.dropEvent(QtGui.QApplication.clipboard())
            
            
    def dragEnterEvent(self, event):
        m = event.mimeData()
        if (m.hasUrls() or 
            m.hasImage() or
            m.hasText() ):
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()


    def _getFilePathsFromUrls(self, urls):
        '''
        return a list of all file paths in event.mimeData.urls()
        '''
        l = []
        def _appendRecursive(path):
            if path.isfile():
                #file
                l.append(path)
            else:
                for f in path:
                    #for all files in folder
                    _appendRecursive(path.join(f))
        # one or more files/folders are dropped
        for url in urls:
            if url.isLocalFile():
                path = PathStr(url.toLocalFile().toLocal8Bit().data())
                if path.exists():
                    _appendRecursive(path)
        return l


    def dropEvent(self, event):
        '''what to do is sth. if dropped'''
        m = event.mimeData()
        
        #HTML CONTENT        
        if m.hasHtml():
            (paths, data) = html2data(unicode(m.html()))
            self.currentWorkspace().addFiles(paths)
            #raise NotImplementedError('direct import of data (like tables) from a browser is not implemented at the moment')
        
        #FILES
        elif m.hasUrls():
            paths =  self._getFilePathsFromUrls(m.urls())
            #filter from session files and open those:
            i  = 0
            while i < len(paths):
                p = paths[i]
                #DATAARTIST SESSION
                if p.endswith(self.app.session.FTYPE):
                    if self.isEmpty():
                        self.app.session.replace(p)
                    else:
                        self.app.session.new(p)
                    paths.pop(i)
                else:
                    i += 1
            
            self.currentWorkspace().addFiles(paths)
        
        #TEXT/TABLES
        if m.hasText():
            txt = unicode(m.text())
            if self.txtIsTable(txt):
                self.currentWorkspace().addTableDock(text=txt)
            else:
                self.currentWorkspace().addTextDock(text=txt)
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


    @staticmethod
    def txtIsTable(txt):
        # for now just a simple check whether there is at least 
        # on tab sign in the first line
        return txt[:txt.find('\n')].count('\t') > 0
        


def main(name='dataArtist', 
         ftype='da', 
         first_start_dialog=FirstStartDialog, 
         icon=None):
    '''
    General start routine
    Create a QApplication and Gui instance
    '''
    if icon is None:
        icon = MEDIA_FOLDER.join('logo.svg')
    
    app = Application(sys.argv, 
                      name=name, 
                      ftype=ftype, 
                      icon=icon,
                      first_start_dialog=first_start_dialog)
    app.setStyle("Plastique") #looks better and shows splitter handle

    win = Gui(title=name)
    s = app.session
    s.registerMainWindow(win)
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()