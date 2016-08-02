import numpy as np

#OWN
from imgProcessor.camera.DarkCurrentMap \
    import getDarkCurrentFunction, getDarkCurrentAverages

from dataArtist.widgets.ImageTool import ImageTool
from dataArtist.figures.image.tools.globals.CalibrationFile import CalibrationFile



class DarkCurrent(ImageTool):
    '''
    Averages multiple dark current images (including STE removal)
    or calculate a dark current function as f(t) = a + b*t
    
    NEEDS EXPOSURE TIMES [s] SET FOR ALL IMAGES AS STACK VALUE!
    Works on unloaded images as well.
    
    '''
    icon = 'darkCurrent.svg'

    def __init__(self, imageDisplay):
        ImageTool.__init__(self, imageDisplay)
        
        self.calFileTool = self.showGlobalTool(CalibrationFile)
        self.pa = self.setParameterMenu() 

        self._bg = None
        self._method = None
        self._inter, self._slope = None, None

        pMeasure = self.pa.addChild({
            'name':'Calculate calibration array ...',
            'type':'empty'})

        self.createResultInDisplayParam(pMeasure)

        self.pMethod = pMeasure.addChild({
            'name':'Method',
            'type':'list',
            'value':'as function',
            'limits':['average', 'as function']})

        pMeasure.addChild({
            'name':'Exposure times [s]',
            'type':'str',
            'value':'... are taken from layer value',
            'readonly':True})


        pFromDisplay = self.pa.addChild({
            'name':'Load calibration array ...',
            'type':'empty'})

        pFromDisplay.addChild({
            'name':'Intercept',
            'type':'menu',
            'value':'from display'}).aboutToShow.connect(
                lambda m, fn=self._interceptfromDisplay:
                            self.buildOtherDisplayLayersMenu(m,fn, includeThisDisplay=True))

        pFromDisplay.addChild({
            'name':'Slope',
            'type':'menu',
            'value':'from display'}).aboutToShow.connect(
                lambda m, fn=self._slopefromDisplay:
                            self.buildOtherDisplayLayersMenu(m,fn, includeThisDisplay=True))

        self.pUpdate = self.pa.addChild({
            'name':'Update calibration',
            'type':'action',
            'visible':False})
        self.pUpdate.sigActivated.connect(self.updateCalibration)


    def _interceptfromDisplay(self, disp,n,layername):
        self._inter = self.display.widget.image[n]
        if self._slope is not None:
            self.pUpdate.show()

    def _slopefromDisplay(self, disp,n,layername):
        self._slope = self.display.widget.image[n]
        if self._inter is not None:
            self.pUpdate.show()


    def updateCalibration(self):
        if self._method == 'as function':
            self.calFileTool.updateDarkCurrent(
                            self._inter, self._slope)
        else:
            raise Exception('only [as function] implemented at the moment')


    def activate(self):   
        self._method = self.pMethod.value()
        
        #need calibration for max value
        assert self.calFileTool.curCal is not None, 'need camera calibration specified'
        
        if self._method == 'as function':
            self.startThread(self._startAsFunction,self._doneAsFunction)
        else:
            self.startThread(self._startAverage,self._doneAverage)


    def _startAsFunction(self):
        x = self.display.stack.values 
        imgs = self.getImageOrFilenames()
        mx = self.calFileTool.curCal.coeffs['max value']
        #TODO: include rmse,maxExpTime
        inter, slope, rmse = getDarkCurrentFunction(x,imgs,mxIntensity=mx)
        return inter, slope


    def _doneAsFunction(self, (inter, slope)):
        self._inter, self._slope = inter, slope
        
        self.outDisplay = self.handleOutput(
                                    [inter, slope], 
                                    names=['Intercept', 'Slope'], 
                                    title='Dark current as function')
        self.pUpdate.show()


    def _startAverage(self):
        x, imgs = self.display.stack.values, self._getImg()
        exposuretimes, imgs = getDarkCurrentAverages(x, imgs)
        return exposuretimes, imgs


    def _doneAverage(self, (exposuretimes, imgs)):
        self.outDisplay = self.handleOutput(imgs, title='Averaged dark current')
        self.outDisplay.stack.values = np.array(exposuretimes)
        self.pUpdate.show()
