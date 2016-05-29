class PyqtgraphgDisplayBase(object):
    '''
    Base class for display widgets inherited from pyqtgraph widgets, like imageView
    '''
    def __init__(self):
        #in case a new layer cannot be added to the current ones:
        #set this variable to the index of that layer
        self.moveLayerToNewImage = None


    def setTitleSize(self, ptSize):
        l = self.view.titleLabel
        l.opts['size'] = '%spt' %ptSize
        l.setText(l.text)