from dataArtist.widgets.Tool import Tool


class OwnFancyTool(Tool):
    '''
    This a dummy tool button - why not clicking on it?
    '''
    icon = 'modding/media/mod.svg'
    
    
    def __init__(self, imageDisplay):
        Tool.__init__(self, imageDisplay)


    def activate(self):
        print 'activate'


    def deactivate(self):
        print 'deactivate'