
from pyqtgraph_karl.widgets.MatplotlibWidget import MatplotlibWidget

#import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm



class MatplotlibSurface(MatplotlibWidget):
    dimensions = (4,)
   # axisOrientation = ['bottom', 'left']
    #icon = 'trend.svg'

    def __init__(self, display, axes, data=None, names=None, 
#                  uncertainty=None
                 ):
        MatplotlibWidget.__init__(self)#size=(5.0, 4.0), dpi=100
#         self.uncertainty = uncertainty

        self.toolbar.hide()
      #  self.vbox.setContentsMargins(0, 0, 0, 0)
        
        s = self.surface = self.fig.add_subplot(111, projection='3d')
        a = display.axes
        s.axis('equal')
        
        s.azim = -90
        s.elev = -90

       # s.auto_scale_xyz([0,480],[0,360],[0,3000])
        
        a[0].p.sigValueChanged.connect(lambda param, value: s.set_xlabel(value))
        s.set_xlabel(a[0].p.value())
        a[1].p.sigValueChanged.connect(lambda param, value: s.set_ylabel(value))
        s.set_ylabel(a[1].p.value())
        a[2].p.sigValueChanged.connect(lambda param, value: s.set_zlabel(value))
        s.set_zlabel(a[2].p.value())

        
        
        self.data = []
       # self.data = []
        self.changed = False

        if names is not None and data is not None:
            for i,(d,n) in enumerate(zip(data, names)):
                self.addLayer(n, d)                                
        self.draw()

        #UPDATE CURVE NAMES:
       # display.stack.sigLayerNameChanged.connect(
        #        lambda index, txt, self=self: self.surfaces[index].set_xlabel('X')(txt))


    def save(self, session, path):
        pass


    def clear(self):
        pass


    def restore(self, session, path):
        pass
    

    def getData(self, index=None):
        pass


#     def getUncertainty(self, index=None):
#         pass
     
            
    def removeLayer(self, index, toMove=False):
        pass



    def insertLayer(self, index, name, data=None, pen=None):
        # data = 3darray[i,j,(x,y,z)]
        if data is not None:
            #surface = self.fig.add_subplot(111, projection='3d')
            
           # surface.set = lambda data: self.setSurface(surface, data)
            
            self.data.insert(index, data)
            self.changed = True
           # surface._data = data
          #  surface._changed = True
           # self.data.insert(index, data)
            #transpose to data = [x,y,z]

        #return surface


    def insertMovedLayer(self, index):
        pass
        #self.addItem(self._movedCurve, params={})
        #self.curves.insert(index, self._movedCurve)
        #del self._movedCurve 


    def addLayer(self, name='unnamed', data=None, **kwargs):
        return self.insertLayer(len(self.data), name, data, **kwargs)


    def update(self, data=None, index=None, label=None,**kwargs):
        if data is not None:
#             if data == self.data:
#                 return
            if index is not None:
                self.data[index] = data
                #s = self.surfaces[index]
                #s._data = data
            else:
                self.data = data
            self.changed = True
               # print 222
          #  else:

#     @staticmethod
#     def setSurface(surface, data):
      


    def updateView(self, force=False, xRange=None):#, yRange=None, zRange=None):
        if self.changed:
            s = self.surface
            s.clear()
            for d in self.data:
                n = d.shape[0]/50 # plot max 50x50 planes
                if n < 1:
                    n = 1
                data = d.transpose(2,0,1)
                s.plot_surface(data[0,::n,::n], data[1,::n,::n], data[2,::n,::n], cmap=cm.jet)
                

                #s._changed = False  
            #s.pbaspect = [1.0, 1.0, 1.0]
            if xRange is not None:
                s.set_xlim(xRange)
#             if yRange != None:
#                 s.set_ylim(yRange)            
#             if zRange != None:
#                 if xRange:
#                 s.get_zlim()
#                 s.set_zlim(zRange)
            s.pbaspect = [1,1,1]
            #else:
            #    s.set_zlim(s.get_zlim())
        #    s.axis('equal')
            #s.invert_zaxis()
            self.fig.tight_layout()
            self.draw()
            self.changed = False
#             if d.changed:
#                 self.curves[n].updateItems() 
#                 d.changed = False


# class _PlotData(list):
#     def __init__(self, l):
#         list.__init__(self, l)
#         self.changed = True