# -*- coding: utf-8 -*-
"""
This example demonstrates how the microstructure generation pipeline can be
used to generate meshes for porous ZTA microstrutures.

This example originates from the AirFox project where the goal was to model 
the matrix phase of infiltrated ceramic fibre composites. 
The matrix consists of Alumina (Al2O3) and Zirconia (ZrO2) with a volume ratio 
of Al2O3 : ZrO2 = 84 / 16.
In addition, the microstructure has a relatively high porosity of about 30 %.

The example demonstrates how to generate multiple RVEs with the given 
properties and how to prepare them into a mesh for simulation with Ansys.
"""
import random
import os
import ast

from pprint import pformat
from pathlib import Path

from MPaut import geoval_subprocess, voxsm_subprocess

def generate_volume_fraction( frac, n_obj, geo_comm, rve_dim=32, voxel_size_um=1.0,
                             randseed=None, method='voronoi', target_porosity=0.0,
                             use_dilation=True):
    """This function generates a two-phase voronoi type RVE with a given volume fraction of the two phases.
    
    There are two different options to generate the RVE. The first method 
    ``'voronoi'`` creates ``n_obj`` GeoVals voronoi objects and assigns them to
    one of the two phases according to the given volume fraction.
    This often produces rather enlongated grains and may not be desired.
    
    Alternatively, the second method ``spheres`` does not directly introduce 
    voronoi objects but instead first introduces ``n_obj`` spheres, 
    distributes them to avoid overlap and then converts them to voronoi 
    objects with the given volume fractions.
    
    After the base RVE has been generated, pores are added by randomly 
    introducing voxels at the corners, edges or faces of the grains until the
    given porosity percentage is achieved. Note that this may not always be
    possible (no checks are performed!).    
    

    Parameters
    ----------
    frac : float
        Target volume fraction for one of the phases. The other phase will have
        a volume fraction of ``1 - frac``.
    n_obj : int
        Number of objects to create in the RVE.
    geo_comm : GeoVal_Communicator
        Communicator object to interact with GeoVal.
    rve_dim : int, optional
        Voxel dimension of RVE. The default is ``32``.
    voxel_size_um : float, optional
        Spacing of a single voxel in the RVE. The default is ``1.0``.
    randseed : int, optional
        Random seed to use for generation. The default is ``None``.
    method : str, optional
        Method to use for the structure generation. The two options are
        ``'voronoi'`` and ``'spheres'``. The default is ``'voronoi'``.
    target_porosity : float, optional
        Target porosity of the RVE. The default is ``0.0``.
    use_dilation : bool, optional
        This option control whether dilation operations are used when adding
        porosity to the RVE. The default is ``True``.

    Returns
    -------
    info_dict : dict
        Dictionary with information about the generated RVE such as volume 
        fractions, porosity, etc.

    """
     # create an empty RVE
    geo_comm.initialize_rve(rve_dims=rve_dim, voxel_size_um=voxel_size_um)
    if randseed is not None:
        geo_comm.set_randseed(randseed)
    
    if method == 'voronoi':
        # 1. option: generating ZTA structures with voronoi method
        geo_comm.introduce_objects(N=round(frac*n_obj), object_type='voronoi_polyeder', 
                                    shape_description={'radius': 5.0e-6})
        geo_comm.introduce_objects(N=round((1-frac)*n_obj), object_type='voronoi_polyeder', 
                                   shape_description={'radius': 5e-6})
        # distribute the objects s.t. there is no overlap
        geo_comm.distribute()
        
    elif method == 'spheres':    
        # 2. option: generate spheres, distribute them and then transform them
        # to voronoi objects
        geo_comm.introduce_objects(N=n_obj, object_type='sphere', 
                                shape_description={'radius': 5.0e-6})
        # distribute the objects s.t. there is no overlap
        geo_comm.distribute()
        geo_comm.distribute()
        geo_comm.distribute()
        
        # transform spheres (phase 1) to voronoi polyeders
        geo_comm.transform_objects(n_obj, 1, 'voronoi_polyeder', 
                                   shape_description={'radius': 5.0e-6})
        
        # split voronoi polyeder (phase 4) to achieve the desired volume fraction
        geo_comm.split_objects(4, fraction=frac)
        
        
        
        
    # add porosity
    vol_fracs = geo_comm.get_volume_fractions()
    
    # split voronoi polyeder (phase 4) to achieve the desired volume fraction
    
    # if vol_fracs[4] < Input_ZrO2[P_ZrO2]:
    #     geo_comm.split_objects(4, fraction=frac)
        
    porosity = 1.0 - sum(vol_fracs.values())
    
    
    # if porosity > target_porosity:
    #     print(f"Volume fractions = {vol_fracs}, porosity = {porosity}")
    #     # randomly deleting pores at corners, edges or faces
    #     mode = random.choice([('corners', 0.01), ('edges', 0.01), ('faces', 0.01)])
    #     #mode = ('corners', target_porosity)
    #     geo_comm.intro_at_interfaces(mode=mode[0], phase=10, fraction=mode[1])
    #     # get new porosity        
    #     vol_fracs = geo_comm.get_volume_fractions()
    #     porosity = 1.0 - sum(vol_fracs.values())
    
    i = 0
    while porosity < target_porosity:
        print(f"Volume fractions = {vol_fracs}, porosity = {porosity}")
        # randomly introduce pores at corners, edges or faces
        mode = random.choice([('corners', 0.3), ('edges', 0.1), ('faces', 0.01)])
        #mode = ('corners', target_porosity)
        geo_comm.intro_at_interfaces(mode=mode[0], phase=0, fraction=mode[1])

        # get new porosity        
        vol_fracs = geo_comm.get_volume_fractions()
        porosity = 1.0 - sum(vol_fracs.values())

        if porosity < target_porosity and use_dilation:
            # randomly dilate existing voxels
            mode = random.choice([1,2,3,4,5])
            
            if vol_fracs[4] > Per_ZrO2:
                geo_comm.dilation(mode, 4, repetitions=1)
            elif vol_fracs[10] > Per_Al2O3:
                geo_comm.dilation(mode, 10, repetitions=1)    
        
            # get new porosity
            vol_fracs = geo_comm.get_volume_fractions()
            porosity = 1.0 - sum(vol_fracs.values())
        
        # make sure we always terminate
        i += 1
        if i > 500:
            break
        
    print(f"Final volume fractions = {vol_fracs}, porosity = {porosity}")
    
    info_dict = {}
    info_dict["porosity"] = porosity
    info_dict["volume_fractions"] = vol_fracs
    info_dict["chord_length_analysis"] = geo_comm.get_chord_length_analysis()
    info_dict["object_analysis"] = geo_comm.get_object_analysis()
    info_dict["3d_region_analysis"] = geo_comm.get_3d_region_analysis()

    return info_dict



''' Code for finding percentage of frac for getting controlled 
   amount of ZrO2, Al2O3 and Porosity in the final structure'''
   
   
# # Required percentage of ZrO2 
# Input_ZrO2 = float(input("Enter Required percentage of  ZrO2 : "))
# # Required percentage of Porosity
# Input_Porosity = float(input("Enter Required percentage of Porosity : "))
# Input_frac = float(Input_ZrO2*100/(100-Input_Porosity))
# print(Input_frac)
# # Required percentage of Al2O3
# Input_Al2O3 = 100 - (Input_ZrO2 + Input_Porosity)

# Required percentage of ZrO2 
# Input_ZrO2 = [55,60,65,70,75,80,85]
Input_ZrO2 = [10,20,30,40,50,60,70,80]
# Required percentage of Porosity
Input_Porosity = 10
# Input_frac = float(Input_ZrO2*100/(100-Input_Porosity))
# Required percentage of Al2O3
# Input_Al2O3 = 100 - (Input_ZrO2 + Input_Porosity)


# set target properties of the RVE
n_rves = 2                # number of RVEs to generate            
# frac = 0.16             # volume fraction of zirconia phase (the alumina phase will have a volume fraction of 1 - this)
# target_porosity = 0.3   # target porosity
# frac = Input_frac/100          
# target_porosity = Input_Porosity/100
rve_dim = 32            # voxel dimensions of the RVEs
n_obj = 60              # number of particles in each RVE

# base_path = Path('airfox') / f'frac_{frac}'


## generate RVEs
# for P_ZrO2 in range(len(Input_ZrO2)):

# for P_Porosity in range(len(Input_Porosity)):
for P_ZrO2 in range(len(Input_ZrO2)):    
    # base_path = Path('Airfox_step_10_nobj_50_rvedim_40')/f'frac_ZrO2_{Input_ZrO2[P_ZrO2]}'
    base_path = Path('Airfox_step_10_nobj_60_rvedim_32')/f'frac_ZrO2_{Input_ZrO2[P_ZrO2]}'
    Input_frac = float(Input_ZrO2[P_ZrO2]*100/(100-Input_Porosity))
    target_porosity = Input_Porosity/100
    frac = Input_frac/100 
    Per_Al2O3 = 100 - (Input_ZrO2[P_ZrO2] + Input_Porosity)
    Per_ZrO2 = Input_ZrO2[P_ZrO2]
    # base_path = Path('Airfox_Vol_Frac')/('Airfox_Vol_Frac')/f'frac_{Input_ZrO2[P_ZrO2]}'
    for j in range(n_rves):
     # launch GeoVal
     geo_comm = geoval_subprocess.GeoVal_Communicator(output_folder= base_path / f'rve_{j}', 
                                                      executable='../bin/geo_val_parallel.exe')
    
     # run the RVE generation
     rve_info = generate_volume_fraction(frac, n_obj, geo_comm, rve_dim, voxel_size_um=1.0, randseed=j, method='spheres',
                                         target_porosity=target_porosity, use_dilation=True)
            
     # store RVE and additional info
     geo_comm.store_voxels('voxels.val')
     geo_comm.store_objects('objects.val')
     geo_comm.view_voxels('snapshot.jpg')
     #geo_comm.view_voxels()
     with open(geo_comm.output_folder / 'info.txt', 'w') as info:
         info.write(pformat(rve_info))
         
         geo_comm.end_communication()
         geo_comm.close()
           


results = {}


# get measure of closeness to target properties for all results
for root, dirs, files in os.walk(base_path):
    if 'info.txt' in files:
        # gather information about generated RVE
        info = Path(root, 'info.txt').read_text()
        data_dict = ast.literal_eval(info)
        
        # get target volume fraction of phase 4 from folder name
        target_vol_frac = float(Path(root).parent.name.split('_')[1])
        
        # compute volume fractions of non-pore phases (4 and 10)
        actual_vol_frac = data_dict['volume_fractions'][4] / data_dict['volume_fractions'][10]
        actual_porosity = data_dict['porosity']
        
        measure = abs(actual_porosity - target_porosity) + abs(actual_vol_frac - target_vol_frac)
        
        results[root] = measure
      

# sort the result to get those that best achieve the desired property (volume fraction and porosity)
results_sorted = list(sorted(results.items(), key=lambda x:x[1]))
print("path to best RVE: ", results_sorted[0][0], " rating: ", results_sorted[0][1])

# run VoxSM mesh generation for the 3 best RVEs
voxsm = voxsm_subprocess.VoxSM_Communicator('../bin/VoxSM_2017_x64.exe')

for root, rating in results_sorted[0:3]:
    print(f"meshing RVE at path {root} (rating = {rating})")
    voxel_file = Path(root, 'voxels.val')
    voxsm.open_voxel_file(voxel_file)
    voxsm.split_regions()
    voxsm.generate_mesh()
    voxsm.adaptive_smooth()
    voxsm.adaptive_simplify()
    voxsm.store_mesh(call_tetview=True, materials=[0], output_path=root, output_basename='pore_phase')
    voxsm.store_mesh(call_tetview=True, materials=[4], output_path=root, output_basename='zirconia_phase')
    voxsm.store_mesh(call_tetview=True, materials=[10], output_path=root, output_basename='alumina_phase')
    voxsm.store_ansys(introduce_GB_prisms=False)