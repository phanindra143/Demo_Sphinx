# -*- coding: utf-8 -*-
import os
import ast
import numpy as np
import matplotlib.pyplot as plt

from pprint import pformat
from pathlib import Path

from MPaut import geoval_subprocess


def generate_zta_rves(rve_dim=32, n_obj=50, n_vol_fracs=3, n_rves=3, 
                      outpath='output'):
    """Generate a number of RVEs for ZTA ceramics using a voronoi method.
    
    You can specify the number of voronoi centers used for the RVEs,
    the number of different target volume fractions for the two components
    (alumina and zirconia) and the number of RVEs to generate for each target 
    volume fraction.
    
    ``n_vol_fracs`` different target volume fractions will be considered (i.e.
    all volume fractions from 1/n_vol_fracs, 2/n_vol_fracs, ..., 
    (n_vol_fracs - 1)/n_vol_fracs ). The target volume fraction is used to 
    decide how many of the introduces particles will be assigned to the 
    zirconia or alumina phase. This gives roughly the desired target volume 
    fraction.
    
    In total ``(n_vol_fracs - 1) * n_rves`` will be created.
    

    Parameters
    ----------
    rve_dim : int, optional
        Number of voxels along each axis of the RVE.
    n_obj : int, optional
        Number of voronoi centers used for generating the RVEs. The default is 50.
    n_vol_fracs : int, optional
        Number of different target volume fractions of the two constituents to
        generate. The default is 3.
    n_rves : int, optional
        Number of RVEs to generate for each target volume fraction. The default is 3.
    outpath : pathlib.Path
        Path to a folder were the results will be stored.

    """
    outpath = Path(outpath) / f'zta_{n_obj}'
    
    for i in range(1,n_vol_fracs):
        frac = 1.0/n_vol_fracs * i  # fraction of objects that will be of other phase
        
        for j in range(0,n_rves):
            # launch GeoVal for control from within python
            geo_comm = geoval_subprocess.GeoVal_Communicator(output_folder= outpath / f'frac_{frac}/rve_{j}', 
                                                             executable='../bin/geo_val_parallel.exe')
            
            # create an empty RVE
            geo_comm.initialize_rve(rve_dims=rve_dim, voxel_size_um=1.0)
            geo_comm.set_randseed(j)
            
            # 1. option: generating ZTA structures with voronoi method
            geo_comm.introduce_objects(N=round(frac*n_obj), object_type='voronoi_polyeder', 
                                        shape_description={'radius': 5.0e-6})
            geo_comm.introduce_objects(N=round((1-frac)*n_obj), object_type='voronoi_polyeder', 
                                       shape_description={'radius': 5e-6})
            
            # # distribute the objects s.t. there is no overlap
            geo_comm.distribute()
            
            geo_comm.store_voxels('voxels.val')
            geo_comm.store_objects('objects.val')
            
            with open(geo_comm.output_folder / 'info.txt', 'w') as info:
                info_dict = {}
                info_dict["volume_fractions"] = geo_comm.get_volume_fractions()
                info_dict["chord_length_analysis"] = geo_comm.get_chord_length_analysis()
                info_dict["object_analysis"] = geo_comm.get_object_analysis()
                info_dict["3d_region_analysis"] = geo_comm.get_3d_region_analysis()
                info.write(pformat(info_dict))
             
             # 3D view of voxels
            geo_comm.view_voxels('snapshot.jpg')
        
            # end communication to give control back to the GUI
            geo_comm.close()
            
    return outpath
            
def plot_rve_statistics(data_path):
    """Loads data of the generated RVEs at the given path and plots some 
    statistics about them.
    

    Parameters
    ----------
    data_path : pathlib.Path
        Path to the output folders of the automated RVE generation.

    """
    vol_fracs = {}
    for root, dirs, files in os.walk(data_path):
        if 'info.txt' in files:
            # gather information about generated RVE
            info = Path(root, 'info.txt').read_text()
            data_dict = ast.literal_eval(info)
            
            # get target volume fraction from folder name
            target_vol_frac = float(Path(root).parent.name.split('_')[1])
            actual_vol_frac = data_dict['volume_fractions'][4]
            
            if not target_vol_frac in vol_fracs:
                vol_fracs[target_vol_frac] = []
                
            vol_fracs[target_vol_frac].append(actual_vol_frac)
    
    target_vols = np.array(list(vol_fracs.keys()))
    av = np.vstack(list(np.array(v) for v in vol_fracs.values()))
    
    # deviations from desired volume fractions
    fig, ax = plt.subplots()
    ax.plot(target_vols, np.vstack(av), marker='o', linestyle='')
    ax.plot([0,1],[0,1], color='k', linestyle='--', label='ideal volume fraction')
    ax.set_xlabel('Target volume fraction for RVE')
    ax.set_ylabel('Actual volume fraction of RVE')
    ax.set_title("Deviations from desired volume fractions")
    ax.grid()
    ax.legend()
    
    # histogram of volume fraction occurences
    fig, ax = plt.subplots()
    all_volume_fractions = av.flatten()
    ax.hist(all_volume_fractions, bins=20)
    ax.set_xlabel('Volume fraction of RVE')
    ax.set_ylabel('Number of RVEs with given volume fraction')
    ax.set_title("Histogram of RVE volume fractions")
    plt.show()
    
outpath = generate_zta_rves(rve_dim=32, n_obj=20, n_vol_fracs=5, n_rves=2, outpath='output')
plot_rve_statistics(outpath)
