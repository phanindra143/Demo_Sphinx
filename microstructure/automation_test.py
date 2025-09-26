# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 08:53:35 2020

@author: pirkelma
"""
import glob
from geoval_subprocess import GeoVal_Communicator
from voxsm_subprocess import VoxSM_Communicator

if __name__ == "__main__":
    folder = 'C:/Users/pirkelma/Desktop/local_git_repos\workflow_automation/output/'
    filename = f'voxels'
    
    geo_comm = GeoVal_Communicator(rve_dims=32, output_folder=folder, filename=filename,
                                   executable='bin/geo_val.exe')
    for i in range(2):
        geo_comm.introduce_objects(N=15)
        geo_comm.distribute()   
    geo_comm.set_volume_fraction(phase_volume_dict={1: 20, 7: 20}, 
                                  iterations=5, distribute_after=True)
    geo_comm.iterative_delete_small_regions()
    geo_comm.store_voxels()
    geo_comm.store_objects()
    geo_comm.end_communication()
    geo_comm.view_voxels()
    
    vc = VoxSM_Communicator(executable='bin/VoxSM_2017_x64.exe')
    vc.open_voxel_file(folder + filename + '.val')
    vc.split_regions()
    vc.generate_mesh()
    vc.adaptive_smooth()
    vc.simplify({'runs': 5})
    vc.store_mesh()
    vc.store_ansys()
    vc.close()
    
    # with fileinput.FileInput(filename + '.tmpSurf.node', inplace=True) as file:
    #     for line in file:
    #         print(line.replace(',', '.'), end='')
        
    # create some microstructures in a loop
    # for j in range(1,10):       
    #     filename = f'voxels{j}'
    #     geo_comm = GeoVal_Communicator(rve_dims=32, filename=filename)
    #     for i in range(2):
    #         geo_comm.introduce_objects(N=15)
    #     geo_comm.set_volume_fraction(phase_volume_dict={1: 10 * j, 7: 10 * (10-j)}, 
    #                                   iterations=5, distribute_beforehand=True)
        
    #     geo_comm.store_voxels()
    #     geo_comm.store_objects()
    #     geo_comm.end_communication()
    #     geo_comm.close()
        
    #     voxsm_exe = 'U:/workflow_automation/VoxSM_Quellcode/VoxSM_2017_x64.exe'
    #     voxsm_exe = glob.glob(voxsm_exe)
    #     vc = VoxSM_Communicator(voxsm_exe[0])
        
    #     vc.open_voxel_file('U:\workflow_automation\\' + filename + '.val')
    #     vc.split_regions()
    #     vc.generate_mesh()
    #     vc.store_mesh()
    #     vc.close()
        
    #     # fix comma issue in node file
    #     with fileinput.FileInput(filename + '.tmpSurf.node', inplace=True) as file:
    #         for line in file:
    #             print(line.replace(',', '.'), end='')
        
    
    #geo_comm.view_voxels()
    
    print("done!")