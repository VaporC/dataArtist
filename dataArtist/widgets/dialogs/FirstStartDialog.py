from appbase.dialogs.FirstStart import FirstStart
from dataArtist.widgets.preferences import ChooseProfile

from pyqtgraph_karl.Qt import QtGui



class FirstStartDialog(FirstStart):
    '''
    Extent first start dialog with profile selection
    '''
    def __init__(self, session):
        FirstStart.__init__(self, session)
        
        self.layout().insertWidget(3, ChooseProfile(session)) 

        #TEMPORARY CONTENT TO BE REMOVED AFTER CODE RELEASE
        self.resize(300,310)
        lab = QtGui.QLabel('<b>Software License Agreement</b>')
        
        ed = QtGui.QTextBrowser()
        ed.setReadOnly(True)  
        ed.setOpenExternalLinks(True)
        ed.setCurrentFont(QtGui.QFont("Courier New", 8))
        ed.setHtml('''<font size="3" face="Courier New">
This free software 'dataArtist' is licensed under GPLv3.
By using this software the user agrees to the thereby associated terms.
More information can be found <a href = "http://www.gnu.org/licenses/quick-guide-gplv3.en.html">here
</a> </font>''')

 
        btn = QtGui.QCheckBox('I accept the terms')
        self.btn_done.setEnabled(False)
        
        btn.clicked.connect(lambda checked: self.btn_done.setEnabled(checked))

        self.layout().insertWidget(4, lab) 
        self.layout().insertWidget(5, ed) 
        self.layout().insertWidget(6, btn)