# -*- coding: utf-8 -*-
from MPaut import voxsm_subprocess

from pathlib import Path
import os

def mesh_zta_rves(data_path):
    """Create meshes from the generated voxel RVEs at the given path.
    
    The function will launch VoxSM and generate a mesh for all ``voxel.val`` 
    files under the given path.
    
    Parameters
    ----------
    data_path : pathlib.Path
        Path to the output folders of the automated RVE generation.

    """
    voxsm = voxsm_subprocess.VoxSM_Communicator('../bin/VoxSM_2017_x64.exe')
    
    for root, dirs, files in os.walk(data_path):
        if 'voxels.val' in files:
            voxel_file = Path(root, 'voxels.val')
            voxsm.open_voxel_file(voxel_file)
            voxsm.split_regions()
            voxsm.generate_mesh()
            voxsm.adaptive_smooth()
            voxsm.adaptive_simplify()
            voxsm.store_mesh(call_tetview=True)
            voxsm.store_ansys(introduce_GB_prisms=False)
            

# outpath = 'output/zta_Voronoi_R5_Obj_20_Dim_16_No_Frac11'
# mesh_zta_rves(outpath)

outpath13 = 'output/zta_Voronoi2_R5_Obj_20_Dim_16_No_Frac11'
mesh_zta_rves(outpath13)
