# -*- coding: utf-8 -*-
from ansys.mapdl import core as pymapdl
from MPaut import ansys_subprocess, ansys_simulations
from pathlib import Path

import pprint
import os

def sim_elcs_zta_rves(data_path, mapdl):
    """Simulate elastic properties for ZTA ceramics.
    
    The function will first load the mesh data from the VoxSM output files 
    under the given path and create a mesh database.
    Then, it will run a simulation for each RVE to determine the elastic
    properties of the RVE.
    
    Parameters
    ----------
    data_path : pathlib.Path
        Path to the output folders of the automated RVE generation.

    """    
    mesh_gen = ansys_subprocess.AnsysMeshGenerator(mapdl)
    sim = ansys_simulations.ELCsSimulator(mapdl)
    
    # set properties for simulation
    phase_mat_params = { 'ZrO2': {'phase_number': 4, 'emod': 200, 'pois': 0.31},
                        'Al2O3': {'phase_number': 10, 'emod': 380, 'pois': 0.23} }
    options={'solver_tolerance': 0.01}
    
    res_total = {}
    
    for root, dirs, files in os.walk(data_path):
        if '_main.win' in files:
            # prepare mesh database
            mesh_options = {'db_filename': f'{Path(root).stem}_mesh.db'}
            mesh_info = mesh_gen.create_mesh_from_VoxSM_output(root, mesh_options)
            
            # run the simulation
            res = sim.simulate(mesh_options['db_filename'], phase_mat_params, 
                         options=options)
            
            # store result of the simulation in a dictionary
            vol_frac = f"ZrO2: {res['v_phase'][4]}, Al2O3: {res['v_phase'][10]}"
            res['data_folder'] = str(Path(root))
            res_total[vol_frac] = res
            
    return res_total

mapdl = pymapdl.launch_mapdl(additional_switches="-smp")


outpath = 'output/zta_20'
res = sim_elcs_zta_rves(outpath, mapdl)

with open("results_elasticity.txt", 'w') as f:
    f.write(pprint.pformat(res))

mapdl.exit()
