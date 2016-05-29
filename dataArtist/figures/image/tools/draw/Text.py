from pyqtgraph_karl import TextItem as pgTextItem
from pyqtgraph_karl.Qt import QtCore, QtGui
from pyqtgraph_karl import functions as fn

#OWN
from dataArtist.widgets.Tool import Tool



class Text(Tool):
    '''
    Draw, move and edit a text box
    '''
    icon = 'text.svg'

    def __init__(self, display):
        Tool.__init__(self, display)
        
        self.textItems = []

        pa = self.setParameterMenu() 

        self.pScales = pa.addChild({
            'name': 'Text scales',
            'type': 'bool',
            'value':True}) 

        pAdd = self._menu.p.addChild({
            'name': 'Add',
            'type': 'action'}) 
        pAdd.sigActivated.connect(lambda:
              self.view.scene().sigMouseClicked.connect(self._textAdd) )   
        pAdd.sigActivated.connect(self._menu.hide)  

        pClear = pa.addChild({
            'name': 'Clear',
            'type': 'action'}) 
        pClear.sigActivated.connect(self._clear)   

        pColor = pa.addChild({
            'name': 'Color',
            'type': 'empty',
            'isgroup':True})         

        self.pCFont = pColor.addChild({
            'name': 'Font',
            'type': 'color',
            'value':(0,0,0)}) 
        self.pCFont.sigValueChanged.connect(self._fontColorChanged)

        self.pCBg = pColor.addChild({
            'name': 'Background',
            'type': 'color',
            'value':'w'}) 
        self.pCBg.sigValueChanged.connect(self._fontBgChanged)

        self.pFont = pa.addChild({
            'name': 'Font',
            'type': 'action',
            'font':None}) 

        self.pFont.sigActivated.connect(self._setFont)


    def _fontColorChanged(self, p,v):
        if self.textItems:
            i = self.textItems[-1] 
            i.textItem.setDefaultTextColor(v)
            i.updateText()

  
    def _fontBgChanged(self, p,v):
        if self.textItems:
            i = self.textItems[-1] 
            i.fill = fn.mkBrush(v)
            i.updateText()
            
 
    def _setFont(self):
        f = QtGui.QFontDialog.getFont
        if self.textItems:
            d = f(self.textItems[-1].textItem.font())
        else:
            d = f()
        if d[1]:
            self.pFont.opts['font'] = d[0]

        if self.textItems:
            self.textItems[-1].setFont(d[0]) 

       
    def _clear(self):
        for a in self.textItems:
            self.view.removeItem(a)  
        self.textItems = []


    def activate(self):
        for a in self.textItems:
            a.show()


    def deactivate(self):
        for a in self.textItems:
            a.hide()


    def _textAdd(self, evt):
        self.setChecked(True)

        self.view.scene().sigMouseClicked.disconnect(self._textAdd)

        t = _TextItem(self, self.pScales.value(),
                      text='CHANGE ME', 
                      color=self.pCFont.value(),  
                      anchor=(0.5,0.5),
                      fill=self.pCBg.value())
        if self.pFont.opts['font']:
            t.setFont(self.pFont.opts['font'])
        self.view.addItem(t)
        t.setPos(*self.mouseCoord(evt))
        self.textItems.append(t)

  
    def _showHide(self, show):
        for t in self.textItems:
            t.show() if show else t.hide()



class _TextItem(pgTextItem):
    '''
    Text box
    --> movable through drag/drop
    --> editable through double click.
    '''
    def __init__(self, parent, scales, **kwargs):
        pgTextItem.__init__(self, **kwargs)
        self._parent = parent

        self.editor = QtGui.QLineEdit(parent)
        self.editor.setWindowFlags(QtCore.Qt.Popup)
        self.editor.setFocusProxy(parent)
        self.editor.editingFinished.connect(self.editingFinished)
        self.editor.installEventFilter(parent)
        self.editor.setText(self.textItem.toPlainText())
        self.setFlag(self.ItemIgnoresTransformations, scales)


    def editingFinished(self):
        self.setText(self.editor.text())
        self.editor.hide()


    def hoverEvent(self, ev):
        ev.acceptDrags(QtCore.Qt.LeftButton)
        
        
    def mouseDragEvent(self, ev):
        #ev.pos()) gives oscillating positions
        self.setPos(*self._parent.mouseCoord(ev))


    def mouseDoubleClickEvent(self, ev):
        self.editor.show()