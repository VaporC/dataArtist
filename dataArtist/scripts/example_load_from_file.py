
#replace first layer:
d.addFiles(['PATH\\TO\\FILE.tiff'], indices=[0])

#add layer:
d.addFiles(['PATH\\TO\\FILE.tiff'])

#add multiple layers but don't load:
d.addFiles(['1.tiff','2.tiff','3.tiff'], openfiles=False)
 