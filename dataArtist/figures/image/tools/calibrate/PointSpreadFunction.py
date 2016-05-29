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

        self.calFileTool = self.showGlobalTool(CalibrationFile)

        pa = self.setParameterMenu() 
        self.createResultInDisplayParam(pa)

        self.pMethod = pa.addChild({
            'name':'Method',
            'type':'list',
            'value':'multiple pin holes',
            'limits':['multiple pin holes']})

        pSetBoundaries = pa.addChild({
            'name':'Set boundaries',
            'type':'action'})
        pSetBoundaries.sigActivated.connect(self._setBoundaries)

        self.pKSize = pa.addChild({
            'name':'Maximum kernel size (mxm)',
            'type':'int',
            'value':51,
            'limits':[7,101]})

        self.pDrawPoints = pa.addChild({
            'name':'Draw found points',
            'type':'bool',
            'value':False})

        self.pFilterLow = pa.addChild({
            'name':'Filter low values',
            'type':'slider',
            'value':0.0,
            'limits':[0,0.2],
            'visible':False})
        self.pFilterLow.sigValueChanged.connect(self._updatePSF)

        self.pUpdate = pa.addChild({
                    'name':'Update calibration',
                    'type':'action',
                    'visible':False})
        self.pUpdate.sigActivated.connect(self.updateCalibration)


    def _updatePSF(self, p,v):
        if not self.outDisplay or self.outDisplay.isClosed():
            return
        out = self.sharp.psf(filter_below=v)    
        self.outDisplay.widget.setImage(out)


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
        s = w.image.shape[1:3]
        #if w.image.ndim == 3:
        #    s = s[1:]
        if not self.quadROI:
            self.quadROI = PolyLineROI([[s[0]*0.2, s[1]*0.2], 
                                        [s[0]*0.8, s[1]*0.2], 
                                        [s[0]*0.8, s[1]*0.8],
                                        [s[0]*0.2, s[1]*0.8]], 
                                       closed=True,
                                       pen='r')
            self.quadROI.translatable = False
            self.quadROI.mouseHovering = False
            #PREVENT CREATION OF SUB SEGMENTS:
            for s in self.quadROI.segments:
                s.mouseClickEvent = lambda x:None

            w.view.vb.addItem(self.quadROI)    


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
        
        self.sharp = SharpnessfromPointSources(
                        max_kernel_size=self.pKSize.value())
        
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
        self.outDisplay.addLayer(data=out, label='PSF')
        
        self.pFilterLow.show()
        self.pUpdate.show()


    def updateCalibration(self):
        w = self.outDisplay.widget
        im = w.image[w.currentIndex]
#         if im.ndim == 3:
#             im = im[w.currentIndex]
        self.calFileTool.updatePSF(im)