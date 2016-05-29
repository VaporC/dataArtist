import pyqtgraph_karl as pg
from pyqtgraph_karl.Qt import QtCore, QtGui
import numpy as np
import cv2



class PseudoSquareROI(pg.ROI):
    """
    ROI built by intersection of an ellipse and a rectangle.
    """
    
    def __init__(self, pos, size=[1,1],ratioEllispeRectangle=1.2, **args):
        self._ratioEllispeRectangle = ratioEllispeRectangle
        
        pg.ROI.__init__(self, pos, size, **args)

        self._prepare()


    def setRatioEllispeRect(self, ratio):
        assert 1<= ratio <=1.41
        self._ratioEllispeRectangle = ratio
        self._prepare()
        self.update()


    @staticmethod
    def _intersectionPointsAndAngles(r, ratioEllispeRectangle):
        '''
        return all 8  x and y coords of lines build by intersection of ellipse and rect
        '''
        w = r.width()
        h = r.height()
        x1  = 0.5*w
        y2 = 0.5*h

        #ellipse parameters:
        a = x1* ratioEllispeRectangle
        b = y2* ratioEllispeRectangle
        #intersection coords in the 1st quadrant with center=(0,0):
        y1 = ((1-x1**2/a**2)*b**2)**0.5
        x2 = ((1-y2**2/b**2)*a**2)**0.5

        c = r.center()
        cx = c.x()
        cy = c.y()
        
        #edge points:
        p1 = QtCore.QPointF(cx+x1, cy+y1)
        p2 = QtCore.QPointF(cx+x2, cy+y2)
        p3 = QtCore.QPointF(cx-x2, cy+y2)
        p4 = QtCore.QPointF(cx-x1, cy+y1)
        p5 = QtCore.QPointF(cx-x1,  cy-y1)
        p6 = QtCore.QPointF(cx-x2, cy-y2)
        p7 = QtCore.QPointF(cx+x2, cy-y2)
        p8 = QtCore.QPointF(cx+x1, cy-y1)
        
        #angle in as degree*16 (needed in .drawArc)
        a1 = int(QtCore.QLineF(c,p1).angle()*16)
        a2 = int(QtCore.QLineF(c,p2).angle()*16)
        a4 = int(QtCore.QLineF(c,p4).angle()*16)
        a6 = int(QtCore.QLineF(c,p6).angle()*16)
        a8 = int(QtCore.QLineF(c,p8).angle()*16)

        arc_length = a1-a2
        return (p1,p2,p3,p4,p5,p6,p7,p8), (a2,a4,a6,a8), arc_length
        
    
    
    def _prepare(self):
        r = self.boundingRect()
        r = QtCore.QRectF(r.x()/r.width(), r.y()/r.height(), 1,1)
        #get draw params:
        self._edges, self._angles, self._alen = self._intersectionPointsAndAngles(
                                r, self._ratioEllispeRectangle)
        #scale rect:
        bl = r.bottomLeft()
        tr = r.topRight()
        size = tr-bl
        newSize = size * self._ratioEllispeRectangle
        ds = 0.5*(newSize-size)
        r.setBottomLeft(bl-ds)
        r.setTopRight(tr+ds)
        self._rect = r

    
    def paint(self, p, opt, widget):
        r = self.boundingRect()
        p.scale(r.width(), r.height())## workaround for GL bug
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        p.setPen(self.currentPen)
        #interrupted rectangle:
        p.drawLine(self._edges[1],self._edges[2])
        p.drawLine(self._edges[3],self._edges[4])
        p.drawLine(self._edges[5],self._edges[6])
        p.drawLine(self._edges[7],self._edges[0])
        #outer circle:
        p.drawArc(self._rect, self._angles[0], self._alen)
        p.drawArc(self._rect, self._angles[1], self._alen)
        p.drawArc(self._rect, self._angles[2], self._alen)
        p.drawArc(self._rect, self._angles[3], self._alen)


    def getMask(self, shape):
        
        p = self.state['pos']
        s = self.state['size']
        center = p + s/2
        a = self.state['angle']
        #opencv convention:
        shape = (shape[1],shape[0])
        arr1 = np.zeros(shape, dtype=np.uint8)        
        arr2 = np.zeros(shape, dtype=np.uint8)

        #draw rotated rectangle:
        vertices = np.int0( cv2.cv.BoxPoints((center, s, a)) )
        cv2.drawContours(arr1, [vertices], 
                         0, 
                         color=1, 
                         thickness=-1)
        #draw ellipse:
        cv2.ellipse(arr2, 
                    ( int(center[0]),int(center[1]) ), 
                    ( int(s[0]/2*self._ratioEllispeRectangle),
                      int(s[1]/2*self._ratioEllispeRectangle) ), 
                    int(a),
                    startAngle=0, 
                    endAngle=360,
                    color=1,
                    thickness=-1)
        #bring both together:
        return np.logical_and(arr1,arr2).T


    def getArrayRegion(self, arr, img=None):
        """
        Return the result of ROI.getArrayRegion() masked by the elliptical shape
        of the ROI. Regions outside the ellipse are set to 0.
        """
        #TODO: get right area for pseudosquare
        arr = pg.ROI.getArrayRegion(self, arr, img)
        if arr is None or arr.shape[0] == 0 or arr.shape[1] == 0:
            return None
        w = arr.shape[0]
        h = arr.shape[1]
        ## generate an ellipsoidal mask
        mask = np.fromfunction(lambda x,y: (((x+0.5)/(w/2.)-1)**2+ (
                        (y+0.5)/(h/2.)-1)**2)**0.5 < self._ratioEllispeRectangle, (w, h))
    
        return arr * mask