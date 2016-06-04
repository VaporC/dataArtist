import pyqtgraph_karl as pg

from imgProcessor.camera import NoiseLevelFunction as NLF

#OWN
from dataArtist.widgets.Tool import Tool
from dataArtist.figures.image.tools.globals.CalibrationFile import CalibrationFile



class NoiseLevelFunction(Tool):
    '''
    Calculate the noise level function from one or more input images
    ...Works on unloaded images as well
    '''
    icon = 'noiseLevelFunction.svg'
    
    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)

        self.calFileTool = self.showGlobalTool(CalibrationFile)

        self.camera = None
        self.outDisplay = None
        self.outDisplay2 = None
        
        self._refDisplay = None

        pa = self.setParameterMenu() 

        self.pRef = pa.addChild({
            'name': 'Reference images',
            'type': 'list',
            'value':'None',
            'limits': ['None', 'From display', 'Every 2nd'],
            'tip':'Images of the same setup taken at the same exposure time'})     

        self.pRefFromDisplay  = self.pRef.addChild({
            'name':'From display',
            'type':'menu',
            'value':'[Choose]',
            'visible':False})
        self.pRefFromDisplay.aboutToShow.connect(self._buildRefFromDisplayMenu)

        self.pRef.sigValueChanged.connect(lambda param, val: 
                        self.pRefFromDisplay.show(val=='From display'))

        self.pPlotResult = pa.addChild({
            'name': 'Plot NLF',
            'type': 'bool',
            'value':True})      

        self.pRange = pa.addChild({
            'name':'Set intensity range',
            'type':'bool',
            'value':False})

        self.pMin = self.pRange.addChild({
            'name':'Minimum',
            'type':'int',
            'visible':False,
            'value':0})
        
        self.pMax = self.pRange.addChild({
            'name':'Maximum',
            'type':'int',
            'visible':False,
            'value':65000})
        self.pRange.sigValueChanged.connect(lambda param, val: 
                        [ch.show(val) for ch in self.pRange.childs])

        self.pUpdate = pa.addChild({
                    'name':'Update calibration',
                    'type':'action',
                    'visible':False})
        self.pUpdate.sigActivated.connect(self.updateCalibration)


    def updateCalibration(self):
        self.calFileTool.updateNoise(self.fitParams)


    def _buildRefFromDisplayMenu(self, menu):
        '''
        add an action for all layers of other ImageDisplays
        '''
        menu.clear()
        for d in self.display.workspace.displays():
            if ( d.widget.__class__ == self.display.widget.__class__ 
                    and d != self.display ):
                a = menu.addAction(d.name())
                a.triggered.connect(
                    lambda checked, d=d: 
                        [menu.setTitle(d.name()[:20]),
                        self.__setattr__('_refDisplay', d)] )


    def activate(self):
        self.startThread(self._process, self._done)
        
        
    def _process(self):
        imgs1 = self.display.widget.image
        if imgs1 is None:
            #image not loaded
            imgs1 = self.display.openFilesFunctions()
        v = self.pRef.value()
        if v == 'Every 2nd':
            imgs1,imgs2 = imgs1[::2],imgs1[1::2] 
        elif v == 'None' or self._refDisplay is None:
            imgs2 = None
        else:#from display
            imgs2 = self._refDisplay.widget.image
            if imgs2 is None:
                #image not loaded
                imgs2 = self._refDisplay.openFilesFunctions()       
        
        mn_mx = None
        if self.pRange.value():
            mn_mx = (self.pMin.value(), self.pMax.value())
        
        x, fn, y_avg, y_vals, w_vals, self.fitParams,i = NLF.estimateFromImages(
                                            imgs1, imgs2, mn_mx=mn_mx)
        print 'fitparams: %s' %self.fitParams
        return x, fn, y_avg, y_vals, w_vals,i


    def _done(self, (x, fn, y_avg, y_vals, w_vals,i)):
        if self.pPlotResult.value():
            if self.outDisplay is None or self.outDisplay.isClosed():
                self.outDisplay = self.display.workspace.addDisplay( 
                                axes=('intensity', 'st.dev'), 
                                title='Noise level functions')
            else:
                self.outDisplay.removeLayers()

            if self.outDisplay2 is None or self.outDisplay2.isClosed():
                self.outDisplay2 = self.display.workspace.addDisplay( 
                                axes=('intensity', 'st.dev'), 
                                title='NLF pointdensity')
            else:
                self.outDisplay2.removeLayers()

            for n, yi in enumerate(y_vals):
                self.outDisplay.addLayer(label='plot %s' %n, 
                                         data=[x,yi])
            pen = pg.mkPen('r')
            pen.setWidth(3)
            self.outDisplay.addLayer(label='average',
                                    data = [x,y_avg],
                                    pen=pen)

            pen = pg.mkPen('g')
            pen.setWidth(5)
            self.outDisplay.addLayer(label='fit',
                                    data = [x,fn(x)],
                                    pen=pen)            

            self.outDisplay2.addLayer(label='density',
                                    data = [x,w_vals],
                                    pen=pen)   
            
            self.pUpdate.show()