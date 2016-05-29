from dataArtist.input.reader._ReaderBase import ReaderBase

import numpy as np

class ABCreader(ReaderBase):
    '''
    Reader for numpy files saved to file as *.abc
    '''
    ftypes = ('abc',)
    axes = ['a', 'b']   


    def __init__(self, *args, **kwargs):
        ReaderBase.__init__(self, *args, **kwargs)


    @staticmethod 
    def check(ftype, fname):  
        return ftype in  ABCreader.ftypes


    def open(self, filename):
        with open(filename,'r') as f:
            arr = np.array(eval(f.read()))        
        return arr, filename
