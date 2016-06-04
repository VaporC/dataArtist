import numpy as np

from pyqtgraph_karl.Qt import QtCore, QtGui

from fancywidgets.pyqtgraphBased.parametertree import ParameterTree

class ReaderBase(QtCore.QThread):
    '''
    Base class for file reader
    reading input files within a QThread in order not to block the screen
    Show progress in progress bar
    '''                      #array, filenames, labels
    done = QtCore.pyqtSignal(object, object,    object) 
    preferences = None
    forceSetup = False #whether to show import preferences on the first time


    def __init__(self, display):
        QtCore.QThread.__init__(self)
        
        self.display = display
        self.progressBar = display.workspace.gui.progressBar
        self._status_timer = QtCore.QTimer()
        self._curFile_n = 0
        self._firstTime = True
       
    @classmethod 
    def check(cls, ftype, fname):
        return ftype in cls.ftypes
        
    def _cancel(self): 
        self.canceled = True 
 
 
 
    def toFloat(self, arr, toFloat, forceFloat64):
        if not  toFloat:
            return arr
        try:
            if forceFloat64:
                dtype = np.float64
            else:
                dtype =  {np.dtype('uint8'): np.float32, #float16 is just to coarse and cause nans and infs
                          np.dtype('uint16'):np.float32,
                          np.dtype('uint32'):np.float64,
                          np.dtype('uint64'):np.float64} [arr.dtype]
            return arr.astype(dtype, copy=False)
        except KeyError:
            return arr
 
 
    def status(self):
        '''
        returns the ratio of progress 
        (should be overridden in child class)
        '''
        return 1
 
 
    def overallStatus(self):
        '''
        return the overall readout status in percent
        '''
        return 100 *  self.status() * float(self._curFile_n+1) / len(self.filenames)
 
 
    def start(self, filenames):
        self.filenames = filenames
        
        if self.preferences and self.forceSetup and self._firstTime:
            d = QtGui.QDialog()
            d.setWindowTitle('Import preferences')
            
            l = QtGui.QVBoxLayout()
            t = ParameterTree(self.preferences)
            b = QtGui.QPushButton('OK')
            b.clicked.connect(d.accept)            
            
            l.addWidget(t)
            l.addWidget(b)

            d.setLayout(l)
            
            d.accepted.connect(self._start)
            d.exec_()
        else: 
            self._start()


    def _start(self):
        self.canceled = False
        self._firstTime = False

        #PROGRESS BAR:
        self.progressBar.show()
        self.progressBar.cancel.clicked.connect(self._cancel)
        self.progressBar.bar.setValue(0)
        self._status_timer.timeout.connect(lambda:
            self.progressBar.bar.setValue(self.overallStatus()))
        self._status_timer.start(1000)#[ms] -> every second
    
        self.finished.connect(self.cleanUp)
        
        QtCore.QThread.start(self)


    def run(self):
        '''
        read data from given self.filenames
        
        returns datalayers, filenames, layernames
        '''
        data_list = []
        label_list = []
        fname_list = []
        for self._curFile_n, f in enumerate(self.filenames):
            if f:
                self.progressBar.label.setText("open file '%s'" %f)
                #GET DATA:     
                try:
                    data, labels = self.open(f)
                    if data is None:
                        raise IOError('data empty')
                    if labels is not None:
                        # multiple plots/images/etc in one file:
                        data_list.extend([d for d in data])
                        label_list.extend(labels)
                        fname_list.extend([f]*len(labels))
                    else:
                        data_list.append(data)  
                        label_list.append(labels)
                        fname_list.append(f)                 
      
                except (IOError, ValueError), errmsg:
                    print 'Error while opening %s: %s' %(f,errmsg)
                    label_list.append(None)
                    data_list.append(None)
                    fname_list.append(f)
                    
                if self.canceled:
                    break
        self.done.emit(data_list, fname_list, label_list)

            
    def cleanUp(self):
        self._status_timer.stop()
        self.progressBar.hide() 