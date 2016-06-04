import numpy as np

#OWN
from dataArtist.input.reader._ReaderBase import ReaderBase



class NpyReader(ReaderBase):
    '''
    Reader for numpy arrays saved to file as *.npy
    '''
    ftypes = ('npy',)

    def __init__(self, *args, **kwargs):
        ReaderBase.__init__(self, *args, **kwargs)


    @staticmethod 
    def check(ftype, fname):  
        b = ftype in NpyReader.ftypes
        if b:
            #get the array shape
            arr = np.load(fname, mmap_mode='r')
            NpyReader.axes = arr.ndim + 1
            #delete memory mapped array to close it
            del arr    
        return b
    

    def open(self, filename):
        arr = np.load(filename)
        labels = None
        return arr, labels