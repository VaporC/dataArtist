
import numpy as np

from pyqtgraph_karl.graphicsItems.GraphicsObject import GraphicsObject
import pyqtgraph_karl as pg
from pyqtgraph_karl import functions as fn

from dataArtist.items.QPainterPath import QPainterPath


#The following class is basically a copy from pyqtgraph
#but using dataArtists modified QPainterPath
#TODO: implement without complete code copy


class FreehandItem(GraphicsObject):
    """
    **Bases:** :class:`GraphicsObject <pyqtgraph.GraphicsObject>`
    
    #TODO text
    Item displaying an isocurve of a 2D array.To align this item correctly with an 
    ImageItem,call isocurve.setParentItem(image)
    """
    

    def __init__(self, parentItem=None, pen='w', brush=None, elements=None, 
                 is_area=True):
        """
        Create a new isocurve item. 
        
        ==============  ===============================================================
        **Arguments:**
        elements
        is_area         Whether the drawn path is closed and can be filled
        ==============  ===============================================================
        """
        GraphicsObject.__init__(self)

        self.setElements(elements)
        
        self.isEmpty = self.path.isEmpty
        self.is_area = is_area
        self.pathEdit = None
        self.isModify = False
        self.setPen(pen)
        
        self.brush = brush
        if brush:
            self.setBrush(brush)
        
        if parentItem is not None:
            self.setParentItem(parentItem)


    def saveState(self):
        return {'elements': self.elements(), 'is_area':self.is_area}



    def setElements(self, elem):
        self.path = QPainterPath()
        if elem:
            self.path.moveTo(*elem[0])
            for e in elem[1:]:
                self.path.lineTo(*e)
            self.update()


    def painterPath(self):
        return self.path

    
    def startPath(self, pos):
        self.path.moveTo(*pos)
#        self.prepareGeometryChange()
        self.update()   


    def continuePath(self, pos):
        self.path.lineTo(*pos)
        self.update()   


    def closePath(self):
        if self.is_area:
            self.path.closeSubpath()
            self.update()   
        

    def setPen(self, *args, **kwargs):
        """Set the pen used to draw the isocurve. Arguments can be any that are valid 
        for :func:`mkPen <pyqtgraph.mkPen>`"""
        self.pen = fn.mkPen(*args, **kwargs)
        self.update()


    def setBrush(self, *args, **kwargs):
        """Set the brush used to draw the isocurve. Arguments can be any that are valid 
        for :func:`mkBrush <pyqtgraph.mkBrush>`"""
        self.brush = fn.mkBrush(*args, **kwargs)
        self.update()


    def elements(self):
        c = self.path.elementCount()-1
        elem = np.empty( (c,2) ) 
        for i in xrange(c):
            e = self.path.elementAt(i)
            elem[i] = e.x,e.y
        return elem


    def setModify(self, modify):
        self.isModify = modify

        if modify:
            self.hide()
            self.pathEdit = pg.PolyLineROI(self.elements(), 
                                closed=True, pen=self.pen, movable=False)
            self.getViewBox().addItem(self.pathEdit)
            
        elif self.pathEdit is not None:
            #x0,y0 = self.pathEdit.pos()
            for i,h in zip(range(self.path.elementCount()-1), self.pathEdit.getHandles()):
                e = self.path.elementAt(i)
                x,y = h.pos()
                
                self.path.setElementPositionAt(i, x,y)
            #last element = first element:
            self.path.setElementPositionAt(i+1, *self.pathEdit.getHandles()[0].pos())
            self.getViewBox().removeItem(self.pathEdit)
            self.pathEdit = None
            self.show()


    def boundingRect(self):
        return self.path.boundingRect()
    

    
    def paint(self, p, *args):
        p.setPen(self.pen)
        if self.brush is not None and self.is_area:
            p.setBrush(self.brush)
        p.drawPath(self.path)
    