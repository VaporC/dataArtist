from imgProcessor.transformations import transpose, rot90

#OWN
from dataArtist.widgets.Tool import Tool


class Transform(Tool):
    '''
    General image transforms
    DEFAULT: rotate the image 90 degrees clockwise
    '''
    icon = 'rotate.svg'
    
    def __init__(self, display):
        Tool.__init__(self, display)

        pa = self.setParameterMenu() 

        pTranspose = pa.addChild({
            'name':'Transpose',
            'type':'action'})
        pTranspose.sigActivated.connect(self._transpose)

        pMirrorX = pa.addChild({
            'name':'Flip Horizontally',
            'type':'action'})
        pMirrorX.sigActivated.connect(self._mirrorX)
        
        pMirrorY = pa.addChild({
            'name':'Flip Vertically',
            'type':'action'})
        pMirrorY.sigActivated.connect(self._mirrorY)

        #TODO: add scale

    def _transpose(self):
        w = self.display.widget
        i = w.image      
        w.setImage(transpose(i))
 
 
    def _mirrorX(self):
        w = self.display.widget
        i = w.image      
        w.setImage(i[:,::-1])


    def _mirrorY(self):
        w = self.display.widget
        i = w.image      
        w.setImage(i[:,:,::-1])
        

    def activate(self):  
        w = self.display.widget
        i = w.image
        w.setImage(rot90(i))

        #rotate axes:
        v = w.view
        a1 = v.axes['bottom']['item']  
        a2 = v.axes['left']['item']
        v.setAxes({'bottom':a2, 'left':a1})