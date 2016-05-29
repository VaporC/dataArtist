from pyqtgraph_karl.Qt import QtGui


class QPainterPath(QtGui.QPainterPath):
    '''
    QainterPath with added methods to calculate
    area, mean, min, max
    '''

    @staticmethod
    def _frange(start, stop, step):
        '''Helper float generator'''
        while start < stop:
            yield start
            start += step
    
    
    def calcArea(self, precision = 100):
        '''QPainterPath area calculation'''
        points = [(point.x(), point.y()) for point in (
            self.pointAtPercent(perc) for perc in self._frange (0, 1, 1.0 / precision))]
        points.append(points[0])
    
        return 0.5 * abs(reduce(
            lambda sum, i: sum + (points[i][0] * points[i + 1][1] - 
                                  points[i + 1][0] * points[i][1]),
            xrange (len (points) - 1),
            0
        ))
        
    #TODO:
    def calcMean(self):
        return 0
    def calcMin(self):
        return 0    
    def calcMax(self):
        return 0