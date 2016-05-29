import pyqtgraph_karl as pg

from fancywidgets.pyqtgraphBased.parametertree import Parameter
   


class AxesContainer(list):
    '''
    A list of all axes that belong to a display
    all axes-parameters are within self.p respective axis.p
    '''
    
    def __init__(self, display, axes, pStack):
        self.display = display
        self.p = Parameter.create(name='Axes', type='group') 
        pSize = self.p.addChild({
            'name':'size',
            'type':'int',
            'value':9})
        pSize.sigValueChanged.connect(
                lambda param, val: [ax.setFontSize(val) for ax in self])
                                      
        orientations =[ 'bottom','left', 'bottom', 'bottom', None]
            
        for n,a in enumerate(axes):
            self.append(a, orientations[n])
        
        #CREATE STACK AXIS - an axis representing the stack of datasets
        self.stackAxis = getattr(axes, 'stackAxis', 
                                 StackAxis('(Stack)', 'n', orientations[n+1]))
        self.stackAxis.registerStackParam(pStack)
        self.p.addChild(self.stackAxis.p)
        

    def remove(self, axis):
        axis.remove()
        list.remove(self, axis)
   
   
    def _getAxisName(self):
        return '(%s)' %list.__len__(self)
     
     
    def append(self, axis, orientation='bottom'):
        if isinstance(axis, basestring):
            #create axis if only a name is given:
            axis = Axis(self._getAxisName(), axis, orientation)
        self.p.addChild(axis.p)
        #TODO: update after scale - define which scale               
        #axe.pScale.sigValueChanged.connect(lambda param, x: self.display.widget.item.setScale(x))                
        list.append(self, axis)
        #axis.container = self


    def copy(self, index=None, orientation=None):
        '''
        make a copy of all or given axes indices
        '''
        #prepare index
        if index is None:
            #copy all axes
            index = range(len(self))
            #except of the stack axis - we will add it at the end anyway
            #index.pop(self.index(self.stackAxis))
        elif not type(index) in (tuple, list):
            index = [index] 
        #create axisList
        out = _List()
        for n,i in enumerate(index):
            if type(orientation) in (tuple, list):
                o = orientation[n]
            else:
                o = orientation
            if i == 'stack':
                axisToCopy = self.stackAxis
                newAxis = axisToCopy.duplicate(o)
                newAxis.__class__ = Axis
                newAxis.p.setName(newAxis.p.value())
            else:
                axisToCopy = self.__getitem__(i)
                newAxis = axisToCopy.duplicate(o)
            newAxis.linkToAxis(axisToCopy)
            out.append(newAxis)
        #add an extra stack axis:
        out.stackAxis = self.stackAxis.duplicate(o)
        return out

    

class Axis(pg.AxisItem):
    '''
    A display axis
    '''
    def __init__(self, name, value, orientation, state=None):
        pg.AxisItem.__init__(self, orientation)

        self.p = Parameter.create(**{
                'name':name,
                'type':'str',
                'value':value,
                'expanded':False,
                'isGroup':True})
        self.setLabel(value)
        
        self.pLinked = self.p.addChild({
                'name':'axis linked',
                'type':'bool',
                'value':True,
                'visible':False})
        self.pLinked.sigValueChanged.connect(lambda param, val, self=self:
                                self.linkToAxis() if val else self.unlinkFromAxis)
        
        self.pUnit = self.p.addChild({
                'name':'unit',
                'type':'str',
                'value':''})
        self.pPrefix = self.p.addChild({
                'name':'prefix',
                'type':'str',
                'value':''})
        self.pRange = self.p.addChild({
                'name':'range',
                'type':'list',
                'limits':['linear', 'percent']
                                 })
        self.pRange.sigValueChanged.connect(self._pRangeChanged)
        #scale
        self.pScale = self.pRange.addChild({
                'name':'scale',
                'type':'float',
                'value':1})
        #offset
        #TODO
        self.pOffset = self.pRange.addChild({
                'name':'offset',
                'type':'float',
                'value':0,
                #'tip': "Doesn't work at the moment",
                'visible':False
                })
            #TODO: need to know the orientation first
            #pOffset.sigValueChanged.connect(lambda x: dock.display.item.setPos ( qreal x, qreal y ))
        
        if state:
            self.p.restoreState(state)
        
        self.p.sigValueChanged.connect(lambda param, x, self=self: 
                                            self.setLabel(text=x))                
        self.pUnit.sigValueChanged.connect(lambda param, x, self=self: 
                                            self.setLabel(units=x))                
        self.pPrefix.sigValueChanged.connect(lambda param, x, self=self: 
                                            self.setLabel(unitPrefix=x))
        self.pScale.sigValueChanged.connect(lambda param, x, self=self: 
                                            self.setScale(x))
        #self.pOffset.sigValueChanged.connect(lambda param, x, self=self: self.setOffset(x))


    def __repr__(self):
        return "%s '%s'" %(self.__class__.__name__, self.p.name())


    def _pRangeChanged(self, param, val):
        [ch.show(val!='percent') for ch in param.childs]
        if val == 'percent':
            #scale axis between 0 - 100
            bounds = self._linkedView().childrenBoundingRect()
            if self.orientation in ['right', 'left']:
                self.pScale.setValue(100/bounds.height())
            else:
                self.pScale.setValue(100/bounds.width())
        else:
            self.pScale.setValue(1)
            

    def linkToAxis(self, axis=None):
        '''
        connect parameter changes to the given axis
        '''
        if axis is not None:
            self._linkedAxis = axis
        self.pLinked.show()
        def link(master, slave):
            for m, s in zip(master.childs,slave.childs):
                if s != self.pLinked:
                    r = s.opts['readonly']
                    if not r:
                        s.setReadonly(True)
                    s.opts['readonly-backup'] = r
                    s.linkedFn = lambda param, val, s=s: s.setValue(val)
                    m.sigValueChanged.connect(s.linkedFn)
                link(m,s)
        link(self._linkedAxis.p, self.p)
       
        
    def unlinkFromAxis(self):
        def unlink(master, slave):
            for m, s in zip(master.childs,slave.childs):
                if s != self.pLinked:
                    r = s.opts.pop('readonly-backup')
                    s.setReadonly(r)
                    m.sigValueChanged.disconnect(s.linkedFn)
                unlink(m,s)
        unlink(self._linkedAxis, self.p)


    def duplicate(self, orientation=None):
        '''
        make a duplicate of this axiswith the same parameters
        '''
        if orientation is None:
            orientation = self.orientation
        a  = self.__class__(self.p.name(), self.p.value(), 
                            orientation, self.p.saveState())
        return a


    def remove(self):
        self.p.remove()



class StackAxis(Axis):
    '''
    Axis representing the dimension built by all input layers (stack)
    '''
    def __init__(self, *args):
        Axis.__init__(self, *args)

        
    def registerStackParam(self, pStack):
        self.pStack = pStack
        
        self.pRange.setOpts(limits=['linear', 'individual', 'fromName'])
        self.pRange.sigValueChanged.connect(lambda param, val: 
                [ch.setOpts(readonly=val!='individual') for ch in pStack.childs])
        self.pRange.sigValueChanged.connect(lambda param, val: 
                [self.pFromName.show(val=='fromName')])
        
        self.pScale.sigValueChanged.connect(self._setPStackValues)
        self.pOffset.sigValueChanged.connect(self._setPStackValues)
        self.pStack.sigChildAdded.connect(self._setPStackValues)
        self.pStack.sigChildRemoved.connect(self._setPStackValues)
        self._setPStackValues()

        try:
            self.pFromName = self.p.addChild({
                    'name':'eval(name)',
                    'type':'str',
                    'value':'name[0:4]',
                    'visible':False})
            
        except Exception:
            self.pFromName = self.p.param('eval(name)')
            self.pFromName.sigValueChanged.disconnect()
        self.pFromName.sigValueChanged.connect(self._setPStackValues)


    def getNextStackValue(self, name):
        l = len(self.pStack.childs)
        #individual numbering
        if self.pRange.value() == 'individual':  
            if l > 1:
                return self.pStack.childs[0].value()+1
        else:
            #linear numbering
            scale = self.pScale.value()
            offset = self.pOffset.value()
            if self.pRange.value() == 'linear':
                return l*scale+offset
            else:
                #numbering from name
                try:
                    val = float(eval(self.pFromName.value(), 
                                     #GLOBALS:
                                     {'name':name})
                                )*scale+offset
                    return val
                except Exception, err:
                    print err


    #TODO: clean following messy defs  
    def _setNewStackValue(self, parent, child, index):
        l = len(parent.childs)
        if self.pRange.value() == 'individual':  
            if l > 1:
                child.setValue(parent.childs[0].value()+1)
        else:
            self._setChildValue(child,l)
    

    def _setChildValue(self, ch,i):
        scale = self.pScale.value()
        offset = self.pOffset.value()
        if self.pRange.value() == 'linear':

            ch.setValue(i*scale+offset)
        else:
            try:
                #evaluate value from expression:
                val = float(eval(self.pFromName.value(), 
                                 #GLOBALS:
                                 {'name':ch.name()})
                            )*scale+offset
                
                ch.setValue(val)
            except Exception, err:
                print err


    def _setPStackValues(self):
        if self.pRange.value() == 'individual':
            return
        for i,ch in enumerate(self.pStack.childs):
            self._setChildValue(ch,i)



class _List(list):
    #only needed to attach attributes to a list
    pass