from dataArtist.widgets.Tool import Tool


class LockAspectRatio(Tool):
    '''
    Lock the aspect ratio of the current view
    '''
    icon = 'aspectRatio.svg'
    
    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)
        
        self.setChecked(self.display.widget.view.vb.state['aspectLocked'])

        pa = self.setParameterMenu() 

        pRange = pa.addChild({
            'name': 'autoRange',
            'type': 'bool',
            'value':True,
            'tip':'''whether to fit view every time the input changes'''})
        pRange.sigValueChanged.connect(lambda param, value: 
                                self.display.widget.setOpts(autoRange=value))


    def activate(self):
        self.display.widget.view.vb.setAspectLocked(True)
        

    def deactivate(self):
        self.display.widget.view.vb.setAspectLocked(False)