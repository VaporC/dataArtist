from dataArtist.widgets.Tool import Tool


class Reload(Tool):
    '''
    Load or reload the displays data
    '''
    icon = 'reload.svg'
    
    
    def activate(self):
        if not self.display.reader:
            raise Exception('no input data to reload')
        self.display.updateInput()
