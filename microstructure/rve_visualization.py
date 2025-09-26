# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 10:40:51 2020

@author: pirkelma
"""


from simple_3dviz import Mesh
from simple_3dviz.window import show
from simple_3dviz.utils import render
from simple_3dviz.behaviours.movements import CameraTrajectory
from simple_3dviz.behaviours.trajectory import Circle

# Using simple-3dviz, we can also visualize point clouds and voxels, lines and
# primitives.
# Let us reproduce the voxel grid example from matplotlib that can be
# found here (https://matplotlib.org/3.2.1/gallery/mplot3d/voxels.html)
import numpy as np
import pandas as pd
import regex as re
import time
import sys

import colorsys
import seaborn as sns
import functools

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

def view_RVE(file, phases_count):
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
    phases = {}
    for i in range(phases_count):
        phases[1+6*i] = np.empty(x.shape, dtype=np.bool)
    
    for phase_id, phase_vals in phases.items():
        ccl = 1
        for iz in range(nz):
            cl = ccl + nz * iz
            for iy in range(ny):
                phase_vals[iz, iy] = list(map(lambda x: int(x) // (phase_id * 100000) == 1, data[cl+iy].split())) 
            ccl += 1
                #list(map(int, data[cl + iy].split()))
    
    #val_rx = re.compile(r'(^(\d+\s*){{{nx}}}\n){{{ny}}}'.format(nx=nx, ny=ny))
    #val_rx = re.compile(r'^(\d+\s*){{{nx}}}\n'.format(nx=nx))
    
    #cube1 = (x < 3) & (y < 3) & (z < 3)
    #cube2 = (x >= 5) & (y >= 5) & (z >= 5)
    #link = abs(x - y) + abs(y - z) + abs(z - x) <= 2
    #voxels = cube1 | cube2 | link
    voxels = functools.reduce(lambda x, y: x | y, phases.values())
    
    
    # Set the colors for evey object and visualize the screen
    colors = np.zeros(voxels.shape + (3,), dtype=np.float32)
    
    N = len(phases)
    cp = sns.color_palette("bright")
    for i, phase_vals in enumerate(phases.values()):
        colors[phase_vals] = cp[i]
    #colors[phases[7]] = (0, 0, 1)
    #colors[phases[13]] = (0, 1, 0)
    
    
    # Build a voxel grid from the voxels
    m = Mesh.from_voxel_grid(
        voxels=voxels,
        #sizes=(0.49,0.49,0.49),
        colors=colors
        #colors=(0.8, 0, 0)
    )
    
    
    show(m, title='RVE')
    
    return 0

def main(args):
    if len(args) > 2:
        filename = args[1]
        phases_count = int(args[2])
        print("file: ", filename)
        print("phases_count: ", phases_count)
        view_RVE(filename, phases_count)
    else:
        print(f"usage: python {args[0]} <voxel_file> <number_of_phases>")
    return 0
    
if __name__ == "__main__":
    main(sys.argv)


# Set the colors for evey object and visualize the screen
#colors = np.empty(voxels.shape + (3,), dtype=np.float32)
#colors[link] = (1, 0, 0)
#colors[cube1] = (0, 0, 1)
#colors[cube2] = (0, 1, 0)
"""
show(
    Mesh.from_voxel_grid(voxels=voxels),
    light=(-1, -1, 1),
    behaviours=[
        CameraTrajectory(
            Circle(center=(0, 0, 0), point=(2, -1, 0), normal=(0, 0, -1)),
            speed=0.0004)
    ]
)

# To visualize a pointloud we can simply use the Spherecloud object
from simple_3dviz import Spherecloud
# We start by generating points uniformly distributed in the unit cube
x = np.linspace(-0.7, 0.7, num=10)
centers = np.array(np.meshgrid(x, x, x)).reshape(3, -1).T
spheres_colors = np.array([[1, 1, 0, 1],
                   [0, 1, 1, 1]])[np.random.randint(0, 2, size=centers.shape[0])]
spheres_sizes = np.ones(centers.shape[0])*0.02"""