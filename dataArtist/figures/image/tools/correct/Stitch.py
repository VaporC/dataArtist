import numpy as np

from imgProcessor.transform.StitchImages import StitchImages

from dataArtist.widgets.ImageTool import ImageTool



class Stitch(ImageTool):
    '''
    Stitch two images at a given edge together.
    Find the right overlap through template matching
    
    ...works on unloaded images too
    
    IMPORTANT: not correction for perspective errors at the moment
    '''
    icon = 'imgStitching.svg'
    
    def __init__(self, imageDisplay):
        ImageTool.__init__(self, imageDisplay)
        
        self._refImg = None
        
        pa = self.setParameterMenu() 
        self.createResultInDisplayParam(pa)

        self.pSide = pa.addChild({
            'name':'Side',
            'type':'list',
            'value':'bottom',
            'limits':['bottom', 'top', 'left', 'right']})

        pImgChoose = pa.addChild({
                    'name':'add to image',
                    'value':'from display',
                    'type':'menu'})
        
        self.pImg = pImgChoose.addChild({
                    'name':'chosen',
                    'value':'-',
                    'type':'str',
                    'readonly':True})
        pImgChoose.aboutToShow.connect(self.buildImgMenu)

        self.pBgColor = pa.addChild({
            'name':'Background colour',
            'type':'list',
            'value':'0',
            'limits':['-','0','np.nan']})

        self.pOverlap = pa.addChild({
                    'name':'Overlap',
                    'type':'int',
                    'value':250,
                    'limits':[0,2000]})
        
        self.pOverlapDev = self.pOverlap.addChild({
                    'name':'Deviation',
                    'type':'int',
                    'value':50,
                    'limits':[0,2000]})

        self.pRot = pa.addChild({
                    'name':'Rotation [DEG]',
                    'type':'float',
                    'value':0,
                    'limits':[-45,45]})
        self.pRotDev = self.pRot.addChild({
                    'name':'Deviation',
                    'type':'float',
                    'value':0,
                    'limits':[0,20]})
        
        self.pSet = pa.addChild({
                    'name':'Set parameters to result',
                    'type':'bool',
                    'value':False,
                    'tip': 'Activate, to set overlap and rotation to found result'})


    def buildImgMenu(self, menu):
        '''
        fill the menu with all available images within other displays
        '''
        menu.clear()
        for d in self.display.workspace.displays():
            if d.widget.__class__ == self.display.widget.__class__:
                m = menu.addMenu(d.name())
                for n,l in enumerate(d.layerNames()):
                    m.addAction(l).triggered.connect(
                        lambda checked, d=d, n=n,l=l: 
                            self.setRefImg(d, n, l) )
                    if d == self.display:
                        #allow only to choose first layer from same display
                        break


    def setRefImg(self, display, layernumber, layername):
        '''
        extract the reference image and -name from a given display and layer number
        '''   
        self._refDisplay = display            
        self._refLayer = layernumber if layernumber else None
        im  = display.widget.image
        if im is None:
            #TODO: reader callable instead of filenames
            self._refImg = display.filenames[layernumber]
        else:
            self._refImg = im[layernumber]   
            
        self.pImg.setValue(layername)


    def activate(self):
        if self._refImg is None:
            raise Exception('Need to define reference image first')
        
        st = StitchImages(self._refImg)
        
        im = self.getImageOrFilenames()
        if self._refDisplay.number == self.display.number:
            im = im[1:]
 
        bgcol = {'0'     : 0,
                 'np.nan': np.nan, 
                 '-'     : None }
        for i in im:
            if i is not None:
                out = st.addImg(i, 
                              side=self.pSide.value(), 
                              backgroundColor=bgcol[self.pBgColor.value()],
                              overlap=self.pOverlap.value(),
                              overlapDeviation=self.pOverlapDev.value(),
                              rotation=self.pRot.value(),
                              rotationDeviation=self.pRotDev.value()) 
                
                if self.pSet.value():
                    offs, rot = st.lastParams[1:]
                    self.pOverlap.setValue(offs)
                    self.pOverlapDev.setValue(0)
                    self.pRot.setValue(rot)
                    self.pRotDev.setValue(0) 
                                       
        self.handleOutput([out], title='stiched', 
                          changes='stitched', names=['stitched'])