import numpy as np
import pyqtgraph_karl as pg
 
#from imgProcessor.QuadDetection import QuadDetection, ObjectNotFound
from imgProcessor.features.QuadDetection import QuadDetection

from imgProcessor.camera.PerspectiveCorrection \
     import PerspectiveCorrection as PC

from fancytools.spatial.closestNonZeroIndex import closestNonZeroIndex

#OWN
from dataArtist.widgets.Tool import Tool
from dataArtist.figures.image.tools.globals.CalibrationFile import CalibrationFile



class PerspectiveCorrection(Tool):
    '''
    Correct the rotation and position of a quad distorted through perspective.
    The edge points of the quad can be chosen manually or automated
    '''
    
    icon = 'quadDetection.svg'

    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)
                
        self.quadROI = None
        self.outDisplay = None
        self.outDisplayViewFactor = None
        
        self._cLayerLines = None

        pa = self.setParameterMenu() 

        self.calFileTool = self.showGlobalTool(CalibrationFile)

        self.pExecOn = pa.addChild({
            'name':'Execute on',
            'type':'list',
            'value':'all images',
            'limits':['current image', 'all images', 'last image']})

        self.pRef = pa.addChild({
            'name':'Reference',
            'type':'list',
            'value':'Object profile',
            'limits':['Object profile','Reference image']})
        #HOMOGRAPHY THROUGH QUAD 
        self.pManual = self.pRef.addChild({
            'name':'Manual object detection',
            'type':'bool',
            'value':False})
#         self.pSnap = self.pManual.addChild({
#             'name':'Snap at edges',
#             'type':'bool',
#             'value':False,
#             'visible':False})
        #HOMOGRAPHY THROUGH REF IMAGE
        self.pRefImgChoose = self.pRef.addChild({
                    'name':'Reference image',
                    'value':'From display',
                    'type':'menu',
                    'visible':False})
        self.pRefImg = self.pRefImgChoose.addChild({
                    'name':'Chosen',
                    'value':'-',
                    'type':'str',
                    'readonly':True})
        self.pRefImgChoose.aboutToShow.connect(lambda menu: 
            self.buildOtherDisplayLayersMenu(menu, self._setRefImg) )

        self.pRef.sigValueChanged.connect(self._pRefChanged)
#         self.pSnap.sigValueChanged.connect(self._pSnapChanged)
        self.pManual.sigValueChanged.connect(self._setupQuadManually)

        pShowPlane = self.pManual.addChild({
            'name':'Show Plane',
            'type':'bool',
            'value':True})
        pShowPlane.sigValueChanged.connect(self._showROI)


        self.pCalcOutSize = pa.addChild({
            'name':'Calculate output size',
            'type':'bool',
            'value':True,
            'tip':''})
        self.pOutWidth = self.pCalcOutSize.addChild({
            'name':'Image width [px]',
            'type':'int',
            'value':1000,
            'visible':False})
 
        self.pOutHeight = self.pCalcOutSize.addChild({
            'name':'Image height [px]',
            'type':'int',
            'value':600,
            'visible':False
            })
        self.pCalcOutSize.sigValueChanged.connect(
                lambda p,v:[self.pCalcAR.show(v), 
                            self.pOutWidth.show(not v),
                            self.pOutHeight.show(not v) ])

        self.pCalcAR = pa.addChild({
            'name':'Calculate aspect ratio',
            'type':'bool',
            'value':True,
            'tip':''})
        
        self.pObjWidth = self.pCalcAR.addChild({
            'name':'Object width [mm]',
            'type':'float',
            'value':0,
            'visible':False})
 
        self.pObjHeight = self.pCalcAR.addChild({
            'name':'Object height [mm]',
            'type':'float',
            'value':0,
            'visible':False
            })
        self.pCalcAR.sigValueChanged.connect(lambda param, val: 
                        [ch.show(not val) for ch in param.childs]) 
        
        self.pCorrViewFactor = pa.addChild({
            'name':'Correct Intensity',
            'type':'bool',
            'value':False,
            'tip':'For realistic results choose a camera calibration'})
        self.pDrawViewFactor = self.pCorrViewFactor.addChild({
            'name':'Show tilt factor',
            'type':'bool',
            'value':False})
        self.pCorrViewFactor.sigValueChanged.connect(lambda param, val: 
                                            self.pDrawViewFactor.show(val)) 

        self.pLive = pa.addChild({
            'name': 'Live',
            'tip':'Update result whenever one of the parameter was changed',
            'type': 'bool',
            'value':False}) 

        self.pOverrideOutput = pa.addChild({
            'name':'Override output',
            'type':'bool',
            'value':True})

 
    def _setRefImg(self, display, layernumber, layername):
        '''
        extract the reference image and -name from a given display and layer number
        '''
        im  = display.widget.image
        self._refImg_from_own_display = -1
        self._refImg = im[layernumber]
        if display == self.display:
            self._refImg_from_own_display = layernumber
        self.pRefImg.setValue(layername)


    
    def _showROI(self, param, value):
        if self.quadROI is not None: 
            self.quadROI.show() if value else self.quadROI.hide()
    
    
    def _setupQuadManually(self, param, value):
#         self.pSnap.show(value)
        if value:
            if not self.quadROI:
                self._createROI()
            else:
                self.quadROI.show()
        elif self.quadROI:
            self.quadROI.hide()


    def _pRefChanged(self, param, val):
        v = val == 'Reference image'
        self.pManual.show(not v)
        self.pRefImgChoose.show(v)
   
#    
#     def _pSnapChanged(self, param, val):
#         w = self.display.widget
# 
#         if val:
#             img = w.image
#             img = img[w.currentIndex]
#     
#             q = QuadDetection(img)
#             s = img.shape[0]
#             threshold=40
#             minLineLength=int(s/10)
#             maxLineGap = int(s/10)
#             
#             q.findLines( threshold=threshold, 
#                          minLineLength=minLineLength, 
#                          maxLineGap=maxLineGap )
#             i = np.zeros_like(img, dtype=np.uint8)
#             q.drawLines(i, thickness=1, color=255)
#             if self._cLayerLines is None:
#                 self._cLayerLines = w.addColorLayer(layer=i, name='Detected edges', 
#                                                     tip='houghLines')
#             else:
#                 self._cLayerLines.setLayer(i)
#         elif self._cLayerLines is not None:
#             w.removeColorLayer(self._cLayerLines)
#             self._cLayerLines = None 


    def _roiMoved(self):
        if self._cLayerLines is not None:
            i = self._cLayerLines.image
            for h in  self.quadROI.handles:
                #snap to closest line
                pos = h['item'].pos()
                pt = ( pos.x(), pos.y() )
                closest = closestNonZeroIndex(pt, i, kSize=101)
                if closest is not None:
                    h['item'].setPos(closest[0], closest[1])
            self.quadROI.update()

   
    def _createROI(self):
        w = self.display.widget
        s = w.image[w.currentIndex].shape[:2]
        if not self.quadROI:
            self.quadROI = pg.PolyLineROI([[s[0]*0.2,s[1]*0.2], 
                                           [s[0]*0.8, s[1]*0.2], 
                                           [s[0]*0.8, s[1]*0.8],
                                           [s[0]*0.2, s[1]*0.8]], 
                                          closed=True, pen='r')
            self.quadROI.translatable = False
            self.quadROI.mouseHovering = False
            self.quadROI.sigRegionChangeFinished.connect(self._roiMoved)
            #TODO: just disconnect all signals instead of having lambda
            #PREVENT CREATION OF SUB SEGMENTS:
            for s in self.quadROI.segments:
                s.mouseClickEvent = lambda x:None

            w.view.vb.addItem(self.quadROI)     
   
     
    def activate(self):        
        if self.pLive.value():
            self._prepare()
            self.display.widget.item.sigImageChanged.connect(
                                                self._processAndDone)
        else:
            self.startThread(self._prepareAndProcess, self._done)


    def _prepare(self):
        w = self.display.widget
        img = w.image[w.currentIndex]

        #HOMOGRAPHY THROUGH REFERENCE IMAGE
        if self.pRef.value() == 'Reference image':
            ref = self._refImg
        else:
            #HOMOGRAPHY THROUGH QUAD
            if self.pManual.value():
                #need to transpose because of different conventions
                vertices = np.array([(h['pos'].y(),h['pos'].x())  
                                    for h in self.quadROI.handles])
                vertices += self.quadROI.pos()
            else:
                vertices = QuadDetection(img).vertices

                if not self.quadROI: 
                    self._createROI()
                #show found ROI:
                for h,c in zip(self.quadROI.handles, vertices):
                    pos = c[::-1] - self.quadROI.pos()
                    h['item'].setPos(pos[0], pos[1])
            ref = vertices
            self.quadROI.show()
            
        c = self.calFileTool.currentCameraMatrix()
        
        #height/width:
        if self.pCalcAR.value():
            w,h = None,None
        else:
            w = self.pObjWidth.value()
            if w == 0:
                w = None
            h = self.pObjHeight.value()
            if h == 0:
                h = None
        #output size:
        size = None
        if not self.pCalcOutSize.value():
            size = (self.pOutHeight.value(),self.pOutWidth.value())
        
        #INIT:
        self.pc = PC(img.shape, 
                     obj_width_mm=w, 
                     obj_height_mm=h, 
                     cameraMatrix=c, 
                     do_correctIntensity=self.pCorrViewFactor.value(),
                     new_size=size
                     )
        self.pc.setReference(ref)

 
    def _process(self):
        w = self.display.widget
        img = w.image
        out = []
        r = self.pRef.value() == 'Reference image'
        e = self.pExecOn.value()
        
        for n,i in enumerate(img):
            if (e == 'all images' 
                or (e=='current image' and n == w.currentIndex)
                or (e=='last image' and n == len(img)-1) ):
                
                if not (r and n == self._refImg_from_own_display):
                    out.append(self.pc.correct(i))           
        return out
     
     
    def _done(self, out):
        change = 'PerspectiveFit'
        if not self.outDisplay or self.outDisplay.isClosed():
            self.outDisplay = self.display.workspace.addDisplay(
                    origin=self.display,
                    changes=change,
                    data=out, 
                    title=change) 
        else: 
            self.outDisplay.widget.update(out)
            self.outDisplay.widget.updateView()


        if self.pCorrViewFactor.value() and self.pDrawViewFactor.value():
            if not self.outDisplayViewFactor:
                self.outDisplayViewFactor = self.display.workspace.addDisplay(
                        origin=self.display,
                        changes=change,
                        data=[self.pc.maps['tilt_factor']], 
                        title='Tilt factor') 
            else: 
                self.outDisplayViewFactor.widget.setImage(self.pc.maps['tilt_factor'])
#         
#         if self.pSceneReconstruction.value():
#             #print p.scene()[0,0], p.scene()[-1,-1]
#             if not self.outDisplayScene:
#                 self.outDisplayScene = self.workspace.addDisplay(
#                         axes = 4,                                   
#                         origin=self.display,
#                         changes=change,
#                         data=[p.scene()], 
#                         title='Scene reconstruction') 
#             else: 
#                 self.outDisplayScene.widget.update(index=0, data=p.scene())
#                 
#             self.outDisplayScene.widget.updateView(xRange=p.sceneRange()[1], 
#                                                       #yRange=p.sceneRange()[0]
#                                                       )


        if not self.pOverrideOutput.value():
            self.outDisplay = None
            self.outDisplayViewFactor = None
        if not self.pLive.value():
            self.setChecked(False)
            del self.pc
#         if self.pDraw3dAxis.value():
#             out = p.draw3dCoordAxis()
#             w.item.blockSignals(True)
#             w.setImage(out)
#             w.item.blockSignals(False)
#             if self.axisLayer == None:
#                 self.axisLayer = w.addColorLayer(out, name='3daxis')#, indices=found_indices) 
#             else:
#                 self.axisLayer.setImage(out)

#             if not self.outDisplayAxes:
#                 self.outDisplayAxes = self.workspace.addDisplay(
#                         origin=self.display,
#                         changes=change,
#                         data=[out], 
#                         title='Axes') 
#             else: 
#                 self.outDisplayAxes.widget.setImage(out)


    def _prepareAndProcess(self):
        self._prepare()
        return self._process()


    def _processAndDone(self):
        out = self._process()
        self._done(out)
   

    def deactivate(self):
        try:
            w = self.display.widget
            w.item.sigImageChanged.disconnect(self._processAndDone)  
        except:
            pass