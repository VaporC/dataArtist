import numpy as np


from skimage.restoration.deconvolution import wiener
from math import radians

#OWN
from dataArtist.widgets.Tool import Tool
from dataArtist.figures.image.tools.globals.CalibrationFile import CalibrationFile
from fancytools.math.rotatePolygon import rotatePolygon



def roiCorners(roi):
    #returns all corners of a ROI
    p = roi.pos()
    s = roi.size()
    a = roi.angle()
    q = np.empty((4,2))
    q[0] = p
    q[1] = p[0]+s[0],p[1]
    q[2] = p[0]+s[0],p[1]+s[1]
    q[3] = p[0]     ,p[1]+s[1]
    return rotatePolygon(q, radians(a), q[0].copy())
    


class DeconvolutionBalance(Tool):
    '''
    Find the best balance value (sharpness vs. deconvolution noise)
    through varying balance values on on an ROI of a test image
    
    Select best image and click update calibration.
    
    
    WARING: executing the tool on the full image might take some time.
    '''
    icon = 'sharpnessBalance.svg'

    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)

        self.calFileTool = self.showGlobalTool(CalibrationFile)

        pa = self.setParameterMenu() 
        self.createResultInDisplayParam(pa, value='[NEW, ADD]')
        
        pB = pa.addChild({
            'name':'Balance value range',
            'type':'group'})
        self.pBFrom = pB.addChild({
            'name':'from',
            'type':'float',
            'value':0.001,
            'limits':[0,1]})  
        self.pBTo = pB.addChild({
            'name':'to',
            'type':'float',
            'value':0.02,
            'limits':[0,1]})       
        self.pn = pa.addChild({
            'name':'N steps',
            'type':'int',
            'value':10,
            'limits':[3,1000]})        
        self.pUpdate = pa.addChild({
            'name':'Update Calibration',
            'type':'action',
            'visible':False}) 
        self.pUpdate.sigActivated.connect(self.updateCalibration)   


    def _bRange(self):
        return np.linspace(self.pBFrom.value(),
                               self.pBTo.value(),
                               self.pn.value())


    def activate(self):
        psf = self.calFileTool.getCurrentCoeff('psf')
        self.startThread(lambda: self._process(psf),self._done)      
        
        
    def _process(self, psf):  
        w = self.display.widget
        img = w.image

        img = img[w.currentIndex].copy()
        #Wiener method needs image scaled (-1,1):
        mn, mx = img.min(), img.max()
        img-=mn
        img/=(mx-mn)
         
        vals = self._bRange()
        out = []        
        for balance in vals:
            o = wiener(img, psf, balance)
            #Scale back:
            o[o<0]=0
            o*=(mx-mn)
            o+=mn
            out.append(o)
        return out, ['Balance=%s' %v for v in vals]


    def _done(self, (out, names)):
        d = self._outDisplay = self.handleOutput(out, names=names)
        self.pUpdate.show()
        d.pTitleFromLayer.setValue(True)
        print 'Now find the best balance value and click on update calibration'
        
        
    def updateCalibration(self):
        val = self._bRange()[self._outDisplay.widget.currentIndex]
        self.calFileTool.updateDeconvolutionBalance(val)