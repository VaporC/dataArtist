import numpy as np
from collections import OrderedDict

from fancywidgets.pyqtgraphBased.parametertree.parameterTypes import GroupParameter

#OWN
from dataArtist.input.reader._ReaderBase import ReaderBase


STR_TO_DTYPE = OrderedDict(( ('8-bit','u1'),
                             ('16-bit Signed','i2'),
                             ('16-bit Unsigned','u2'),
                             ('32-bit Signed','i4'),
                             ('32-bit Unsigned','u4'),
                             ('32-bit Real/floating point','f4'),
                             ) )



class RAWimage(ReaderBase):
    '''
    Read RAW images
    '''
    ftypes = ('raw', 'bin')
    axes = ['x', 'y', '']   
    #preferred = True
    forceSetup = True
    
    def __init__(self, *args, **kwargs):
        self.preferences = _Preferences()

        ReaderBase.__init__(self, *args, **kwargs)

    
    def open(self, filename): 
        p = self.preferences

        dt = STR_TO_DTYPE[p.pDType.value()]
        if not p.pLittleEndian.value():
            dt = '>'+ dt

        s0,s1 = p.pWidth.value(),p.pHeight.value()
        arr = np.fromfile(filename, dtype=dt, count=s0*s1)
        try:
            arr = arr.reshape(s0,s1) #, order='F'
        except ValueError:
            #array shape doesn't match actual size
            s1 = arr.shape[0]/s0
            arr = arr.reshape(s0,s1)
            
        arr = self.toFloat(arr, p.pToFloat.value(), p.pForceFloat64.value()) 

        labels = None
        return arr, labels




class _Preferences(GroupParameter):
    
    def __init__(self, name=' RAW image import'):
        
        GroupParameter.__init__(self, name=name)

        self.pDType = self.addChild({
                'name':'Image type',
                'type':'list',
                'value':'16-bit Unsigned',
                'limits':STR_TO_DTYPE.keys()})
        self.pLittleEndian = self.addChild({
                'name':'Little-endian byte order',
                'type':'bool',
                'value':False})
        self.pWidth = self.addChild({
                'name':'Width',
                'type':'int',
                'value':1024,
                'unit':'pixels'})
        self.pHeight = self.addChild({
                'name':'Height',
                'type':'int',
                'value':1024,
                'unit':'pixels'})
        self.pToFloat = self.addChild({
                'name':'transform to float',
                'type':'bool',
                'value':True})
        self.pForceFloat64 = self.pToFloat.addChild({
                'name':'Force double precision (64bit)',
                'type':'bool',
                'value':False})
        self.pToFloat.sigValueChanged.connect(lambda p,v:
                      self.pForceFloat64.show(v))
        