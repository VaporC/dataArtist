'''
this module is still in development!

at the moment it is only capable of showing an example surface
'''



from pyqtgraph_karl.Qt import QtCore, QtGui
import pyqtgraph_karl as pg
import pyqtgraph_karl.opengl as gl
import numpy as np


#OWN
from .._view3d import View3d

class _SurfaceView(View3d):
    #dimensions = (4)

    def __init__(self, data=None):
        View3d.__init__(self)
        if data is not None:
            self.setData(data)

    def setData(self, data):


        def psi(i, j, k, offset=(25, 25, 50)):
            x = i-offset[0]
            y = j-offset[1]
            z = k-offset[2]
            th = np.arctan2(z, (x**2+y**2)**0.5)
            phi = np.arctan2(y, x)
            r = (x**2 + y**2 + z **2)**0.5
            a0 = 1
            ps = (1./81.) * 1./(6.*np.pi)**0.5 * (1./a0)**(3/2) * (r/a0)**2 * np.exp(-r/(3*a0)) * (3 * np.cos(th)**2 - 1)
            return ps

        data = np.abs(np.fromfunction(psi, (50,50,100)))
        
        
        print("Generating isosurface..")
        verts, faces = pg.isosurface(data, data.max()/4.)
        md = gl.MeshData(vertexes=verts, faces=faces)
        
        colors = np.ones((md.faceCount(), 4), dtype=float)
        colors[:,3] = 0.2
        colors[:,2] = np.linspace(0, 1, colors.shape[0])
        md.setFaceColors(colors)
       # m1 = gl.GLMeshItem(meshdata=md, smooth=False, shader='balloon')
       # m1.setGLOptions('additive')
        
        #w.addItem(m1)
       # m1.translate(-25, -25, -20)
        
        mesh = gl.GLMeshItem(meshdata=md, smooth=True, shader='balloon')
        mesh.setGLOptions('additive')
        
        self.addItem(mesh)
        mesh.translate(-25, -25, -50)
        mesh.show()

