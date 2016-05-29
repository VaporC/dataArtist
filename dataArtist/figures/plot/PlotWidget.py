import numpy as np
import weakref
from pyqtgraph_karl import PlotWidget as pgPlotWidget
from scipy.interpolate import interp1d

from fancytools.fcollections.ProxyList import ProxyList

from dataArtist.figures.DisplayWidget import DisplayWidget
from dataArtist.figures._PyqtgraphgDisplayBase import PyqtgraphgDisplayBase



class PlotWidget(DisplayWidget, pgPlotWidget, PyqtgraphgDisplayBase):
    dimensions = (1,2)
    axisOrientation = ['bottom', 'left']
    icon = 'trend.svg'


    def __init__(self, display, axes, data=None, names=None, **kwargs):
        self.display = display
        
        axisItems = {}
        o = self.axisOrientation
        for n,a in enumerate(axes[:2]):
            a.setOrientation(o[n])
            axisItems[o[n]] = a
            a.setPen() # update colour theme
        pgPlotWidget.__init__(self, axisItems=axisItems)
        PyqtgraphgDisplayBase.__init__(self)
        DisplayWidget.__init__(self, **kwargs)
        
        self.view = self.getPlotItem()

        self.addLegend()
        self.curves = []
        # this is mostly used for fast and easy access to all curve values
        # within the Automatic-script:
        self.data = ProxyList()

        if names is not None and data is not None:
            #ADD MULTIPLE LAYERS
            if names is None:
                c = len(data)
                names = [None]*c
            else:
                c = len(names)
            if data is None:
                data = [None]*c
            for i,(d,n) in enumerate(zip(data, names)):
                
                self.addLayer(n, d, pen=(i,c))                                

        #UPDATE CURVE NAMES:
        display.stack.sigLayerNameChanged.connect(
                lambda index, txt, self=self: self.curves[index].label.setText(txt))



    def saveState(self):
        state = DisplayWidget.saveState(self)
        state['view'] = self.view.vb.getState()
        state['layerNames'] = [c.label.text for c in self.curves]
        for n, c in enumerate(self.curves):
            state['%i_x' %n] = c.xData
            state['%i_y' %n] = c.yData
        return state


    def restoreState(self, state):
        self.clear()

        self.view.vb.setState(state['view'])
        names = state['layerNames']
        #DATA
        for n, name in enumerate(names):
            x,y = state['%i_x' %n], state['%i_y' %n]
            self.addLayer(name, data=(x,y))
            
        DisplayWidget.restoreState(self, state)





# 
#     def save(self, session, path):
#         l = {}
#         l['view'] = self.view.vb.getState()
#         l['layerNames'] = [c.label.text for c in self.curves]
#         session.addContentToSave(l, *path+('widget.txt',))
#         #DATA
#         p = session.createSavePath(*path+('data',''))
#         
#         def saveInThread():
#             for n, c in enumerate(self.curves):
#                 np.save(p.join('%s.npy'%n),[c.xData, c.yData])
#         
#         #this one can take time, so:
#         session.saveThread.tasks.append(saveInThread)      
# 
#         DisplayWidget.save(self, session, path)
# 
# 
#     def restore(self, session, path):
#         self.clear()
# 
#         l =  eval(session.getSavedContent(*path+('widget.txt',)) )
#         self.view.vb.setState(l['view'])
#         names = l['layerNames']
#         #DATA
#         for n, name in enumerate(names):
#             data = np.load(session.getSavedFile(*path+('data/%s.npy' %n,)))
#             self.addLayer(name, data=tuple(data))
#         
#         DisplayWidget.restore(self, session, path)
    

    def clear(self):
        for i in range(len(self.curves)):
            self.removeLayer(i)    


    def close(self):
        self.clear()#free memory
        try:
            pgPlotWidget.close(self)
        except TypeError:
            pass


    def getData(self, index=None):
        '''
        return listOf(x_vals, v_vals)
        '''
        if index is None:
            return self.data
        return self.data[index]

            
    def removeLayer(self, index, toMove=False):
        c = self.curves.pop(index)
        self.data.pop(index)
        if toMove:
            self._movedCurve = c

        self.view.legend.removeItem(c.label.text)
        self.removeItem(c)


    def insertLayer(self, index, name, data=None, **kwargs):
        if not 'pen' in kwargs:
            kwargs['pen'] = (len(self.curves)%10)
        plotItem = self.plot(name=name, **kwargs) 
        if data is not None:
            #this should word, but doesn't 
#             if isinstance(data,_PlotData):
            #working but uncool workaround:
            if data.__class__.__name__.endswith('_PlotData'):
            
                p = data
                x,y = p.item.xData, p.item.yData
            else:
                if type(data) in (tuple, list):
                    x = data[0]
                    y = data[1]
                elif isinstance(data, np.ndarray) and len(data.shape) == 2:
                    x = data[:,0]
                    y = data[:,1]
                else:
                    y = data
                    x = range(len(data))
                
                p = _PlotData(plotItem)
            plotItem.setData(x,y)
        else:
            p = _PlotData(plotItem)
        self.data.append(p)

        self.curves.insert(index, plotItem) 
        plotItem.label = self.plotItem.legend.getLabel(plotItem)
        return plotItem#weakref.proxy(plotItem)


    def insertMovedLayer(self, index):
        self.addItem(self._movedCurve, params={})
        self.curves.insert(index, self._movedCurve)
        del self._movedCurve 


    def addLayer(self, name='unnamed', data=None, **kwargs):
        return self.insertLayer(len(self.curves), name, data, **kwargs)


    def update(self, data=None, index=None, label=None, **kwargs):
        if data is not None:
            if data is self.data:#own plotdata
                return
            if index is not None:
                if isinstance(data, _PlotData):
                    x = data.item.xData
                    y = data.item.yData
                else:
                    x,y = data[0], data[1]
                self.curves[index].xData = x
                self.curves[index].yData = y
                self.data[index].changed = True
                if label is not None:
                    self.curves[index].label.setText(label)
            else:
                l = len(data)
                for n,d in enumerate(data):

                    if isinstance(data, _PlotData):
                        x = data.item.xData
                        y = data.item.yData
                    else:
                        x,y = d[0], d[1]
                    try:
                        c = self.curves[n]
                        c.xData = x
                        c.yData = y
                        self.data[n].changed = True
                    except IndexError:
                        self.addLayer(data=(x,y), pen=(n,l))
                    if label is not None:
                        self.curves[n].label.setText(label[n])


    def updateView(self, force=False):
        for n,d in enumerate(self.data):

            if d.changed:
                #ensure that updateItems gets the new x and yData:
                self.curves[n].xDisp = None
                
                self.curves[n].updateItems() 
                d.changed = False



class _PlotData(object):
    '''
    Convenience class for easy and fast access to the plot data
    Access normally through the automation script.
    
    to access all layers, use 'd.l' (=display.layer)
    to access on specific layer use 'd.l2' or 'd.l[2]'
    
    to change x or y values, do sth. like:
    d.l.y += 100  or d.l2.x[:10]*=2
    
    also slicing and interaction with each other are possible:
    
    d.l0[:10] += d.l10[:10]
    '''

    def __init__(self, plotItem, key=None):
        self.item = plotItem
        self.key = key
        self.changed = False


    @property
    def shape(self):
        return (2, len(self.item.yData))
    
    
    @property
    def dtype(self):
        return self.item.yData.dtype


    @property
    def x(self):
        if self.key is not None:
            return self.item.xData[self.key]
        else:
            return self.item.xData  
    @x.setter
    def x(self, val):
        if not isinstance(val,(np.ndarray, ProxyList)):
            raise Exception('use x[:] to change all x values')
        if self.key is not None:
            self.item.xData[self.key] = val
        else:
            self.item.xData = val
        self.changed = True

    
    @property
    def y(self):
        if self.key is not None:
            return self.item.yData[self.key]
        else:
            return self.item.yData
    @y.setter
    def y(self, val):
        if not isinstance(val,(np.ndarray, ProxyList)):
            raise Exception('use y[:] to change all y values')
        if self.key is not None:
            self.item.yData[self.key] = val
        else:
            self.item.yData = val
        self.changed = True


    def copy(self):
        return np.array([self.item.xData, self.item.yData])


    def __iadd__(self, val):
        self.y += self._getY(val)
        return self
 

    def __isub__(self, val):
        self.y -= self._getY(val)
        return self


    def __imul__(self, val):
        self.y *= self._getY(val)
        return self


    def __idiv__(self, val):
        self.y /= self._getY(val)
        return self

    def __truediv__(self, val):
        self.y /= (self._getY(val))
        return self

    def _getY(self, val):
        if isinstance(val, _PlotData):
            if (val.x==self.x).all():
                return val.y
            else:
                return interp1d(val.x, val.y, kind='cubic', bounds_error=False)(self.x)
        return val

    
    def __getitem__(self, key):
        return _PlotData(self.item, key)
        
        
    def __len__(self):
        return len(self.x)
    
    
    def __repr__(self):
        return 'x: %s\n\ty:%s' %(self.x.__repr__(), self.y.__repr__())
