import numpy as np
from pyqtgraph_karl.Qt import QtGui, QtCore

from imgProcessor.camera.LensDistortion import LensDistortion as LD
from imgProcessor.camera.LensDistortion import EnoughImages, NothingFound

from fancytools.os.PathStr import PathStr

import os

#OWN
from dataArtist.widgets.Tool import Tool
from dataArtist.figures.image.tools.globals.CalibrationFile import CalibrationFile
from dataArtist.items.UnregGridROI import UnregGridROI

import dataArtist
PATTERN_FILE = PathStr(dataArtist.__file__).dirname().join('media', 'camera_calibration_patterns.pdf')
del dataArtist



class LensDistortion(Tool):
    '''
    Calibrate the camera through interpreting chessboard images
    [also works with un-loaded image stack]
    '''
    icon = 'chessboard.svg'

    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)

        self.calFileTool = self.showGlobalTool(CalibrationFile)

        self.camera = None
        self.cItem = None
        self.key = None
        
        self._rois = []
        self._roi = None
                
        pa = self.setParameterMenu() 
        
        btn = QtGui.QPushButton('Show Patterns')
        btn.clicked.connect(lambda: os.startfile(PATTERN_FILE) )
        btn.setFlat(True)
        self._menu.content.header.insertWidget(2, btn)

        self.pLive = pa.addChild({
            'name':'Live',
            'type':'bool',
            'value':False,
            'tip':"""'False': Images are taken from stack
True: Images are taken every time the first layer is updated 
      choose this if you use a webcam"""})
        
        self.pLiveStopAfter = self.pLive.addChild({
            'name':'Stop after n images',
            'type':'int',
            'value':20,
            'limits':[0,10000]})
        
        self.pLiveActivateTrigger = self.pLive.addChild({
            'name':"Manual trigger",
            'type':'bool',
            'value':True})
        
        self.pLiveTrigger = self.pLiveActivateTrigger.addChild({
            'name':"Trigger or KEY [+]",
            'type':'action',
            'visible':False})

        self.pLive.sigValueChanged.connect(
            #show/hide children
            lambda param, value: [ch.show(value) for ch in param.children()])
        self.pLive.sigValueChanged.emit(self.pLive, self.pLive.value())
        
        self.pMethod = pa.addChild({
            'name':'Method',
            'type':'list',
            'limits':['Chessboard', 'Symmetric circles', 'Asymmetric circles',
                      'Manual']})
        self.pMethod.sigValueChanged.connect(self._pMethodChanged)

        self.pFit = self.pMethod.addChild({
            'name':'Fit to corners',
            'type':'action',
            'visible':False,
            'tip': '''Fit grid to given corner positions'''}) 
        self.pFit.sigActivated.connect(self._pChebXYChanged)
        
        self.pChessbX = self.pMethod.addChild({
            'name':'N corners X',
            'type':'int',
            'value':6,
            'tip': '''Depending on used pattern, number of corners/circles in X''',
            'limits':[3,100]}) 
        self.pChessbX.sigValueChanged.connect(self._pChebXYChanged)
        
        self.pChessbY = self.pMethod.addChild({
            'name':'N corners Y',
            'type':'int',
            'value':8,
            'tip': '''Depending on used pattern, number of corners/circles in Y''',
            'limits':[3,100]})
        self.pChessbY.sigValueChanged.connect(self._pChebXYChanged)
        
        
        pApSize = pa.addChild({
            'name':'Aperture Size [mm]',
            'type':'group',
            'tip':'Physical size of the sensor'})
        
        self.pApertureX = pApSize.addChild({
            'name':'Size X',
            'type':'float',
            'value':4,
            'tip':'Physical width of the sensor'}) 
        
        self.pApertureY = pApSize.addChild({
            'name':'Size Y',
            'type':'float',
            'value':3,
            'tip':'Physical height of the sensor'})
        
        self.pDrawChessboard = pa.addChild({
            'name': 'Draw Chessboard',
            'type': 'bool',
            'value': False}) 

        self.pDisplacement  = pa.addChild({
            'name':'Return spatial uncertainty',
            'type':'bool',
            'value':False})

        self.pUpdate = pa.addChild({
                    'name':'Update calibration',
                    'type':'action',
                    'visible':False})
        self.pUpdate.sigActivated.connect(self.updateCalibration)

        self.pCorrect = pa.addChild({
                    'name':'Undistort',
                    'type':'action',
                    'visible':False})
        self.pCorrect.sigActivated.connect(self.correct)


    def correct(self):
        out = []
        for i in self.getImageOrFilenmes():
            out.append( self.camera.correct(i, keepSize=True) )
        
        self.display.workspace.addDisplay(
            origin=self.display,
            data=out, 
            title='Corrected')


    def _posSize(self):
        #TODO: as general method in WidgetBase?
        vb = self.display.widget.view.vb
        r = vb.viewRange()  
        s = ((r[0][0]+r[0][1])/1.1, (r[1][0]+r[1][1])/1.1)
        p = [(r[0][1]-r[0][0])*0.1, (r[1][1]-r[1][0])*0.1]
        return p,s


    def _nCells(self):
        return (self.pChessbX.value()-1, self.pChessbY.value()-1)


    def _removeROIs(self):
        w = self.display.widget
        vb = w.view.vb
        if self._rois:
            vb.removeItem(self._roi)
            w.sigTimeChanged.disconnect(self._changeROI)
        self._rois = []


    def _createROIs(self, edgesList=None):
        w = self.display.widget
        vb = w.view.vb
        p,s = self._posSize() 
        n =    self._nCells()
        e = None
        if self._roi:
            e = self._roi.edges()
        for i in range(len(w.image)):
            r = UnregGridROI(n, pos=p, size=s, edges=e, pen='r')
            self._rois.append(r)
            if i == w.currentIndex:
                self._roi = r
                vb.addItem(r)
        w.sigTimeChanged.connect(self._changeROI)


    def _changeROI(self, ind, time):
        w = self.display.widget
        vb = w.view.vb
        vb.removeItem(self._roi)
        self._roi = r = self._rois[ind]
        vb.addItem(r)
        
    
    def _pMethodChanged(self, param, val):
        self._removeROIs()
        if val == 'Manual':
            self._createROIs()
            self.pFit.show()  
        else:
            self.pFit.hide()


    def _pChebXYChanged(self):
        #Show GridROI in case manual detectoin is chosen
        if self.pMethod.value() == 'Manual':
            if self._rois:
                self._removeROIs()
            self._createROIs()



    def updateCalibration(self):
        self.calFileTool.updateLens(self.camera)


    def _chooseSavePath(self):
        d = self.display.workspace.gui.dialogs.getSaveFileName(
                                    filter='*.%s' %LensDistortion.ftype)
        if d:
            self.pSavePath.setValue(d)
        

    def activate(self):  
        w = self.display.widget
        self.camera = LD()
        self.camera.calibrate(
                   method=self.pMethod.value(),
                   board_size=(self.pChessbX.value(), 
                               self.pChessbY.value()), 
                   max_images=self.pLiveStopAfter.value(),
                   sensorSize_mm=(self.pApertureX.value(), 
                                  self.pApertureY.value()),
                   detect_sensible=True )

        if self.pLive.value():  
            if self.pDrawChessboard.value() and not self.cItem:
                self.cItem = w.addColorLayer(name='Chessboard')
            if self.pLiveActivateTrigger.value():
                self.pLiveTrigger.setOpts(visible=True)
                self.pLiveTrigger.sigActivated.connect(self._addImgStream)
                if not self.key:
                    #ACTIVATE ON KEY [+]
                    self.key = QtGui.QShortcut(self.display.workspace)
                    self.key.setKey(QtGui.QKeySequence(QtCore.Qt.Key_Plus))
                    self.key.setContext(QtCore.Qt.ApplicationShortcut)
                self.key.activated.connect(self.pLiveTrigger.activate)     
            else:
                #ACTIVATE WHEN IMAGE CHANGES
                w.item.sigImageChanged.connect(self._addImgStream)
        else:
            #READ IMAGE STACK
                #check conditions:
            if len(self.display.filenames) < 10:
                print 'having less than 10 images can result in erroneous results'

            img = w.image
            img_loaded = True
            if img is None: #calibration images not loaded
                img_loaded = False
                img = self.display.filenames
            
            out = []
            d = self.pDrawChessboard.value()
            found_indices = []
            for n, i in enumerate(img):
                try:
                    #MANUAL ADDING POINTS
                    if self._rois:
                        print self._rois[n].points()
                        self.camera.addPoints(self._rois[n].points())
                        self.camera.setImgShape(i.shape)
                    else:
                        self.camera.addImg(i)
                    #draw chessboard
                    if d:
                        out.append(self.camera.drawChessboard(
                                False if img_loaded else None))
                        found_indices.append(n)
                except NothingFound, errm:
                    print 'Layer %s: ' %n, errm
            if d:
                if img_loaded:
                    w.addColorLayer(np.array(out), name='chessboard')#, indices=found_indices) 
                else:
                    self.display.addLayers(out, ['Chessboard']*len(out))
            
            self._end()


    def _end(self):     
        self.setChecked(False)    
        i = self.camera.findCount
        print 'found chessboard of %s images' %i
        if i:
            #show calibration in window:
            t = self.display.workspace.addTextDock('Camera calibration').widgets[-1]
            t.showToolbar(False)
            t.text.setText(self.camera.getCoeffStr())

            self.pUpdate.show()
            self.pCorrect.show()

            if self.pDisplacement.value():
                self.display.workspace.addDisplay(
                        origin=self.display,
                        data=self.camera.getDisplacementArray(), 
                        title='displacement')


    def _addImgStream(self):
        '''
        add a new image and draw chessboard on it till there are enough images
        '''
        if self.pLiveActivateTrigger.value():
            print 'click'
        if not self.camera:
            print 'activate first'
        try:
            image = self.display.widget.image
            found = self.camera.addImgStream(image)
            if found and self.pDrawChessboard.value():
                chessboard = self.camera.drawChessboard(img=False)
                self.cItem.setLayer(chessboard)
            if found:
                print 'found %s chessboards' %self.camera.findCount  
        except EnoughImages:
            self.deactivate()
            self._end()


    def deactivate(self):
        try:
            self.display.widget.item.sigImageChanged.disconnect(self._addImgStream)
        except:
            pass
        try:
            self.pLiveTrigger.sigActivated.disconnect(self._addImgStream)
        except:
            pass
        try:
            self.key.activated.disconnect(self.pLiveTrigger.activate)
        except:
            pass   