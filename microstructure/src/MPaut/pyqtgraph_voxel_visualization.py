# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 10:58:43 2020

@author: pirkelma
"""
import numpy as np
import re
import functools
try:
    import pyqtgraph as pg
    from pyqtgraph.Qt import QtCore, QtGui
    import pyqtgraph.opengl as gl
    plotting_available = True
except ModuleNotFoundError:
    plotting_available = False
    print("error Qt libraries not found! 3D visualizations will not be available.")

def _parse_line(line, rx_dict):
    """
    Do a regex search against all defined regexes and
    return the key and match result of the first matching regex

    """

    for key, rx in rx_dict.items():
        match = rx.search(line)
        if match:
            return key, match
    # if there are no matches
    return None, None

def view_RVE(file, phases, screenshot_file=None):
    if plotting_available:
        data = open(file).readlines()
        file = "".join(data)
        rx_dict = {
            'dims': re.compile(r'^(?P<nx>\d+\s*)(?P<ny>\d+\s*)(?P<nz>\d+\s*)(?P<edge_length>\d*\.?\d+\s*)\n'),
            }
        key, match = _parse_line(data[0], rx_dict)
        nx = int(match['nx'])
        ny = int(match['ny'])
        nz = int(match['nz'])
        
        x, y, z = np.indices((nx, ny, nz))
        
        
        #phases = dict(zip([1 + 6 * i for i in range(phases_count)], [np.empty(x.shape, dtype=np.bool)] * phases_count))
        phase_voxels = {p: np.empty(x.shape, dtype=np.bool) for p in phases}
        
        for phase_id, phase_vals in phase_voxels.items():
            ccl = 1
            for ix in range(nx):
                cl = ccl + nx * ix
                for iy in range(ny):
                    phase_vals[ix, iy] = list(map(lambda zz: int(zz) // (phase_id * 100000) >= 1, data[cl+iy].split())) 
                ccl += 1
                    #list(map(int, data[cl + iy].split()))
        
        #val_rx = re.compile(r'(^(\d+\s*){{{nx}}}\n){{{ny}}}'.format(nx=nx, ny=ny))
        #val_rx = re.compile(r'^(\d+\s*){{{nx}}}\n'.format(nx=nx))
        
        #cube1 = (x < 3) & (y < 3) & (z < 3)
        #cube2 = (x >= 5) & (y >= 5) & (z >= 5)
        #link = abs(x - y) + abs(y - z) + abs(z - x) <= 2
        #voxels = cube1 | cube2 | link
        voxels = functools.reduce(lambda x, y: x | y, phase_voxels.values())
        
        
        # Set the colors for evey object and visualize the screen
        colors = np.zeros(voxels.shape + (4,), dtype=np.ubyte)
        
        cp = [(0.00784313725490196, 0.24313725490196078, 1.0),
             (1.0, 0.48627450980392156, 0.0),
             (0.10196078431372549, 0.788235294117647, 0.2196078431372549),
             (0.9098039215686274, 0.0, 0.043137254901960784),
             (0.5450980392156862, 0.16862745098039217, 0.8862745098039215),
             (0.6235294117647059, 0.2823529411764706, 0.0),
             (0.9450980392156862, 0.2980392156862745, 0.7568627450980392),
             (0.6392156862745098, 0.6392156862745098, 0.6392156862745098),
             (1.0, 0.7686274509803922, 0.0),
             (0.0, 0.8431372549019608, 1.0)]
        for i, phase_vals in enumerate(phase_voxels.values()):
            colors[phase_vals] = *tuple(map(lambda x: x * 255, cp[i])), 255
        
        pg.mkQApp()    
        w = gl.GLViewWidget()
        w.resize(600,600)
        w.setBackgroundColor('w')
        w.opts['distance'] = 155 * voxels.shape[0]/64
        w.show()
        w.setWindowTitle('RVE 3D view')
    
        v = gl.GLVolumeItem(colors, sliceDensity=20)
        v.translate(0,0,0)
        w.addItem(v)
        
        b = gl.GLBoxItem(size=QtGui.QVector3D(*voxels.shape))
        b.setColor('k')
        w.addItem(b)
        
        if screenshot_file is not None:
            # save screenshot of RVE
            screenshot = w.renderToArray((600, 600))
            pg.makeQImage(screenshot).save(str(screenshot_file))
            w.close()
        else:
            import sys
            if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
                QtGui.QApplication.instance().exec_()
    else:
        print("plotting features are not available")
    
    return 0

if __name__ == "__main__":
    view_RVE('output/voxels.val', 2)
