# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 12:14:15 2020

@author: pirkelma
"""
from MPaut import geoval_subprocess

# launch GeoVal for control from within python
geo_comm = geoval_subprocess.GeoVal_Communicator(output_folder='output', executable='../bin/geo_val_parallel.exe')




for r in [15]:
    
   # create an empty RVE 
   geo_comm.initialize_rve(rve_dims=64, voxel_size_um =1.0)
   geo_comm.set_randseed(42)
   
  # add some objects
  
   # geo_comm.introduce_objects(N=5, object_type='voronoi_polyeder',
   #                            shape_description={'radius': (r-5)*1e-6})
   # geo_comm.introduce_objects(N=10, object_type='voronoi_polyeder', 
   #                                shape_description={'radius': r*1e-6})
  
    
   # geo_comm.introduce_objects(N=4, object_type= 'tube', 
   #                                  shape_description={'radius': r*1e-6, 'length': (r+5)*1.0e-6, 'inner_radius': (r-5)*1.0e-6})


   geo_comm.introduce_objects(N=10, object_type= 'sphere', 
                                     shape_description={'radius': r*1.0e-6})
   
   
   # geo_comm.introduce_objects(N=4, object_type= 'prism', 
   #                                  shape_description={'edge_length': r*1e-6, 'thickness': (r-5)*1e-6, 'n_edges': 6})

   # geo_comm.introduce_objects(N=5, object_type= 'fibre', 
   #                                  shape_description={'radius': r*1e-6, 'shell': (r-5)*1e-6})
   
   
   

   # geo_comm.introduce_objects(N=5, object_type= 'sphere', 
                                     # shape_description={'radius': (r+5)*1.0e-6})

  # # distribute the objects s.t. there is no overlap
   # geo_comm.distribute()
   geo_comm.split_objects(phase = 1, fraction=0.5)

  # # voxel operations
   geo_comm.transform_objects(1, 7, 'prism', shape_description={})
   # geo_comm.delete_small_regions(phase=-1, voxel_margin=50)
  # geo_comm.iterative_delete_small_regions(margin_fraction_of_mean=0.7)
   # geo_comm.intro_at_interfaces(mode='edges', phase=1, fraction=1.0)
   
   
   
   
    

  # # get information about the volumes
  # vol_frac = geo_comm.get_volume_fractions()
  # print("volume fractions: ", vol_frac)

  # # get information about regions
  # reg_ana = geo_comm.get_3d_region_analysis()
  # print("region analysis: ", reg_ana)


  
  # save voxels to file
  # 3D view of voxels
   if r == 10 : 
      geo_comm.store_voxels('sphere_del_small_regions_10.val')
      geo_comm.view_voxels('sphere_del_small_regions_10.jpg')
   elif r == 15 :
      geo_comm.store_voxels('sphere_intro_new_voxels_15.val')
      geo_comm.view_voxels('sphere_intro_new_voxels_15.jpg')
   elif r == 20 :
      geo_comm.store_voxels('sphere_del_small_regions_20.val')
      geo_comm.view_voxels('sphere_del_small_regions_20.jpg')
   elif r == 25 :
      geo_comm.store_voxels('fibre_25.val') 
      geo_comm.view_voxels('fibre_25.jpg')
   elif r == 30 :
      geo_comm.store_voxels('fibre_30.val') 
      geo_comm.view_voxels('fibre_30.jpg')
   elif r == 35 :
      geo_comm.store_voxels('fibre_35.val') 
      geo_comm.view_voxels('fibre_35.jpg')
   elif r == 40 :
      geo_comm.store_voxels('fibre_40.val') 
      geo_comm.view_voxels('fibre_40.jpg')

# end communication to give control back to the GUI
geo_comm.end_communication()

# quit GeoVals
#geo_comm.close()