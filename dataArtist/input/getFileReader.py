import inspect

from dataArtist.widgets.dialogs.ChooseFileReaderDialog import ChooseFileReaderDialog
from . import reader


READERS = inspect.getmembers(reader, inspect.isclass)


def getFileReader(filenames=[]):
    '''
    Try to find the right reader comparing filetypes of the given [filenames]
    (e.g. reader.image for *.jpg)
    '''        
    readers = []
    if not filenames:
        raise IOError('need a list of filenames if no reader is given')
    ftype = filenames[0].filetype().lower()
    if not ftype:
        raise IOError('input file needs a file-type like .csv or .jpg')
    for _, cls in READERS:
        if cls.check(ftype, filenames[0]):
            readers.append(cls)
    if not readers:
        raise IOError( ftype + ' not supported') 
    if len(readers)>1:
        d = ChooseFileReaderDialog(readers)
        d.exec_()   
        return readers[d.index]
    return readers[0]

