from dataArtist.widgets.Tool import Tool


#TODO: is this extra image tool actually needed? 
class ImageTool(Tool):
    
    def getImageOrFilenames(self):
        img = self.display.widget.image
        if img is None:
            img = self.display.filenames
        return img
