import numpy as np
import fancywidgets.pyqtgraphBased.parametertree.parameterTypes as pTypes

#OWN
from dataArtist.input.reader._ReaderBase import ReaderBase



class Array2DReader(ReaderBase):
    '''
    Read CSV/text files using numpy.loadtxt
    '''
    ftypes = ('txt', 'csv')
    axes = ['x', 'y', '']   
    preferred = True

    def __init__(self, *args, **kwargs):
        ReaderBase.__init__(self, *args, **kwargs)
        self.preferences = _Preferences()


    @staticmethod 
    def check(ftype, fname):
        return ftype in Array2DReader.ftypes

    
    def open(self, filename):
        p = self.preferences
        f = p.pFindDelimiter.value()
        if f:
            delimiters = [',',', ','\t', ' ', ';', '; ']
        else:
            delimiters = [p.pDelimiter.value()]
        arr = None
        for d in delimiters:
            try: 
                arr = np.loadtxt(filename, 
                     dtype=p.pDType.value(),
                     comments=p.pComments.value(),
                     delimiter=d
                     )
                p.pDelimiter.setValue(d)
                p.pFindDelimiter.setValue(False)
                break
            except Exception, err:
                if not f:
                    print err
        if p.pTransposed.value():
            arr = arr.T
        labels = None
        return arr, labels



class _Preferences(pTypes.GroupParameter):
    SUBST_SIGN = {' ':'SPACE', '\t':'TAB'}
    RE_SIGN = {'SPACE': ' ', 'TAB': '\t'}
    
    def __init__(self, name='Numpy import'):
        
        pTypes.GroupParameter.__init__(self, name=name)
        
        self.pDType = self.addChild({
                'name':'dtype',
                'type':'list',
                'value':'float',
                'limits':['int','float']})
        self.pComments = self.addChild({
                'name':'Comments',
                'type':'str',
                'value':'#'})
        self.pFindDelimiter = self.addChild({
                'name':'Find delimiter',
                'type':'bool',
                'value':True})
        self.pDelimiter = self.pFindDelimiter.addChild({
                'name':'Delimiter',
                'type':'str',
                'value':',',
                'visible':False,
                'tip':'''The sign used to separate values. 
                By default, this is one whitespace.
                Type 'TAB' to choose tab.'''})
        self.pDelimiter.setValue = self._setValueDelimiter
        self.pDelimiter.value = self._valueDelimiter
        
        self.pFindDelimiter.sigValueChanged.connect(lambda p,v:
                                    self.pDelimiter.show(not v))
        self.pTransposed = self.addChild({
                'name':'Transposed',
                'type':'bool',
                'value':False,
                'tip':'''Check, if data is transposed'''})
    
    
    def _setValueDelimiter(self, val):
        p = self.pDelimiter
        if val in self.SUBST_SIGN:
            val = self.SUBST_SIGN[val]
        p.__class__.setValue(p, val)
        
        
    def _valueDelimiter(self):
        p = self.pDelimiter
        val = p.__class__.value(p)
        if val in self.RE_SIGN:
            val = self.RE_SIGN[val]
        return val