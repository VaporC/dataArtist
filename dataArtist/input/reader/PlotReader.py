import numpy as np
from operator import itemgetter 

from pyqtgraph_karl.Qt import QtCore
from pyqtgraph_karl.pgcollections import OrderedDict

import fancywidgets.pyqtgraphBased.parametertree.parameterTypes as pTypes
from fancytools.os.countLines import countLines

#OWN
from dataArtist.input.reader._ReaderBase import ReaderBase



        
class PlotReader(ReaderBase):
    '''
    Readout values from a plain-text saved in file. The format has to be similar to the following example::
        
        value00 value01 value02
        value10 value11 value12
        ...
    
    Where the values of all dimensions are written in one line, separated by one or
    more signs like spaces ' ' or tab '\t'.
    
    Large files (larger that RAM) can be read through choosing a buffer size.
    '''

    axes = ['x', 'y']
    ftypes = ('csv','txt')

    def __init__(self, *args, **kwargs):
        ReaderBase.__init__(self, *args, **kwargs)

        self.preferences = _CSVPreferences()
        self.n_line = 0
        self.nLines = 1

        self._lastModified = None
        self._lastFilename = None


    @staticmethod 
    def check(ftype, fname):  
        return ftype in PlotReader.ftypes
    

    def open(self, filename):
        
        prefs = self.preferences
        #VARIABLES:
        buff = prefs.pBuffer.value()
        step = prefs.pReadEveryNLine.value()
        stop_at_line = prefs.pHasStopLine.value()
        stop_n = prefs.pStopLine.value()
        x_col = prefs.pXColumn.value()
        has_x_col = prefs.pHasXColumn.value()
        
        self.n_line = 0 #number of current line
        step_len = 0 #number of lines in the read file_part
        n_defective_lines = 0 # number of corrupted lines
        i = 0 # current index in data array
        at_end = False # is file the the end

        labels = filename

        #COUNT LINES:
        if stop_at_line:
            self.nLines = stop_n
        else:
            modified = QtCore.QFileInfo(filename).lastModified().toString()
            #ONLY OF THIS IS A NEW FILE OR THE FILE WAS MODIFIED:
            if not (self._lastFilename == filename and self._lastModified == modified):
                self.nLines = countLines(filename, prefs.pBuffer.value())
                self._lastnLines = self.nLines
                self._lastFilename = filename
                self._lastModified = modified
            else:
                self.nLines = self._lastnLines

        #GET NUMBER OF COLUMNS:
        with open(filename, 'r') as f:
            
            #FIND SEPARATOR:
            if prefs.pFindSeparator.value():
                prefs.pSeparator.setValue(self._findSeparator(f))
            separator = prefs.separators[prefs.pSeparator.value()]
            
            #DEFINE NUMBER OF COLUMNS:
            n_col = f.readline().count(separator)+1
            f.seek(0) #back to begin
            #FILTER COLUMNS:
            filter_columns = prefs.pFilterColumns.value()
            if filter_columns:
                c = [ch.value() for ch in prefs.pFilterColumns.children()[1:]][:n_col]
                #ADD X COLUMN TO THE BEGINNING:
                if has_x_col:
                    if x_col not in c:
                        c.insert(0,x_col)
                n_col = len(c)
                col_filter = itemgetter(*c)
            elif n_col >1:
                col_filter = lambda l: l[:n_col]
            else:
                col_filter = lambda l:l[0]
            
            #GET FIRST LINE NAMES:
            fline = prefs.pFirstLine.value()
            if fline != '-':
                names = col_filter(f.readline().split(separator))
                if fline == 'axes names':
                    for n, ax in enumerate(self.display.axes):
                        ax.p.setValue(names[n])
                
                else: #plot names:
                    labels = names
                    if has_x_col:
                        labels.pop(x_col)
                        
            #JUMP TO START POSITION:
            startline = prefs.pStartLine.value()
            if startline:
                f.readline(startline)
                self.n_line = startline
  
            #PRINT FIRST 10 LINES:
            if prefs.pPrintFirstLines.value():
                startPos = f.tell()
                print '=========='
                for line in f.readlines( min(self.nLines,10) ):
                    
                    #TODO: do the check for \n only once 
                    # ??? doesn't have every line \n at the end??
                    #print line[-2:]
                    #if line[-2:] == '\n':
                    #    line = line[:-2]
                    print '[%s]: %s' %(self.n_line, line)
                    print '--> %s\n' %str(col_filter(line.split(separator)))
                f.seek(startPos)
                print '=========='
            
            #CREATE DATA ARRAY:
            shape = self.nLines/step
            if n_col == 0:
                raise Exception('no columns given')
            elif n_col > 1:
                shape = (shape,n_col)
            data = np.empty(shape=shape, dtype=prefs.dtypes[prefs.pDType.value()])
                
            #MAIN LOOP:
            while not self.canceled:
                #READ PART OF THE FILE:
                file_piece = f.readlines(buff)
                l = len(file_piece)
                if not l:
                    break
                for n, line in enumerate(file_piece[::step]):
                    #line = line[:-1]
                    #FILTER COLUMNS:
                    line = col_filter(line.split(separator))
                    self.n_line = n+step_len
                    #ADD LINE TO ARRAY:
                    try:
                        data[i] = line
                        i += 1
                    except ValueError:
                        n_defective_lines += 1
                #CHECK BREAK CRITERIA:
                    if stop_at_line and self.n_line >= stop_n:
                        at_end = True
                        break
                if at_end:
                    break
                step_len += l
            data = data[:i]
            print '%s lines were corrupted' %n_defective_lines

            #SPLIT ARRAY IF NEEDED:
            if (has_x_col and n_col > 2) or (not has_x_col and n_col > 1):
                if has_x_col:
                    x = data[:,x_col]
                    #GET Y COLUMNS THROUGH REMOVING THE X COLUMN:
                    y_cols = np.c_[ data[:,:x_col], data[:,x_col+1:] ]
                else:
                    y_cols = data
                l = []
                #CREATE TUPLE OF [y_n] OR [x, y_n] arrays:
                for n in range(y_cols.shape[1]):
                    y = y_cols[:,n]
                    if has_x_col:
                        y = np.c_[x,y]
                    l.append(y)
                return tuple(l), labels
            return [data], labels

    
    def _findSeparator(self, f):
        #find separating symbol between values (e.g. tab, comma ...)
        separators = self.preferences.separators

        last_pos = f.tell()
        numberOfSeparator = [0]*len(separators)
        #get the first 50 lines and try to determine the separator there
        for line in f.readlines( min(self.nLines, 50) ):
            for n,s in enumerate(separators.values()):
                numberOfSeparator[n] += line.count(s)
        sep = separators.keys()[numberOfSeparator.index(max(numberOfSeparator))]
        print "--> separator set to '%s'" %sep
        f.seek(last_pos) # go back  
        return sep 

    def status(self):
        #read lines over all lines
        return float(self.n_line) / self.nLines



class _CSVPreferences(pTypes.GroupParameter):
    
    def __init__(self, name='Plot import'):
        pTypes.GroupParameter.__init__(self, name=name)

        self.separators = {'SPACE':' ', 'TAB':'\t', 'COMMA':',', 'SEMICOLON':';'}
        
        self.dtypes = OrderedDict ( (
                        ("16 bit float",np.float16),
                        ("32 bit float",np.float32),
                        ("64 bit float",np.float64),
                        ("8 bit integer",np.int8),
                        ("16 bit integer",np.int16),
                        ("32 bit integer",np.int32),
                        ("64 bit integer",np.int64) ) )

        self.pDType = self.addChild({
            'name':"Data type",
            'type':'list',
            'value':"32 bit float",
            'limits':self.dtypes.keys()})

        self.pFindSeparator = self.addChild({
            'name':"Find Separator Character",
            'type':'bool',
            'value':True})
        self.pFindSeparator.sigValueChanged.connect(lambda param, value: 
                            [ch.show(not value) for ch in param.children()] )
        
        self.pSeparator = self.pFindSeparator.addChild({
            'name':"Separator Character",
            'type':'list',
            'value':'COMMA',
            'visible':False,
            'limits':self.separators.keys(),
            'tip':'''the sign, that separates the values in one line e.g. '\t' for a tab'''} )

        self.pPrintFirstLines = self.addChild({
            'name':"Print 1st 10 lines",
            'type':'bool',
            'value':False})

        self.pFirstLine = self.addChild({
            'name':"First line contains",
            'type':'list',
            'value':'plot names',
            'limits':['plot names', 'axes names', '-']})
   
        self.pBuffer = self.addChild({
            'name':"Buffer[byte]",
            'type':'int',
            'value':int(10e6),
            'limits':[0,1e10],
            'tip':'''max. size(byte) loaded into RAM insert '0' to read the whole file'''} )

#TODO:
#         self.pFIFO = self.addChild({
#             'name':"Use FIFO",
#             'type':'bool',
#             'value':False})
#         
#         self.pFIFOlength = self.pFIFO.addChild({
#             'name':"length",
#             'type':'int',
#             'value':100})

        self.pStartLine = self.addChild({
            'name':"Start line",
            'type':'int',
            'value':0}) 

        self.pHasStopLine = self.addChild({
            'name':"Stop line",
            'type':'bool',
            'value':False}) 
        self.pHasStopLine.sigValueChanged.connect(lambda param, value: 
                            [ch.show(value) for ch in param.children()] )
        self.pStopLine = self.pHasStopLine.addChild({
            'name':"line",
            'type':'int',
            'value':10000,
            'visible':False}) 

        self.pReadEveryNLine = self.addChild({
            'name':"Read every n line",
            'type':'int',
            'limits':[1,100000],
            'value':1}) 

        self.pHasXColumn = self.addChild({
            'name':"X Column",
            'type':'bool',
            'value':False}) 
        self.pHasXColumn.sigValueChanged.connect(lambda param, value: 
                            [ch.show(value) for ch in param.children()] )
        
        self.pXColumn = self.pHasXColumn.addChild({
            'name':"Index",
            'type':'int',
            'visible':False,
            'limits':[0,100000],
            'value':0}) 

        self.pFilterColumns = self.addChild({
            'name':"Filter Columns",
            'type':'bool',
            'tip':'True: take all columns, False: Choose specific columns',
            'value':False}) 
        self.pFilterColumns.sigValueChanged.connect(lambda param, value: 
                            [ch.show(value) for ch in param.children()] )
        
        pAddColumns = self.pFilterColumns.addChild({
            'name':"Add",
            'type':'action',
            'visible':False}) 
        fn = lambda: self.pFilterColumns.addChild({
            'name':"Index",
            'autoIncrementName':True,
            'renamable':True,
            'removable':True,
            'type':'int',
            'value':len(self.pFilterColumns.children())-1})
        pAddColumns.sigActivated.connect(fn)