import pyqtgraph_karl as pg
from pyqtgraph_karl.Qt import QtGui
#OWN
from dataArtist.widgets.Tool import Tool



class Drill(Tool):
    '''
    Plot the stack changes of a chosen pixel
    '''
    icon = 'drill.svg'
    
    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)

        self.scene = self.view.scene()
        
        #MENU:
        self.a_newDisplay = QtGui.QAction('result in new display', self)
        self.a_newDisplay.setCheckable(True)
        self.addAction(self.a_newDisplay)
     
        a_show = QtGui.QAction('show', self)
        a_show.setCheckable(True)
        a_show.setChecked(True)
        a_show.toggled.connect(self.toggleShow)
        self.addAction(a_show)

        self.n_slices = 0
        self.slave = None
        
        self._POIS = []


    def toggleShow(self, checked):
        [p.toggleShow(checked) for p in self._POIS]


    def activate(self):
        if self.display.widget.image.ndim < 3:
            raise Exception('need a 3d-image for the z-stack tools')
        
        self.setChecked(True)
        name = 'Drill[%s]' %str(self.n_slices+1)

        x_axis = self.display.axes.copy(index=('stack',0))
        if (not self.slave or self.slave.isClosed()) or self.a_newDisplay.isChecked():
            self.slave = self.display.workspace.addDisplay(
                            axes=x_axis, 
                            data=None, 
                            title=name)

        #take middle of current position
        r = self.display.widget.view.vb.viewRange()  
        p = ((r[0][0]+r[0][1])/2, (r[1][0]+r[1][1])/2)

        self._POIS.append(
                _POI(self, name, 
                     p,pen=(self.n_slices%6) ) 
                         )
               
        self.n_slices += 1
        self.slave.addLayer(label=name, info='Drill')



class _POI(pg.ROI):
    '''
    ROI that only shows its one translation handle
    coloured with the given pen
    
    * it creates a plot layer in the slaveDisplay.widget
       that is updates when the handle is moved
    * it is removed, it the slaveDisplay is removed
    '''
    def __init__(self, tool, name, pos, pen):
        super(_POI, self).__init__(pos, size=[0,0])
        
        self.handlePen = pen
        self.addTranslateHandle([0.5, 0.5])

        self._name = name
        self.tool = tool
        self.view = tool.view
        self.slaveDock = tool.slave
        self.master = tool.display.widget
        self.masterDisplay = tool.display
        slave = self.slaveDock.widget

        #PLOT
        self.plot = slave.addLayer(name=self._name, pen=pen)
        #LABEL
        self.text = pg.TextItem(
            text=self._name, 
            color=(0,0,0), 
            html=None, 
            anchor=(0, 0),
            border=None, 
            fill=pg.mkBrush(255, 255, 255, 80), 
            angle=0)
        #CONNECT
        self.slaveDock.closed.connect(lambda: self.toggleShow(False))
        self.sigRegionChanged.connect(self.updateView)
        #UPDATE
        self.updateView()
        self.toggleShow()
    
    
    def toggleShow(self, show=True):
        if show:
            self.master.addItem(self.text)    
            self.master.addItem(self)
        else:
            self.master.removeItem(self.text)    
            self.master.removeItem(self) 
       
          
    def updateView(self):
        p = self.boundingRect().center() + self.pos()

        x = int(p.x())
        y = int(p.y())
        if x == 0 or y == 0:
            return
        try:
            z_values = self.master.image[:, x, y]
            
            self.plot.setData(x=self.masterDisplay.stack.values, y=z_values)
            self.plot.label.setText('%s: [%s, %s]' %(self._name, x, y))
            self.text.setPos(p)
        except IndexError:
            pass