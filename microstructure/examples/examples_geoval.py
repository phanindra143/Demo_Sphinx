# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 12:14:15 2020

@author: pirkelma
"""
from MPaut import geoval_subprocess

# launch GeoVal for control from within python
geo_comm = geoval_subprocess.GeoVal_Communicator(output_folder='output', executable='../bin/geo_val_parallel.exe')


# looping over all the objects in geo_val_orig.exe software
for type in ['sphere', 'tube', 'prism', 'fibre', 'voronoi_polyeder', 'platonic_solid']:
        
    # creates an empty RVE
    geo_comm.initialize_rve(rve_dims=32, voxel_size_um=1.0)
    geo_comm.set_randseed(42)
    
    # Assigning corresponding parameters for each type of object. 
    if type == 'sphere' :
        geo_comm.introduce_objects(N=4, object_type= type, 
                                    shape_description={'radius': 5.0e-6})
    elif type == 'tube' :
      geo_comm.introduce_objects(N=4, object_type= type, 
                                    shape_description={'radius': 5.0e-6, 'length': 20.0e-6, 'inner_radius': 3.0e-6})
    elif type == 'prism' :
      geo_comm.introduce_objects(N=4, object_type= type, 
                                    shape_description={'edge_length': 5.0e-6, 'thickness': 5.0e-6, 'n_edges': 4})
    elif type == 'fibre' :
      geo_comm.introduce_objects(N=4, object_type= type, 
                                    shape_description={'radius': 5.0e-6, 'shell': 1.0e-6})

    elif type == 'voronoi_polyeder' :
      geo_comm.introduce_objects(N=10, object_type= type, 
                                    shape_description={'radius': 5.0e-6})
    elif type == 'platonic_solid' :
      geo_comm.introduce_objects(N=4, object_type= type, 
                                    shape_description={'edge_length': 10.0e-6, 'variation': 5.0e-6, 'n_faces': 6})
    
    # # distribute the objects s.t. there is no overlap
    # geo_comm.distribute()
    
    # # voxel operations
    # geo_comm.delete_small_regions()
    # geo_comm.intro_at_interfaces()
    
    # # get information about the volumes
    # vol_frac = geo_comm.get_volume_fractions()
    # print("volume fractions: ", vol_frac)
    
    # # get information about regions
    # reg_ana = geo_comm.get_3d_region_analysis()
    # print("region analysis: ", reg_ana)
    
    # save voxels to file
    geo_comm.store_voxels('voxels.val')
    
   
    # 3D view of voxels 
    if type == 'sphere' :
        geo_comm.view_voxels('sphere.jpg')
    elif type == 'tube' :
        geo_comm.view_voxels('tube.jpg')
    elif type == 'prism' :
        geo_comm.view_voxels('prism.jpg')
    elif type == 'fibre' :
        geo_comm.view_voxels('fibre.jpg')
    elif type == 'voronoi_polyeder' :
        geo_comm.view_voxels('voronoi_polyeder.jpg')
    elif type == 'platonic_solid' :
        geo_comm.view_voxels('platonic_solid.jpg')
    
    
# # end communication to give control back to the GUI
geo_comm.end_communication()

# quit GeoVals
# geo_comm.close()
