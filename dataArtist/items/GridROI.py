import pyqtgraph_karl as pg
import numpy as np
from math import cos, sin, pi
import cv2
from pyqtgraph_karl.Qt import QtCore

from PseudoSquareROI import PseudoSquareROI
from dataArtist.items.QPainterPath import QPainterPath



class GridROI(pg.ROI):
    '''
    An ROI displaying mini ROIs of different shapes as a grid
    '''

    def __init__(self, pos=[20,20], size=[20,20], grid=[4,5], 
                 shape='Rect', gap=[0,0], subgrid=([],[]),
                 subgrid_width=0.05, pen='w', **kwargs):
        '''
        shape = ['Rect', 'Square', 'Circular', 'Pseudosquare']
        '''
        self.opts = {'shape':shape,
                     'grid':np.asarray(grid),
                     'gap':np.asfarray(gap),
                     'subgrid':subgrid,
                     'subgrid_width':subgrid_width
                    }
        #TODO: limit max cell size while rescale
        self.maxCellSize = size / self.opts['grid']

        self.cells = []
        self._createCells()
        self._createSubgrid()

        #cannot set brush at the moment, so:
        if 'brush' in kwargs:
            kwargs.pop('brush')
        
        pg.ROI.__init__(self, pos,size, pen=pen, **kwargs)

        self.translatable = False
        self.mouseHovering = False
        
        self._setCellSize(self.state['size'])
        self._setCellPos(pos)

        self.layout_rescaling  = False
        
        self.addScaleHandle([1, 1], [0,0])
        self.addScaleHandle([0, 0], [1,1])
        self.addScaleHandle([1, 0], [0,1])
        self.addScaleHandle([0, 1], [1,0])
        
        self.addRotateHandle([0.5, 1], [0.5,0.5])


    def saveState(self):
        s = pg.ROI.saveState(self)
        o = self.opts
        s['gap'] = tuple(o['gap'])
        s['grid'] = tuple(o['grid'])
        s['shape'] = o['shape']
        return s
    

    def painterPath(self):
        '''
        Return a qpainterpath including all cells
        '''
        p = self.cells[0].painterPath()
        for c in self.cells[1:]:
            p.addPath(c.painterPath())
        return p


    def _createCells(self):
        grid = self.opts['grid']
        
        cellClass = {'Rect':RectROI, 
                     'Circle':CircleROI,
                     'Pseudosquare':CellPseudoSquareROI}[self.opts['shape']]     
        
        self.layout_rescaling  = True
        
        for c in self.cells:
            self.vb.removeItem(c)
 
        self.cells = [cellClass(pos=[1,1]) for _ in range( grid[0]*grid[1])]
        
        i_scaleCell = -(grid[0]*grid[1]-grid[1]+1)
        self._scaleCell = c = self.cells[i_scaleCell]
        
        c.setScaleCell()
        c.sigRegionChanged.connect(self._cellResized)


    def _createSubgrid(self):
        for c in self.cells:
            for line in c.subgrid:
                self.vb.removeItem(line)
   
        s = self.opts['subgrid']
        w = self.opts['subgrid_width']
        for c in self.cells:
            for pos in s[0]:
                c.subgrid.append(SubLine(c, orientation=0, pos=pos, 
                                         thickness=w))
            for pos in s[1]:
                c.subgrid.append(SubLine(c, orientation=1, pos=pos, 
                                         thickness=w))
        
        for n, line in enumerate(self._scaleCell.subgrid):
            line.setScaleLine()
            line.sigRegionChanged.connect(lambda line, n=n:
                                    self._lineResized(line, n))
 

    def setPen(self, pen):
        pg.ROI.setPen(self, pen)
        for c in self.cells:
            c.setPen(pen)
            for line in c.subgrid:
                line.setPen(pen)


    def setBrush(self, pen):
        pass
        #TODO
        #pg.ROI.setB(pen)
#         for c in self.cells:
#             c.setBrush(pen)
#             #raises: AttributeError: 'RectROI' object has no attribute 'setBrush'


    def getMask(self, shape):
        m = self.cells[0].getMask(shape)
        for c in self.cells[1:]:
            m +=  c.getMask(shape)
        return m
        

    def __iter__(self):
        return iter(self.cells)

    
    def __len__(self):
        return len(self.cells)


    def _lineResized(self, line, n):
        if not self.layout_rescaling:
            #size = line.state['size']
            pos = line.state['pos']
            
            thick, pos = line.fromState()

            for c in self.cells:
                ln = c.subgrid[n]
                if ln != line:
                    ln.thickness = thick
                    ln.pos = pos
                    ln.updatePos()
                    ln.updateSize()


    def _cellResized(self, cell):
        if not self.layout_rescaling:
            size = cell.state['size']
         
            self.opts['gap'] = (self.state['size'] - (
                                size*self.opts['grid']) ) / (self.opts['grid']-1)

            for c in self.cells:
                if c != cell:
                    c.setSize(size)
            self._setCellPos(self.state['pos'], True)
           

    def setAngle(self, angle, update=True, finish=True):
        for c in self.cells:
            c.setAngle(angle, update, finish)
            for line in c.subgrid:
                line.setAngle(angle, update, finish)
        self._setCellPos(self.state['pos'])
        pg.ROI.setAngle(self, angle, update, finish)


    def setPos(self, pos, update=True, finish=True):
        pg.ROI.setPos(self, pos, update, finish)
        self._setCellPos(pos)


    def setSubGrid(self, s):
        self.opts['subgrid'] = s
        self.refresh()


    def setGrid(self, x=None,y=None):
        g = self.opts['grid']
        if x is not None:
            g[0]=x
        if y is not None:
            g[1]=y            
        self.refresh()


    def setCellShape(self, shape):
        self.opts['shape'] = shape
        self.refresh()
        
        
    def refresh(self):
        self._createCells()
        self._setCellSize(self.state['size'])
        self._setCellPos(self.state['pos'])
        [self.vb.addItem(c) for c in self.cells]
        self._createSubgrid()
        [ [self.vb.addItem(line) for line in c.subgrid] for c in self.cells]


    def setSize(self, size, update=True, finish=True):
        pg.ROI.setSize(self, size, update, finish)
        self.layout_rescaling =True
        self._setCellSize(size)
        self._setCellPos(self.state['pos'])
        self.layout_rescaling = False
        self.maxCellSize = size / self.opts['grid']


    def _setCellSize(self, size):
        size_cell = (size - (self.opts['grid']-1)*self.opts['gap']) / self.opts['grid'] 
        for c in self.cells:
            c.setSize(size_cell)
            for line in c.subgrid:
                line.updateSize()


    @staticmethod
    def _rotatePoint(point, angle, center):
        if angle == 0:
            return point
        x = point[0]
        y = point[1]
        cx = center[0]
        cy = center[1]
        point[0] = cos(angle) * (x - cx) - sin(angle) * (y - cy) + cx
        point[1] = sin(angle) * (x - cx) + cos(angle) * (y - cy) + cy
        
        
    def _setCellPos(self, pos, ignoreScaleCell=False):
        size_cell = self._scaleCell.state['size']

        rad = self.state['angle']*pi/180
        #center of rotation:
        c = self.state['pos']
        if self.handles:
            #centre defined by both edges:
            c += 0.5*self.handles[1]['item'].pos()
        n = 0
        for x in range(self.opts['grid'][0]):
            for y in range(self.opts['grid'][1]):
                cell = self.cells[n]
                n += 1
                if ignoreScaleCell and cell == self._scaleCell:
                    for line in cell.subgrid:
                        line.updatePos()
                    continue
                p = pos +  [x,y]*(size_cell+self.opts['gap'])
                self._rotatePoint(p, rad, c)
                cell.setPos(p)
                for line in cell.subgrid:
                    line.updatePos()


    def setViewBox(self, v):
        '''
        add grid and its cells to the ViewBox
        '''
        self.vb = v
        v.addItem(self)    
        [v.addItem(c) for c in self.cells]
        [ [self.vb.addItem(line) for line in c.subgrid] for c in self.cells]


    def show(self):
        [c.show() for c in self.cells]
        [ [line.show() for line in c.subgrid] for c in self.cells]

        pg.ROI.show(self)


    def hide(self):
        [c.hide() for c in self.cells]
        [ [line.hide() for line in c.subgrid] for c in self.cells]
        pg.ROI.hide(self)


    def close(self):
        [self.vb.removeItem(c) for c in self.cells]
        self.vb.removeItem(self)
       
        
        
class _CellBase(object):     
    '''
    Base class for all cells in a grid
    '''
    def __init__(self, *args,**kwargs):
        self.subgrid = []
        self.translatable = False
        self.mouseHovering = False



class SubLine(pg.ROI):
    '''
    one line for the subgrid
    '''
    def __init__(self, cell, orientation, pos, thickness):
        pg.ROI.__init__(self, pos=(1,1), size=(1,1))
        
        self.translatable = False
        self.mouseHovering = False

        self.pos = pos
        self.thickness = thickness
        
        if orientation == 0:
            self.i = 0
            self.j = 1
        else:
            self.i = 1
            self.j = 0           
        
        self.cell = cell


    def fromState(self):
        '''
        update thickness and position from current state
        '''
        j =  self.j
        s = self.state
        cs = self.cell.state
        p=self.pos = (s['pos'][j]-cs['pos'][j])/cs['size'][j]
        t=self.thickness = s['size'][j] / cs['size'][j]
        return t,p


    def setScaleLine(self):
        self.addScaleHandle([0.5, 1], [0.5,0])
        self.addScaleHandle([0.5, 0], [0.5,1])


    def updateSize(self):
        s = self.cell.state['size']
        pg.ROI.setSize(self, (s[self.i],self.thickness*s[self.j]))


    def updatePos(self):
        p = self.cell.state['pos'].copy()
        s = self.cell.state['size']
        
        j = self.j
        p[j]+=s[j]*self.pos

        pg.ROI.setPos(self, p)



class RectROI(pg.ROI, _CellBase):
    
    def __init__(self, *args,**kwargs):
        pg.ROI.__init__(self, *args, **kwargs)
        _CellBase.__init__(self, *args, **kwargs)


    def setScaleCell(self):
        self.addScaleHandle([1, 0], [0,1])
        self.setPen('y')


    def painterPath(self):
        p = QPainterPath()
        a = self.boundingRect()
        a.moveTo(self.state['pos'])
        p.addRect(a)
        return p


    def getMask(self, shape):
        
        p = self.state['pos']
        s = self.state['size']
        center = p + s/2
        a = self.state['angle']
        #opencv convention:
        shape = (shape[1],shape[0])
        arr = np.zeros(shape, dtype=np.uint8)        
        #draw rotated rectangle:
        vertices = np.int0( cv2.cv.BoxPoints((center, s, a)) )
        cv2.drawContours(arr, [vertices], 
                         0, 
                         color=1, 
                         thickness=-1)
        return arr.astype(bool).T

 

class CircleROI(_CellBase, pg.EllipseROI):
   
    def __init__(self, *args,**kwargs):

        pg.ROI.__init__(self, *args, **kwargs)
        _CellBase.__init__(self, *args, **kwargs)        


    def setScaleCell(self):
        self.addScaleHandle([cos(1), sin(0)], [0,1])
        self.setPen('y')


    def painterPath(self):
        p = QPainterPath()
        a = self.boundingRect()
        a.moveTo(self.state['pos'])
        p.addEllipse(a)
        return p
    
    
    def getMask(self, shape):
        '''
        returns bool array
        '''
        p = self.state['pos']
        s = self.state['size']
        center = p + s/2
        a = self.state['angle']
        #opencv convention:
        shape = (shape[1],shape[0])
        arr = np.zeros(shape, dtype=np.uint8)
        #draw ellipse:
        cv2.ellipse(arr, 
                    ( int(center[0]),int(center[1]) ), 
                    ( int(s[0]/2*self._ratioEllispeRectangle),
                      int(s[1]/2*self._ratioEllispeRectangle) ), 
                    int(a),
                    startAngle=0, 
                    endAngle=360,
                    color=1,
                    thickness=-1)
        return arr.astype(bool).T




class CellPseudoSquareROI(_CellBase, PseudoSquareROI):
    
    def __init__(self, *args,**kwargs):
        PseudoSquareROI.__init__(self, *args, **kwargs)
        _CellBase.__init__(self, *args, **kwargs)


    def setScaleCell(self):
        self.addScaleHandle([1,0], [0,1])
        self.setPen('y')


    def painterPath(self):
        p = QPainterPath()
        roundness = int(99 * float(self._alen)/16/90)
        r = QtCore.QRectF(self._rect)
        r.moveTo(self.state['pos'])
        p.addRoundRect(r, roundness)
        return p



if __name__ == '__main__':
    from pyqtgraph.Qt import QtGui

    app = QtGui.QApplication([])
    w = pg.GraphicsWindow(size=(1000,800), border=True)
    w.setWindowTitle('pyqtgraph example: ROI Examples')
    
    w1 = w.addLayout(row=0, col=0)
    #label1 = w1.addLabel('test', row=1, col=0)
    v = w1.addViewBox(row=1, col=0, lockAspect=True)

    v2 = w1.addViewBox(row=2, col=0, lockAspect=True)
    img1b = pg.ImageItem()
    v2.addItem(img1b)


    v3 = w1.addViewBox(row=3, col=0, lockAspect=True)
    img1c = pg.ImageItem()
    v3.addItem(img1c)

    ## Create image to display
    arr = np.ones((100, 100), dtype=float)
    arr[45:55, 45:55] = 0
    arr[25, :] = 5
    arr[:, 25] = 5
    arr[75, :] = 5
    arr[:, 75] = 5
    arr[50, :] = 10
    arr[:, 50] = 10
    arr += np.sin(np.linspace(0, 20, 100)).reshape(1, 100)
    arr += np.random.normal(size=(100,100))


    img1a = pg.ImageItem(arr)
    v.addItem(img1a)

    r = GridROI([20, 20], [20, 20], pen=(0,9), 
                subgrid=([0.3,0.5,1],[]), shape='Pseudosquare')
    r.setViewBox(v)

    cell = r.cells[0]
    v.autoRange(False)

    def update(roi):
        img1b.setImage(roi.getArrayRegion(arr, img1a), levels=(0, arr.max()))
        img1c.setImage(np.int0(r.getMask(arr.shape)))

    #cell.sigRegionChanged.connect(update)
    #update(cell)

    app.exec_()