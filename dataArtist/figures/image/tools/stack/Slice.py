import pyqtgraph_karl as pg
from pyqtgraph_karl.Qt import QtGui

#OWN
from dataArtist.widgets.Tool import Tool
        
        

class Slice(Tool):
    '''
    Create a new image through slicing the image stack
    '''
    icon = 'slice.svg'
    
    
    def __init__(self, display):
        Tool.__init__(self, display)

        self.n_slices = 0
        self._ROIs = []

        a_show = QtGui.QAction('show', self)
        a_show.setCheckable(True)
        a_show.setChecked(True)
        a_show.toggled.connect(self.toggleShow)
        self.addAction(a_show)


    def toggleShow(self, checked):
        [p.toggleShow(checked) for p in self._ROIs]


    def activate(self):
        if len(self.display.widget.image) == 1:
            raise Exception('need a 3d-image for the z-stack tools')
        
        name = 'ZSlice[%s]' %str(self.n_slices+1)
        axes = self.display.axes.copy(('stack', 0,1))
        slave = self.display.workspace.addDisplay(
                                     axes=axes, 
                                     title=name)

        #position slice within current view:
        r = self.display.widget.view.vb.viewRange()
        avy =   (r[1][0]+r[1][1])/2
        xmin,xmax = r[0][0], r[0][1]
        avx = (xmin+xmax)/2
        p = [[avx-0.5*(avx-xmin),avy],[avx+0.5*(xmax-avx),avy]]

        self._ROIs.append(
                _LineROI( self.display.widget, 
                          slave, name, pen=(self.n_slices%6),
                          fromTo=p )
                          )
        self.n_slices += 1



class _LineROI(pg.LineSegmentROI):
    
    def __init__(self, master, slave, name, fromTo, pen='r'):
        pg.LineSegmentROI.__init__(self, fromTo, pen=pen)
        self.master = master
        self.slaveDock = slave

        self.text = pg.TextItem(
            text=name, 
            color=(0,0,0), 
            html=None, 
            anchor=(0, 0), 
            border=None, 
            fill=pg.mkBrush(255, 255, 255, 80), 
            angle=0)
 
        self.slaveDock.closed.connect(lambda: self.toggleShow(False))
        self.sigRegionChanged.connect(self.updateView)
        #UPDATE
        self.updateView()
        self.toggleShow()
        #DISABLE LOCK ASPECT: 
        slave.widget.view.vb.setAspectLocked(False)


    def toggleShow(self, show=True):
        if show:
            self.master.addItem(self.text)    
            self.master.addItem(self)
        else:
            self.master.removeItem(self.text)    
            self.master.removeItem(self) 


    def updateView(self):
        data = self.getArrayRegion(self.master.image, 
                                   self.master.imageItem, axes=(1,2))
        self.slaveDock.widget.setImage(data)
        
        self.text.setPos( self.boundingRect().center() + self.pos() )