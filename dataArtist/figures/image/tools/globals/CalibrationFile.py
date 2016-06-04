import numpy as np
from pyqtgraph_karl.Qt import QtGui

from imgProcessor.camera.CameraCalibration import CameraCalibration
from fancywidgets.pyQtBased.ArgSetter import ArgSetter

from dataArtist.widgets.GlobalTool import GlobalTool


class CalibrationFile(GlobalTool):
    '''
    Create and view all individual camera calibrations coefficients
    
    Right click on 'infos' to view or remove a coefficient
    
    Selected light range and calibration dates will be used in tool
    'CorrectCamera'
    '''
    icon = 'camCalFile.svg'
    
    def __init__(self, display):
        GlobalTool.__init__(self, display)

        self.calibrations = []

        self._last_dir  = None
        self._cal_file_path = None
        self._curIndex = 0

        pa = self.setParameterMenu() 

        pNew = pa.addChild({
            'name': 'New',
            'type': 'action'})   
        pNew.sigActivated.connect(self._createNew) 
        
        pLoad = pa.addChild({
            'name': 'Load',
            'type': 'action'})   
        pLoad.sigActivated.connect(self._loadFromFile) 

        self.pCal = pa.addChild({
            'name': 'Calibration',
            'type': 'list',
            'value':'-'}) 
        self.pCal.sigValueChanged.connect(self._pCalChanged)

        self.pAutosave = self.pCal.addChild({
            'name': 'Autosave',
            'type': 'bool',
            'visible':True})   

        self.pModified = self.pCal.addChild({
            'name': 'Modified',
            'type': 'bool',
            'visible':False,
            'readonly':True})   

        self.pAutosave.sigValueChanged.connect(self._pAutoSaveChanged)

        pSave = self.pCal.addChild({
            'name': 'Save as',
            'type': 'action',
            'visible':False})   
        pSave.sigActivated.connect(lambda:self._saveToFile()) 

#         pUnload = self.pCal.addChild({
#             'name': 'Unload',
#             'type': 'action',
#             'visible':False
#             })   
#         pUnload.sigActivated.connect(self._unloadCalibration) 

        self.pLight  = self.pCal.addChild({
            'name': 'Light spectra',
            'type': 'list',
            'limits':[],
            'value':'',
            'visible':False}) 
        self.pLight.sigValueChanged.connect(self._updateInfo)

        for name in ('dark current', 'flat field', 'lens',
                     'noise', 'psf', 'balance'):

            pDates  = self.pCal.addChild({
                'name': name,
                'type': 'list',
                'limits':[],
                'value':'',
                'visible':False}) 
            
            aView = QtGui.QAction('View', self)
            aDel = QtGui.QAction('Remove', self)
            aView.triggered.connect(lambda checked, n=name:
                                    self._viewCurrentCoeff(n))
            aDel.triggered.connect(lambda checked, n=name: 
                                    self._removeCurrentCoeff(n))
            pDates.addChild({
                'name': 'Info',
                'type': 'str',
                'readonly':True,
                'value':'',
                'addToContextMenu':[aView,aDel]}) 
            pDates.sigValueChanged.connect(
                    lambda p,v, n=name: self._pDatesChanged(p,v,n))
           

    def _removeCurrentCoeff(self, name):
        c = self._checkCal()
        pDates = self.pCal.param(name)
        val =  pDates.value()
        
        c.deleteCoeff(name, val, self.pLight.value())
        
        l = list(pDates.opts['limits'])
        l.remove(val)
        pDates.setLimits(l)
        
        if not l:
            pDates.hide()
        
        self.pModified.setValue(True)
        self._autosave()
        

    def _viewCurrentCoeff(self, name):
        c = self.getCurrentCoeff(name)
        if not type(c) is tuple:
            c = (c,)
        for data in c:
            #display calibration data if is image
            if type(data) is np.ndarray and data.ndim == 2:
                date = self.pCal.param(name).value()
                self.display.workspace.addDisplay(
                    data=[data],title='Calibration: %s' %name,
                    names=[date])
            else:
                print data


    def getCurrentCoeff(self, name):
        c = self._checkCal()
        try:
            return c.getCoeff(name, self.pLight.value(), 
                          self.pCal.param(name).value())[2]
        except TypeError:
            raise KeyError("current calibration doesn't have [%s]" %name)


    def currentCameraMatrix(self):
        c = self.curCal
        if c is None:
            return
        l = c.getLens(self.pLight.value(), self.pCal.param('lens').value())
        return l.coeffs['cameraMatrix']
        

    def _pAutoSaveChanged(self, p, v):
        self.pModified.show( len(self.calibrations) and not v )
        if v:
            self._autosave()
            

    def _pCalChanged(self, param, value):
        self._curIndex = param.opts['limits'].index(value)
        self._updateInfo()


    def _pDatesChanged(self, param, date, typ):
        '''
        update infos for chosen date and calibration typ
        '''
        ch =  param.childs[0]
        if date == '-':
            ch.hide()
        else:
            ch.show()
            ch.setValue( self.curCal.infos(typ, self.pLight.value(), date) )


    def _createNew(self):
        a = ArgSetter('New camera calibration', {
                'camera name':{
                                'value': 'change me', 
                                'dtype':str},
                'bit depth': {
                                'value':16, 
                                'limits':[8,12,14,16,24,32], 
                                'dtype':int,
                                'tip':'e.g. 16 for 16 bit'} })
        a.exec_()
        if a.result():
            c = CameraCalibration()
            self.calibrations.append(c)

            name = a.args['camera name']
            c.setCamera(name,a.args['bit depth'])
            self.calibrations.append(c)
            self.pModified.setValue(True)
            l = list(self.pCal.opts['limits'])
            l.append(name)
            self.pCal.setLimits(l)
            [p.show() for p in self.pCal.childs]


    def _loadFromFile(self):
        d = self.display.workspace.gui.dialogs.getOpenFileName(
                            filter='*%s' %CameraCalibration.ftype)
        if d:
            self._cal_file_path = d
            self._last_dir = d.dirname()
            
            c = CameraCalibration.loadFromFile(d) 
            self.calibrations.append(c)
            
            [p.show() for p in self.pCal.childs]
            self._curIndex = -1
            self.pCal.setLimits([c.coeffs['name'] for c in self.calibrations])

            self._updateInfo()


    @property
    def curCal(self):
        try:
            return self.calibrations[self._curIndex]
        except IndexError:
            return None


    def udpateFlatField(self, arr, error=None):
        c = self._checkCal()

        a = ArgSetter('Update flat field', {
                'date':{
                        'value': c.currentTime(), 
                        'dtype':str,
                        'tip':'Please stick to the date format'},
                'light spectrum':{
                        'value': 'visible', 
                        'dtype':str,
                        'tip':"e.g. 'IR'"},                                        
                'info': {
                        'value':'[change me]', 
                        'dtype':str} })
        a.exec_()
        if a.result():
            date = a.args['date']
            info = a.args['info']
            c.addFlatField(arr, date, info,
                           error, a.args['light spectrum'])
            self._updateInfo()
            
            self.pModified.setValue(True)
        self._autosave()


    def updateDarkCurrent(self, slope, intercept):
        c = self._checkCal()

        a = ArgSetter('Update dark current', {
                'date':{
                        'value': c.currentTime(), 
                        'dtype': str,
                        'tip':'Please stick to the date format'},                                     
                'info': {
                        'value':'[change me]', 
                        'dtype': str} })
        a.exec_()
        if a.result():
            date = a.args['date']
            info = a.args['info']
            c.addDarkCurrent(slope, intercept, date, info, error=None)
            self._updateInfo()
            
            self.pModified.setValue(True)
        self._autosave()


    def _checkCal(self):
        c = self.curCal
        if c is None:
            print ('no calibration chosen - load now')
            self.showMenu()
            c = self.curCal
            if c is None:
                self._loadFromFile()
            c = self.curCal
            if c is None:
                raise Exception('no calibration chosen')
        return c     


    def updateNoise(self, nlf_coeff):
        c = self._checkCal()

        a = ArgSetter('Update noise', {
                'date':{
                        'value': c.currentTime(), 
                        'dtype':str,
                        'tip':'Please stick to the date format'},                                     
                'info': {
                        'value':'[change me]', 
                        'dtype':str
                        }
                    })
        a.exec_()
        if a.result():
            date = a.args['date']
            info = a.args['info']
            c.addNoise(nlf_coeff, date, info, error=None)
            self._updateInfo()
            self.pModified.setValue(True)
        self._autosave()


    def updateDeconvolutionBalance(self, val):
        c = self._checkCal()
        a = ArgSetter('Update deconvolution balance', {
                'value':{'value':str(val),
                         'dtype':float },
                'date':{
                        'value': c.currentTime(), 
                        'dtype':str,
                        'tip':'Please stick to the date format'},                                     
                'info': {
                        'value':'[change me]', 
                        'dtype':str },
                'light_spectrum':{
                        'value':'visible', 
                        'dtype':str } })
        a.exec_()
        
        if a.result():
            value = a.args['value']
            date = a.args['date']
            info = a.args['info']
            l = a.args['light_spectrum']
            c.addDeconvolutionBalance(value, date, info, l)
            self._updateInfo()
            self.pModified.setValue(True)

        self._autosave()



    def updatePSF(self, psf):
        c = self._checkCal()
        a = ArgSetter('Update Point spread function', {
                'date':{
                        'value': c.currentTime(), 
                        'dtype':str,
                        'tip':'Please stick to the date format'},                                     
                'info': {
                        'value':'[change me]', 
                        'dtype':str
                        },
                'light_spectrum':{
                        'value':'visible', 
                        'dtype':str
                        }
                })
        a.exec_()
        
        if a.result():
            date = a.args['date']
            info = a.args['info']
            l = a.args['light_spectrum']
            c.addPSF(psf, date, info, l)
            self._updateInfo()
            self.pModified.setValue(True)

        self._autosave()


    def updateLens(self, lens):
        c = self._checkCal()

        a = ArgSetter('Update Lens', {
                'date':{
                        'value': c.currentTime(), 
                        'dtype':str,
                        'tip':'Please stick to the date format'},                                     
                'info': {
                        'value':'[change me]', 
                        'dtype':str },
                'light_spectrum':{
                        'value':'visible', 
                        'dtype':str } })
        a.exec_()
        
        if a.result():
            date = a.args['date']
            info = a.args['info']
            l = a.args['light_spectrum']
            c.addLens(lens, date, info, l)
            self._updateInfo()
            
            self.pModified.setValue(True)     
        self._autosave()


    def correct(self, **kwargs):
        '''
        Call CameraCalibration.correct()
        with added kwargs as defined by the tool settings
        '''
        names = ('dark current','flat field','lens','noise','psf')
        dates = {}
        for name in names:
            val = self.pCal.param(name).value()
            if val == '-':
                print('''
                no calibration found for [%s] 
                at the chosen light spectrum [%s]''' %(name, self.pLight.value()))
                val = None
            dates[name]=val
            
        kwargs.update({
            'light_spectrum':self.pLight.value(),
            'date':dates })
        return self.curCal.correct(**kwargs)
        
        
    def _updateInfo(self):
        c = self.curCal
        self.pCal.setValue(c.coeffs['name'])
        #needs to be copy of list - otherwise limits would not be updated:
        l_new = list(c.coeffs['light spectra'])
        self.pLight.setLimits(l_new)
        ll = self.pLight.value()
        for name in ('dark current','flat field',
                     'lens', 'noise', 'psf', 'balance'):
            dates = c.dates(name, ll)
            if not dates:
                dates = ['-']
            param = self.pCal.param(name)
            param.setLimits(dates)


    def _saveToFile(self, path=None):
        kwargs = {'filter':'*%s' %CameraCalibration.ftype}
        if self._last_dir != None:
            kwargs['directory']=self._last_dir
        if path is None: 
            path = self.display.workspace.gui.dialogs.getSaveFileName(**kwargs)
        if path:
            self._cal_file_path = path
            c = self.calibrations[self._curIndex]
            c.saveToFile(path) 
            self.pModified.setValue(False)
            print 'camera calibration saved'


    def _autosave(self):
        if self.pAutosave.value():
            self._saveToFile(self._cal_file_path)
                

    def saveState(self, state={}):
        GlobalTool.saveState(self, state)
        state['cal dir'] = self._last_dir
        

    def restoreState(self, state):
        GlobalTool.restoreState(self, state)
        self._last_dir = state['cal dir']


#     def save(self, session, path):
#         l = {}
#         l['cal dir'] = self._last_dir
#         session.addContentToSave(l, *path+('general.txt',))
# 
# 
#     def restore(self, session, path):
#         l =  eval(session.getSavedContent(*path +('general.txt',) ))
#         self._last_dir = l['cal dir']