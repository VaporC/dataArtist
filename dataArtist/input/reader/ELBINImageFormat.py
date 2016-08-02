
from imgProcessor.reader.elbin import elbin
#OWN
from dataArtist.input.reader._ReaderBase import ReaderBase, ReaderPreferences


class ELBINImageFormat(ReaderBase):
    __doc__ = elbin.__doc__
    ftypes = ('elbin',)
    axes = ['x', 'y', '']   
    preferred = False

    def __init__(self, *args, **kwargs):
        ReaderBase.__init__(self, *args, **kwargs)
        self.preferences = ReaderPreferences(name='.ELBIN file preferences')

    @staticmethod 
    def check(ftype, fname):
        return ftype in ELBINImageFormat.ftypes


    def open(self, filename): 
        arr, labels = elbin(filename) 
        arr = self.toFloat(arr.transpose(0,2,1)) 
        return arr, labels


