import numpy as np
from pyqtgraph_karl.Qt import QtGui, QtCore

from scipy.optimize import curve_fit
from scipy.misc import factorial

from collections import OrderedDict

#OWN
from dataArtist.widgets.Tool import Tool

#TODO: make more functions / currently only poisson supported

class Fit(Tool):
    '''
    Fit points to a given function/distribution
    '''
    icon = 'fit.svg'
    
    def __init__(self, plotDisplay):
        Tool.__init__(self, plotDisplay)
        
        self.guess = None
        
        pa = self.setParameterMenu() 

        self.pPlot = pa.addChild({
            'name':'Plot',
            'type':'list',
            'value':'All'}) 

        XVals = pa.addChild({
            'name':'X values',
            'type':'empty',
            'isgroup':True}) 
        
        self.pXFrom = XVals.addChild({
            'name':'From',
            'type':'float',
            'value':0}) 

        self.pXTo = XVals.addChild({
            'name':'To',
            'type':'float',
            'value':100}) 
        
        self.pXN = XVals.addChild({
            'name':'Number',
            'type':'int',
            'value':100,
            'limits':[2,10000]}) 

        self.pMethod = pa.addChild({
            'name':'Method',
            'type':'list',
            'value':'Poisson',
            'limits':['Poisson']})         

        pManual = pa.addChild({
            'name':'Manually set initial guess',
            'type':'action'}) 
        
        pManual.sigActivated.connect(self._manualSetInitGuess)
  
        self._menu.aboutToShow.connect(self._updateMenu)
  

    def activate(self):
        if self.pMethod.value() == 'Poisson':
            v = self.pPlot.value() 
            index = None
            if v != 'All':
                # index here if specific plot chosen
                index = self.pPlot.opts['limits'].index(v)-1
            plots = self.display.widget.getData(index) 
            
            for plot in plots:
                # fit with curve_fit
                x,y = plot.x, plot.y
                if not self.guess:
                    self.guess = _Poisson.initGuess(x,y)
                parameters, cov_matrix = curve_fit(_Poisson.function, x, y, self.guess) 
                # plot poisson-deviation with fitted parameter
                x_vals = self._getXVals()
                y_vals = _Poisson.function(x_vals, *parameters)
                self.display.addLayer(data = (x_vals, y_vals), 
                                      filename='X - Poission fitted')


    def _getXVals(self):
        return np.linspace(self.pXFrom.value(),
                           self.pXTo.value(), 
                           self.pXN.value())


    def _manualSetInitGuess(self):
        plotItem = self.display.addLayer(filename='guess')
        self.control = _ControlWidget(_Poisson.parameters, _Poisson.function, 
                                      self._getXVals(), plotItem)
        self.control.show()
        self.control.sigDone.connect(self._manualSetInitGuessDone)


    def _manualSetInitGuessDone(self, paramVals):
        self.guess = paramVals
        self.activate()


    def _updateMenu(self):
        l = ['All']
        l.extend(self.display.layerNames())
        self.pPlot.setLimits(l)


    
class _Poisson(object):
    #class for estimating initial values from data
    #and fitting data to a poisson distribution
    parameters = OrderedDict([('lambda',1),
                              ('offsX',0),
                              ('offsY',0),
                              ('scaleX',1),
                              ('scaleY',1)] )
    
    
    @staticmethod
    def initGuess(xVals, yVals):
        xmin = np.min(xVals)
        #xmax = np.max(xVals)
        offsY = np.min(yVals)
        lamb = 1#xVals[np.argmax(yVals)] # peak
        offsX = xmin
        scaleX = xVals[np.argmax(yVals)]
        scaleY = np.max(yVals)-np.min(yVals)
        return (lamb, offsX, offsY, scaleX, scaleY)
        
    
    @staticmethod
    def function(x, lamb, offsX, offsY, scaleX, scaleY):
        # poisson function, parameter lamb is the fit parameter
        x = (x - offsX)/scaleX
        y = (lamb**x/factorial(x)) * np.exp(-lamb)
        return scaleY*y + offsY



class _ControlWidget(QtGui.QWidget):
    '''
    A draggable control window with:
    * Button 'Previous'
    * Button 'Next'
    to be connected with the given functions
    '''
    sigDone = QtCore.Signal(tuple) #parameter values

    def __init__(self, parameters, function, xVals, plotItem):
        QtGui.QWidget.__init__(self)
        
        #make frame-less:
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | 
                            QtCore.Qt.WindowStaysOnTopHint)
        #TODO:
#         #go to current screen:
#         d = QtGui.QApplication.desktop()
#         n = d.screenNumber(self)
#         self.setGeometry(d.screenGeometry(n))  

        self.xVals = xVals
        self.plotItem = plotItem
        self.function = function

        layout = QtGui.QGridLayout()
        self.setLayout(layout)
        
        self.s = []#all spinboxes
        
        for n, (name, value) in enumerate(parameters.items()):
            layout.addWidget(QtGui.QLabel(name),n,0)
            s = QtGui.QDoubleSpinBox()
            s.setValue(value)
            s.setMaximum(1e6)
            s.setMinimum(-1e6)

            s.valueChanged.connect(self._valueChanged)
            layout.addWidget(s,n,1)
            self.s.append(s)
        
        btn_done = QtGui.QPushButton('Done')  
        btn_done.clicked.connect(self.done)   
        layout.addWidget(btn_done, n+1, 0, 1,2)
        
        self._valueChanged()


    def _getVals(self):
        vals = []
        for s in self.s:
            vals.append(s.value())
        return vals        


    def _valueChanged(self):
        yVals = [self.function(x, *tuple(self._getVals())) for x in self.xVals]
        
        self.plotItem.setData(self.xVals, yVals)

    def done(self):
        self.close()
        self.sigDone.emit(tuple(self._getVals()))


    #make draggable:
    def mousePressEvent(self, event):
        self.offset = event.pos()
    
    
    def mouseMoveEvent(self, event):
        x = event.globalX()
        y = event.globalY()
        x_w = self.offset.x()
        y_w = self.offset.y()
        self.move(x-x_w, y-y_w)
