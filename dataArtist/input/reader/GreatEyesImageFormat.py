import numpy as np

#OWN
from dataArtist.input.reader._ReaderBase import ReaderBase



class GreatEyesImageFormat(ReaderBase):
    '''
    Read EL images (*.txt) created by the LumiSolarCell Software
    from GreatEyes 
    '''
    ftypes = ('txt')
    axes = ['x', 'y', '']   
    preferred = False

    def __init__(self, *args, **kwargs):
        ReaderBase.__init__(self, *args, **kwargs)


    @staticmethod 
    def check(ftype, fname):
        return ftype in GreatEyesImageFormat.ftypes

    
    def open(self, filename):  
        #TODO: replace with faster method e.g. panda      
        arr = np.loadtxt(filename, 
                         dtype=np.uint16,
                         delimiter='\n')
        shape = arr[:2]
        arr = arr[2:]
        arr = arr.reshape(shape, order='F')

        labels = None
        return arr, labels