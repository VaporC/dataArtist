# -*- mode: python -*-

# This is the *.spec-file used by 'pyinstaller' to create a portable version
# of 'datartist'.


global pkg_dir
pkg_dir = os.path.dirname(os.path.abspath(os.curdir))


def addDataFiles():
    import os
    extraDatas = []
    dirs = [
    	#(root in temp folder, pos. of disk)
   		('appbase', os.path.join(pkg_dir,'appBase', 'appbase', 'media')),
   		('dataArtist', os.path.join(pkg_dir,'dataartist', 'dataArtist', 'media')),
   		('dataArtist', os.path.join(pkg_dir,'dataartist', 'dataArtist','scripts')),
   	#	('dataArtist', os.path.join(pkg_dir,'dataartist', 'dataArtist','tutorials')),
   	#	('bat', os.path.join(pkg_dir,'dataartist', 'dataArtist','bat')),
   		('fancywidgets', os.path.join(pkg_dir,'fancyWidgets', 'fancywidgets', 'media'))
    		]
    for loc, d in dirs:
        for root, subFolders, files in os.walk(d):
            for file in files:
                r = os.path.join(d,root,file) 
                extraDatas.append((r[r.index(loc):], r, 'DATA'))

    return extraDatas


a = Analysis(['dataArtist\\gui.py'],
             pathex=[
             	os.path.join(pkg_dir,'pyqtgraph_karl'), 
             	os.path.join(pkg_dir,'fancyTools'), 
             	os.path.join(pkg_dir,'fancyWidgets'), 
             	os.path.join(pkg_dir,'imgprocessor'), 
             	os.path.join(pkg_dir,'appBase'), 
             	#os.path.join(pkg_dir,'interactiveTutorial'), 
             	'', 
             	os.path.join(pkg_dir,'dataartist')],
             	
             hiddenimports=[

             	#'mpl_toolkits.mplot3d',#3d surface plot with matplotlib
             	#'pygments.lexers.SourcesListLexer',
             	
             	'scipy.linalg._decomp_u',#???for tool: createSpatialSensitivity Array
             	#'ctypes',
             	
             	#skimage:
                'scipy.special._ufuncs_cxx',
                #'skimage.external.tifffile._tifffile',
             	#'skimage.filter.rank.generic' 
             	#'skimage.filter.rank.core_cy', 
             	#'skimage.draw.draw',
                # 'skimage.draw._draw',
                # 'skimage.draw.draw3d',
                # 'skimage._shared.geometry',
                # 'skimage._shared.interpolation',
                # 'skimage.filter.rank.core_cy'
             	],
             	
             hookspath=None,
             runtime_hooks=None)
             
#to prevent the error: 'WARNING: file already exists but should not: ...pyconfig.h'
for d in a.datas:
    if 'pyconfig' in d[0]: 
        a.datas.remove(d)
        break

a.datas += addDataFiles()             
  
#needed by numba:
a.datas += [ ('llvmlite.dll', 'C:\\Python27\\Lib\\site-packages\\llvmlite\\binding\\llvmlite.dll', 'DATA') ]
a.datas += [ ('vcruntime140.dll', 'C:\\Python27\\Lib\\site-packages\\llvmlite\\binding\\vcruntime140.dll', 'DATA') ]
a.datas += [ ('msvcp140.dll', 'C:\\Python27\\Lib\\site-packages\\llvmlite\\binding\\msvcp140.dll', 'DATA') ]
#at the moment the visual studio redistributables 2015 also have to be installed


pyz = PYZ(a.pure)


#make exe file:
exe = EXE(pyz,
      a.scripts,
      exclude_binaries=1,
      name='dataArtist.exe',
      debug=False,
      strip=None,
      upx=True,#should be disabled for PtQt4 according to https://groups.google.com/forum/#!topic/pyinstaller/GEL1QQfpHLI
      console=False, 
      icon=os.path.join(pkg_dir,'dataartist','dataArtist','media','logo.ico'))

#make dist folder:
dist = COLLECT(exe, 
	  a.binaries, 
      a.zipfiles,
      a.datas,
      name="dataArtist")
          

