# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 12:14:15 2020

@author: pirkelma
"""
from MPaut import geoval_subprocess

# launch GeoVal for control from within python
geo_comm = geoval_subprocess.GeoVal_Communicator(output_folder='output', executable='../bin/geo_val_parallel.exe')

# create an empty RVE
geo_comm.initialize_rve(rve_dims=32, voxel_size_um=1.0)
geo_comm.set_randseed(42)

# add some spheres
geo_comm.introduce_objects(N=15, object_type='sphere')
geo_comm.introduce_objects(N=5, object_type='sphere', 
                           shape_description={'radius': 10.0e-6})

# distribute the objects s.t. there is no overlap
geo_comm.distribute()

# voxel operations
geo_comm.delete_small_regions()
geo_comm.intro_at_interfaces()

# get information about the volumes
vol_frac = geo_comm.get_volume_fractions()
print("volume fractions: ", vol_frac)

# get information about regions
reg_ana = geo_comm.get_3d_region_analysis()
print("region analysis: ", reg_ana)

# save voxels to file
geo_comm.store_voxels('voxels.val')

# 3D view of voxels
geo_comm.view_voxels()

# end communication to give control back to the GUI
geo_comm.end_communication()

# quit GeoVals
#geo_comm.close()