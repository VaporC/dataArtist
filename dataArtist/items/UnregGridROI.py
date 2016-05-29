from pyqtgraph_karl import PolyLineROI
import numpy as np
from fancytools.math.gridPointsFromEdges import gridPointsFromEdges



class UnregGridROI(PolyLineROI):
    def __init__(self, nCells, edges=None, pos=(0,0), size=(1,1), **args):
        '''
        nCells = [10,6]
        
        either define grid edges as e.g.
               np.array([(0,0),
                       (1,0.1),
                       (2,2),
                       (0.1,1)])
        or size = [4,5] and pos=[0,0]
        '''
        self._nCells = nCells
        
        if edges is None:
            edges = np.array([(pos[0],pos[1]),
                       (size[0],pos[1]),
                       (size[0],size[1]),
                       (pos[0],size[1])])
        
        points = gridPointsFromEdges(edges, nCells)

        PolyLineROI.__init__(self, points, **args)
        

        self.translatable = False
        self.mouseHovering = False

        #PREVENT CREATION OF SUB SEGMENTS:
        for s in self.segments:
            s.mouseClickEvent = lambda x:None


    def points(self):
        return np.array([(h['pos'].x(),h['pos'].y())  
                          for h in self.handles]) 


    def edges(self):
        '''
        return array containing the 4 edges of the grid
        '''
        sx,sy = self._nCells
        h = self.handles

        ind = [0,sx,-1,(sx+1)*sy]
        
        e = np.array([(h[i]['pos'].x(),h[i]['pos'].y())  
                                    for i in ind])
        e += self.pos()
        return e


    def setPoints(self, points, closed=None):

        for p in points:
            self.addFreeHandle(p)
        
        sx = self._nCells[0]
        c = 0
        #horiz. connections:
        for i in range(len(self.handles)-1):
            if c == sx:
                c = -1
            else:
                self.addSegment(self.handles[i]['item'], self.handles[i+1]['item'])
            c+=1
    
        #vertic. connections:
        for i in range(len(self.handles)-sx-1):
            self.addSegment(self.handles[i]['item'], self.handles[i+sx+1]['item'])



if __name__ == '__main__':
    from pyqtgraph.Qt import QtGui
    import pyqtgraph as pg

    app = QtGui.QApplication([])
    w = pg.GraphicsWindow(size=(1000,800), border=True)
    w.setWindowTitle('pyqtgraph example: ROI Examples')
    
    w1 = w.addLayout(row=0, col=0)
    v = w1.addViewBox(row=1, col=0, lockAspect=True)

    g = UnregGridROI([4,5])
    print g.edges()
    print g.points()

    v.addItem(g)

    app.exec_()
        