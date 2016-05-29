'''
This is an example of how to extend dataArtist with ...
   an own display class
       with own tools
   own tools for the existing imageWidget
   own data reader
   
   Execute this module and drag and drop the file 'dataArtist/modding/testFile.abc'
   in the open window.
   
   Modifying dataArtist allows you to create your own individual 
   visualisation, analysis and processing suite. 
'''
if __name__ == '__main__':
    import dataArtist
    import os
    #change working directory
    #this is essential if dataArtist is started from another directory:
    os.chdir(dataArtist.__path__[0])
    
    #load dataArtist modules which are to be modified:
    from dataArtist.figures.plot import tools
    from dataArtist import figures
    from dataArtist.input import reader
    
    #own classes:
    from dataArtist.modding.ownDisplay.OwnDisplayWidget import OwnDisplayWidget
    from dataArtist.modding.ownDisplay.tools.ownBar.OwnFancyTool import OwnFancyTool
    from dataArtist.modding.ownReader.ABCreader import ABCreader
    
    #ADD OWN COMPONENTS TO DATAARTIST:
        #new display
    figures.OwnDisplayWidget = OwnDisplayWidget
        #add own tool to the  PlotWidgets processing toolbar:
    tools.processing.OwnFancyTool = OwnFancyTool
        #add an own reader with allows us to open an *.abc file:
    reader.ABCreader = ABCreader
    
    #start modified dataArtist:
    from dataArtist import gui
    gui.main(name='MODDED dataArtist')