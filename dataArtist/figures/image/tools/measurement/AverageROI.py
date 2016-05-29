import numpy as np

#OWN
from dataArtist.functions import RMS
from _ROI import ROITool, ROIArea


class AverageROI(ROITool):
    '''
    add averaged regions of interest (ROI)
    '''
    icon = 'ROI.svg'
    def __init__(self, imageDisplay):
        ROITool.__init__(self, imageDisplay)

        self.ROI01Slave = None
        self.stdSlave = None
        self.rmsSlave = None

        self.pAveraging = self._menu.p.insertChild(0,{
            'name': 'Averaging',
            'type': 'list',
            'value':'one side',
            'limits':['No', 'one side', 'both sides']})
        self.pAveraging.sigValueChanged.connect(lambda param, value: 
                        [ch.show(value != 'No') for ch in param.children()] )
        
        self.pRotatable = self._menu.p.insertChild(1,{
            'name': 'Rotatable',
            'type': 'bool',
            'value':False})
        self.pRotatable.sigValueChanged.connect(lambda param, value: 
                        [ch.show(not value) for ch in param.children()] )

        self.pAvDirection = self.pRotatable.addChild({
            'name': 'Averaging direction',
            'type': 'list',
            'value':'vertical',
            'limits':['vertical', 'horizontal']})

        self.pStd = self.pAveraging.addChild({
            'name': 'show standard deviation',
            'type': 'bool',
            'value':False,
            'visible':False})
        
        self.pRMS = self.pAveraging.addChild({
            'name': 'show RMS',
            'type': 'bool',
            'value':False,
            'visible':False,
            'tip':'Root Mean Square'})


    def activate(self):
        pa = self.pAveraging.value() 
        slave = None
        #CHOOSE THE ROI TYPE:
        if pa == 'No':
            ROI = _ROI2d    
            iaxes = None
        else:
            #USE THE LAST ROI SLAVE DISPLAY IF APPLICABLE:
            if self.ROI01Slave and not self.ROI01Slave.isClosed():
                slave = self.ROI01Slave
                         
            if pa == 'one side':
                ROI = _ROI1d
                if self.pAvDirection.value() == 'vertical':
                    iaxes = (0,1)
                else:
                    iaxes = (1,0)
            else:
                ROI = _ROI0d
                iaxes = ('stack',0)
        
        name = '%s[%s]' %(ROI.name, str(len(self.ROIs)+1))

        if slave is None:
            #CREATE A NEW SLAVE DISPLAY
            slave = self.display.workspace.addDisplay( 
                        axes=self.display.axes.copy(iaxes), 
                        title='%s of %s' %(name, self.display.shortName()) 
                                              )
        #REMEMBER THIS DISPLAY FOR LATER REUSE:                               
        if pa != 'No':
            self.ROI01Slave = slave

        #STANDARD DEVIATION
        if self.pStd.value():
            stdname = 'st.Dev[%s]' %str(len(self.ROIs)+1)
            if not self.stdSlave or self.stdSlave.isClosed():
                self.stdSlave = self.display.workspace.addDisplay( 
                        axes=self.display.axes.copy(('stack',0)), 
                        title='%s of %s' %(stdname, self.display.shortName()) ) 

        #RMS
        if self.pRMS.value():
            rmsname = 'RMS[%s]' %str(len(self.ROIs)+1)
            if not self.rmsSlave or self.rmsSlave.isClosed():
                self.rmsSlave = self.display.workspace.addDisplay( 
                        axes=self.display.axes.copy(('stack',0)), 
                        title='%s of %s' %(rmsname, self.display.shortName()) ) 
     
        #SET DATA:
        w = self.display.widget
        if not self.pPlotAll.value():
            index = w.currentIndex
        else:
            index = None
                #take middle of current position
        r = self.display.widget.view.vb.viewRange()  
        p = ((r[0][0]+r[0][1])/2, (r[1][0]+r[1][1])/2)
        s = [(r[0][1]-r[0][0])*0.1, (r[1][1]-r[1][0])*0.1]
        #CREATE NEW ROI:
        roi = ROI(self, 
                    self.display, 
                    slave, 
                    name, 
                    index=index,
                    pen=(len(self.ROIs)%6),
                    pos=p,
                    size=s
                  )
        
        self.ROIs.append(roi)
        return roi



class _ROIAverage(ROIArea):
    
    def setup(self):
        ROIArea.setup(self)

        self.stdPlot = None
        self.rmsPlot = None
        self.plots = []
        
        self.averaging = self.tool.pAveraging.value()
        self.calcVariance = self.tool.pStd.value()
        self.calcRMS = self.tool.pRMS.value()  

        self.master.addItem(self.text)
        self.master.addItem(self)
 
        #CREATE ROI SHAPE
        rotation = self.tool.pRotatable.value()
        if rotation:
            self.addScaleRotateHandle([0, 0.5], [1, 0.5])
            self.addScaleRotateHandle([1, 0.5], [0, 0.5])
            self.addScaleHandle([0.5, 1], [0.5, 0.5])
        else:
            self.addScaleHandle([1, 1], [0,0])
        self.setupUpdateView(rotation)


    def getSymbol(self):
        return None



class _ROI1d(_ROIAverage):
    '''
    line plot ROI
    '''
    name = 'LinePlot'
    

    def setupUpdateView(self, rotation):
        self._rotation = rotation
        if not rotation:
            self.av_dir = 1 if self.tool.pAvDirection.value() == 'vertical' else 0


    def setup(self):
        '''
        remove old plots
        add multiple plots if multiple images and all layers should be used
        else add one plot
        '''
        _ROIAverage.setup(self)
        
        self.rmsPlots = []
        self.stdPlots = []
        l = len(self.img) if self.img.ndim == 3 else 1
        unit = self.masterDisplay.axes.stackAxis.pUnit.value()
        if unit:
            unit = ' [%s]' %unit
        for n,val in enumerate(self.masterDisplay.stack.values):
            name = '%s%s' %(val,unit)
            #ROI
            plot = self.slaveDisplay.addLayer(label=name, 
                                              info='one dimension averaged', 
                                              pen=self._pen+l-n-1 )
            self.plots.append(plot)
            #STD
            p=None
            if self.tool.pStd.value():
                p = self.tool.stdSlave.addLayer(label='Std[%s] of %s' %(n, name), 
                                                info='Standard deviation', 
                                                pen=self._pen+l-n-1 )        
            self.stdPlots.append(p)
            #RMS
            p=None
            if self.tool.pRMS.value():
                p = self.tool.rmsSlave.addLayer(label='RMS[%s] of %s' %(n, name),
                                                info='root mean square', 
                                                pen=self._pen+l-n-1 )        
            self.rmsPlots.append(p)


    def updateView(self):
        if self._rotation:
            return self._updateViewRotable()
        return self._updateViewStatic()


    def _updateViewStatic(self):
        #COORDS
        px,py = self.pos().x(), self.pos().y()
        r = self.boundingRect()
        x0,y0,x1,y1 = r.getCoords()
        x0 = max(0,int(round(x0+px)))
        x1 = int(round(x1+px))
        y0 = max(0,int(round(y0+py)))
        y1 = int(round(y1+py))
        #TEXT
        #self.text.setText('%s (%s,%s)-(%s,%s)' %(self.name(), x0,y0,x1,y1) )
        self.text.setPos(px,py)
        
        simg = self.img
        if simg.ndim == 2:
            simg = [simg]
            
        for img, plot, vplot, rplot in zip(simg, self.plots, 
                                           self.stdPlots, self.rmsPlots):
            #DATA
            try:
                dataorig = img[x0:x1, y0:y1]
                if dataorig.ndim == 3:#color
                    data = np.mean(dataorig, axis=(self.av_dir,2))
                else:
                    data = dataorig.mean(axis=self.av_dir)
                    
                if self.av_dir == 1:
                    xvals = np.linspace(x0,x1, len(data))
                else:
                    xvals = np.linspace(y0,y1, len(data))

                plot.setData(y=data, x=xvals)

                if vplot:
                    vplot.setData(y=dataorig.var(axis=self.av_dir), 
                                  x=xvals, 
                                  symbol=self.getSymbol())
                if rplot:
                    rplot.setData(y=RMS(dataorig, axis=self.av_dir), 
                                  x=xvals, 
                                  symbol=self.getSymbol())

            except (IndexError, ValueError): # out out bounds
                pass
            

    def _updateViewRotable(self):
        simg = self.img
        if simg.ndim == 2:
            simg = [simg]
            
        for img, plot, vplot, rplot in zip(simg, self.plots, 
                                           self.stdPlots, self.rmsPlots): 

            data, coords = self.getArrayRegion(img.view(np.ndarray), 
                                               self.master.imageItem, axes=(0,1), 
                                               returnMappedCoords=True)
            dataorig = data#np.copy(data)
            if data is not None:
                while data.ndim > 1:
                    #average rectangle to line
                    data = data.mean(axis=1)
                while coords.ndim > 2:
                    coords = coords[:,:,0]
                coords = coords - coords[:,0,np.newaxis]
                xvals = (coords**2).sum(axis=0) ** 0.5
                plot.setData(y=data, x=xvals)

            if vplot:
                vplot.setData(y=dataorig.var(axis=1), 
                              x=xvals, 
                              symbol=self.getSymbol())
            if rplot:
                rplot.setData(y=RMS(dataorig, axis=1), 
                              x=xvals, 
                              symbol=self.getSymbol())

        p = self.boundingRect().bottomLeft() + self.pos()
        self.text.setPos(p)



class _ROI0d(_ROIAverage):
    name = 'Average'


    def getSymbol(self):
        return 'o'


    def setup(self):
        '''
        remove old plots
        add multiple plots if multiple img and all layers should be used
        else add one plot
        '''
        _ROIAverage.setup(self)
        
        name = 'Average[%s]' %str(len(self.tool.ROIs)+1)
        
        self.plot = self.slaveDisplay.addLayer(
                                label=name, 
                                info='averaged', 
                                pen=self._pen)        

        if self.tool.pStd.value():
            name = 'Standard Deviation[%s]' %str(len(self.tool.ROIs)+1)
            self.stdPlot = self.tool.stdSlave.addLayer(
                                label=name, 
                                info='stDev', 
                                pen=self._pen)        

        if self.tool.pRMS.value():
            name = 'RMS[%s]' %str(len(self.tool.ROIs)+1)
            self.rmsPlot = self.tool.rmsSlave.addLayer(
                                label=name, 
                                info='root mean square', 
                                pen=self._pen)        
      

    def updateView(self):
        x_vals = self.tool.display.stack.values 
        data =  []
        #DATA
        def getData(img):
            d = self.getArrayRegion(img.view(np.ndarray), 
                                    self.master.imageItem, axes=(0,1))                   
            if d is not None:
                data.append(d)
        
        if  self.img.ndim > 2:     
            for layer in self.img:
                getData(layer)
        else:
            getData(self.img)
            
        #MEAN
        mean =  [d.mean() for d in data]   
        self.plot.setData(y=mean, 
                          x=x_vals, 
                          symbol=self.getSymbol())
        #STD
        if self.stdPlot:
            self.stdPlot.setData(y=[d.std() for d in data], 
                                 x=x_vals, 
                                 symbol=self.getSymbol())
        #RMS
        if self.rmsPlot:
            self.rmsPlot.setData(y=[RMS(d)-m for d,m in zip(data, mean)], 
                                 x=x_vals, 
                                 symbol=self.getSymbol())



class _ROI2d(_ROIAverage):
    '''
    a 2d ROI or excerpt of the original image
    '''
    name = 'Focus'

    def setup(self):
        _ROIAverage.setup(self)
        for n in self.masterDisplay.layerNames():
            self.slaveDisplay.addLayer(label='%s - %s' %(self.name,n))
 

    def setupUpdateView(self, rotation):
        self._rotation = rotation


    def updateView(self):
        if self._rotation:
            self._updateViewRotable()
        else:
            self._updateViewStatic()


    def _updateViewRotable(self):
        #AXES
        if self.img.ndim == 2:
            ax = (0,1)
        else:
            ax = (1,2)
        #DATA
        data = self.getArrayRegion(self.img.view(np.ndarray), 
                                   self.master.imageItem, axes=ax)
        self.slaveDisplay.widget.setImage(data)

        #TEXT
        #s = self.size()
        p1 = self.pos()
        #p2 = p1+s
        self.text.setPos(p1.x(),p1.y())        
#         self.text.setText('%s (%s,%s)-(%s,%s)' %(self.roiName(), 
#                                     int(round(p1.x())),int(round(p1.y())),
#                                     int(round(p2.x())),int(round(p2.y()))) )


    def _updateViewStatic(self):
        #COORDS
        px,py = self.pos().x(), self.pos().y()
        r = self.boundingRect()
        x0,y0,x1,y1 = r.getCoords()
        x0 = int(round(x0+px))
        x1 = int(round(x1+px))
        y0 = int(round(y0+py))
        y1 = int(round(y1+py))
        #TEXT
        #self.text.setText('%s (%s,%s)-(%s,%s)' %(self.roiName(), x0,y0,x1,y1) )
        self.text.setPos(px,py)
        #DATA
        try:
            img_cut = self.img[:, x0:x1, y0:y1]
            w = self.slaveDisplay.widget
            w.image = img_cut
            w.updateView(force=True)
        except (IndexError, ValueError): # out out bounds
            pass