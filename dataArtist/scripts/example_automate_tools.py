# This example shows how to automate 
# the region-of-interest tool
#=====================================

# this example only works on a image display!

#show the 'Measurement' tool bar, if hidden:
d.showToolBar('Measurement')

#get tool:
roi = d.tools['AverageROI']
av = roi.param('Averaging')
s = d.l.shape

av.setValue('No')
for n in np.linspace(0,0.7,3):
    r = roi.activate()
    r.setPos([int(s[1]*n),int(s[2]*n)])

av.setValue('one side')
for n in np.linspace(0,0.7,10):
    r = roi.activate()
    r.setPos([int(s[1]*n),int(s[2]*n)])