import numpy as np
 
#OWN
from dataArtist.widgets.Tool import Tool


class Table(Tool):
    '''
    export the values of all plots to a table
    '''
    icon = 'table.svg'
    
    def __init__(self, plotDisplay):
        Tool.__init__(self, plotDisplay)


    def activate(self):
        lnames = self.display.layerNames()
        data = self.display.widget.getData()
        table = self.display.workspace.addTableDock().widgets[-1]
        col = 0
        #FOR ALL GRAPHS:
        for d, f in zip(data, lnames):
            header = [ [f, ''], ['x','y'] ]
            #HEADER
            table.importTable(header, startRow=0, startCol=col)
            #VALUES
            table.importTable(np.array([d.x, d.y]).transpose(), startRow=2, startCol=col)
            col += 2