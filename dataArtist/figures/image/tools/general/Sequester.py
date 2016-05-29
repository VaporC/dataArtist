from dataArtist.widgets.Tool import Tool


class Sequester(Tool):
    '''
    make image array independent from its origin
    Otherwise changed in the original data also affect all of
    its copies
    '''
    icon = 'sequester.svg'
    
    
    def activate(self):
        w = self.display.widget
        w.setImage(w.image.copy())