from pyqtgraph_karl.Qt import QtCore
from fancytools.os.PathStr import PathStr



class WatchFolder(object):
    '''
    Auto-import new files/folders in a directory into dataArtist
    after activation.
    '''
    def __init__(self, gui):
        self.gui = gui
        self.timer = None
        
        self.opts = {'refreshrate':1000, #ms
                     'folder':'.',
                     'files only':True
                     }


    def start(self):
        '''
        configure the server and check the 
        message-inbox every self.opts['refeshrate']
        '''
        self._files = PathStr(self.opts['folder']).listdir()
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.checkFolder)
        self.timer.start(self.opts['refreshrate'])


    def stop(self):
        if self.timer is not None and self.timer.isActive():
            self.timer.stop()


    def checkFolder(self):
        '''
        Check for new files/folders in self.opts['folder']
        and import them into dataArtist
        '''
        fo = PathStr(self.opts['folder'])
        o = self.opts['files only']
        files = fo.listdir()
        for f in files:
            if f not in self._files:
                ff = fo.join(f)
                if not o or ff.isfile():
                    self.gui.addFilePath(ff)
        self._files = files
                
        