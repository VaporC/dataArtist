import numpy as np
from pyqtgraph_karl import PolyLineROI

#OWN
from dataArtist.widgets.Tool import Tool
from imgProcessor.measure.sharpness.SharpnessfromPoints import SharpnessfromPointSources
from dataArtist.figures.image.tools.globals.CalibrationFile import CalibrationFile



class PointSpreadFunction(Tool):
    '''
    Calculate the point spread function / absolute sharpness of an image
    '''
    icon = 'pointSpreadFunction.svg'

    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)

        self.quadROI = None
        self.outDisplay = None
        self.stdDisplay = None

        self.calFileTool = self.showGlobalTool(CalibrationFile)

        pa = self.setParameterMenu() 
        
        pMeasure = pa.addChild({
            'name':'Calculate calibration array ...',
            'type':'empty'})
        
        self.createResultInDisplayParam(pMeasure)

        self.pMethod = pMeasure.addChild({
            'name':'Method',
            'type':'list',
            'value':'multiple pin holes',
            'limits':['multiple pin holes']})

#         self.pBg = pa.addChild({
#             'name':'Optional: background image(s)',
#             'type':'menu',
#             'tip': 'if given do background subtraction',
#             'value':'from display'}).aboutToShow.connect(
#                 lambda m, fn=self._fromDisplay:
#                             self.buildOtherDisplayLayersMenu
#                             (m,fn, includeThisDisplay=True))

        pSetBoundaries = pMeasure.addChild({
            'name':'Set boundaries',
            'type':'action'})
        pSetBoundaries.sigActivated.connect(self._setBoundaries)

        self.pShowStd = pMeasure.addChild({
            'name':'Show standard deviation',
            'type':'bool',
            'value':False})

        self.pKSize = pMeasure.addChild({
            'name':'Maximum kernel size (mxm)',
            'type':'int',
            'value':51,
            'limits':[7,101]})

        self.pDrawPoints = pMeasure.addChild({
            'name':'Draw found points',
            'type':'bool',
            'value':False})

        self.pFilterLow = pMeasure.addChild({
            'name':'Filter low values [n std]',
            'type':'slider',
            'value':1.5,
            'limits':[0,3],
            'visible':False})
        self.pFilterLow.sigValueChanged.connect(self._updatePSF)

        self.pUpdate = pMeasure.addChild({
                    'name':'Update calibration',
                    'type':'action',
                    'visible':False})
        self.pUpdate.sigActivated.connect(self.updateCalibration)


        pa.addChild({
            'name':'Load calibration array ...',
            'type':'menu',
            'value':'from display'}).aboutToShow.connect(
                lambda m, fn=self._fromDisplay:
                            self.buildOtherDisplayLayersMenu(
                                    m,fn, includeThisDisplay=True))


    def _fromDisplay(self, display,n,layername):
        im = display.widget.image[n]
        self.calFileTool.updatePSF(im)


    def _updatePSF(self, p,v):
        if not self.outDisplay or self.outDisplay.isClosed():
            return
        out = self.sharp.psf(filter_below=v)    
        self.outDisplay.widget.update(out)


    def _setBoundaries(self, param):
        if not self.quadROI:
            self._createROI()
            param.setName('Show/Hide boundaries')
        elif self.quadROI.isVisible():
            self.quadROI.hide()
        else:
            self.quadROI.show()


    def _createROI(self):
        w = self.display.widget
#         s = w.image.shape[1:3]
        r = self.display.widget.view.vb.viewRange()  
        p = ((r[0][0]+r[0][1])/2, (r[1][0]+r[1][1])/2)
        s = [(r[0][1]-r[0][0])*0.1, (r[1][1]-r[1][0])*0.1]
        
        #if w.image.ndim == 3:
        #    s = s[1:]
        if not self.quadROI:
            self.quadROI = PolyLineROI([
                            [p[0]-s[0],p[1]-s[1]],
                            [p[0]+s[0],p[1]-s[1]],
                            [p[0]+s[0],p[1]+s[1]],
                            [p[0]-s[0],p[1]+s[1]],
                            
                                        
                                        
#                                         [s[0]*0.2, s[1]*0.2], 
#                                         [s[0]*0.8, s[1]*0.2], 
#                                         [s[0]*0.8, s[1]*0.8],
#                                         [s[0]*0.2, s[1]*0.8]
                                        
                                        ], 
                                       closed=True,
                                       pen='r')
            self.quadROI.translatable = False
            self.quadROI.mouseHovering = False
            #PREVENT CREATION OF SUB SEGMENTS:
            for s in self.quadROI.segments:
                s.mouseClickEvent = lambda x:None

            w.view.vb.addItem(self.quadROI)    


    def deactivate(self):
        #show tool activated to highlight this one against PSF tools
        #in other displays
        pass


    def activate(self):
        if self.quadROI is None:
            print 'need to set boundaries first'
            return self._createROI()
        
        p = self.quadROI.pos()
        x0 = p.x()
        y0 = p.y()
        #has to be y,x due to different conventions:        
        corners = np.array( [( h['pos'].y()+y0, h['pos'].x()+x0 )  
                               for h in self.quadROI.handles] )

        std = self.pShowStd.value()
        
        self.sharp = SharpnessfromPointSources(
                        max_kernel_size=self.pKSize.value(),
                        calc_std=std)
        
        w = self.display.widget
        for i in w.image:
            self.sharp.addImg(i, corners)
            if self.pDrawPoints.value():
                lay = self.sharp.drawPoints(img=False)
                w.addColorLayer(lay, name='found PSF pin holes')
               
        if self.outDisplay is None or self.outDisplay.isClosed():
            self.outDisplay = self.display.workspace.addDisplay( 
                            axes=(3), 
                            title='Point spread function')
            
        out = self.sharp.psf(filter_below=self.pFilterLow.value())    
        self.outDisplay.addLayer(data=[out], label='PSF')
        #make filtering low values less painfull:
        self.outDisplay.widget.setOpts(autoLevels=False,
                                 autoHistogramRange=False)
        
        self.pFilterLow.show()
        self.pUpdate.show()
        
        if std:
            trend, offs = self.sharp.std()
            self.stdDisplay = self.display.workspace.addDisplay( 
                            axes=2,
                            data=offs, 
                            names=('LSF-std', 'LSF', 'LSF+std'),
                            title='LSF +-std // Point spread function ')
            self.stdDisplay2 = self.display.workspace.addDisplay( 
                            axes=2,
                            data=[trend], 
                            title='STD.sum() trend // Point spread function')



    def updateCalibration(self):
        w = self.outDisplay.widget
        im = w.image
        if im.ndim == 3:
            im = im[w.currentIndex]
        self.calFileTool.updatePSF(im)