# -*- coding: utf-8 -*-
"""
 Unittests for workflow automation pipeline
"""
import pytest
import sys
from pathlib import Path
sys.path.append("../")   # this adds the mother folder  
                         # "my_python_scripts_folder/" to the python path 
                         # It will allow you to import your modules.
                         # Adjust depending where your tests scripts location
                         
                         
from MPaut import geoval_subprocess
from MPaut import voxsm_subprocess
from MPaut import ansys_subprocess
from MPaut import ansys_converter
from MPaut import ansys_simulations

GEOVAL_EXECUTABLE = '../bin/geo_val_parallel.exe'
VOXSM_EXECUTABLE = '../bin/VoxSM_2017_x64.exe'

@pytest.fixture
def mapdl_tmpdir(tmpdir):
    # helper fixture for launching pyansys mapdl with a temporary directory as workdir
    workdir = tmpdir / 'ansys_workdir'
    mapdl = ansys_subprocess.Ansys_Communicator(workdir)
    yield (mapdl, tmpdir)
    mapdl.exit()
    

def prepare_mesh_db(mapdl, tmpdir, element_types={}):
    """Generate RVE, run meshing and create database for further simulations in Ansys
    

    Parameters
    ----------
    mapdl : Ansys_Communicator
        Instance for pyansys simulations.
    tmpdir : 
        Root temporary directory where files (voxel files, mesh files, 
        converted pyansys scripts, Ansys database) will be placed

    Returns
    -------
    db_path : Path
        Path to the generated database file with the definition of the mesh
    """
    # 1. create RVE
    filename = 'testfile'
    tmpdir = Path(tmpdir)
    voxel_path = tmpdir / 'geoval' / (filename + '.val')
    object_path = tmpdir / 'geoval'  / (filename + '.obj')
    screenshot_path = tmpdir / 'geoval' / (filename + '.jpg')
    
    geo_comm = geoval_subprocess.GeoVal_Communicator(executable=GEOVAL_EXECUTABLE, 
                                                     output_folder=tmpdir / 'geoval')
    geo_comm.initialize_rve(rve_dims=32)
    geo_comm.introduce_objects(N=15, shape_description={'radius': 7e-6})
    geo_comm.distribute()
    geo_comm.store_voxels(voxel_path.name)
    geo_comm.store_objects(object_path.name)
    geo_comm.view_voxels(screenshot_file=screenshot_path.name)
    geo_comm.close()

    # make sure first step succeeds
    assert voxel_path.exists(), ".val file was not created"
    assert object_path.exists(), ".obj file was not created"
    assert screenshot_path.exists(), ".jpg was not created"
    
    # 2. create mesh
    # launch VoxSM process
    voxsm_comm = voxsm_subprocess.VoxSM_Communicator(executable=VOXSM_EXECUTABLE)
    voxsm_comm.open_voxel_file(voxel_path)    
    voxsm_comm.split_regions()
    voxsm_comm.generate_mesh()
    voxsm_comm.adaptive_smooth()
    voxsm_comm.simplify({'runs': 5})
    
    voxsm_comm.store_mesh(call_tetview=True)
    voxsm_comm.store_ansys(introduce_GB_prisms=False, element_types=element_types)
    voxsm_comm.close()
    
    expected_files = ["_main.win", "1_nodes.win", "2_SHELL_GB_RVE.win", "3_CMs_mesh.win"]
    for f in expected_files:    
        assert (tmpdir / 'geoval' / f).exists(), f"Ansys output file {f} was not created"
    
    # 3. create module for Ansys simulation
    package_output_dir = tmpdir / 'package_output_dir'
    package_name = 'mypackage'
    sc = ansys_converter.APDL_Script_Converter(package_output_dir)
    ansys_script = tmpdir / 'geoval' / '_main.win'
     # convert script to package
    created_main_script = sc.convert_script(ansys_script, package_name)
    
    assert (package_output_dir / package_name).exists()
    assert (package_output_dir / package_name / 'script__main.py').exists()
    
    # run the main module of the package
    mapdl.run_module(package_output_dir / package_name, created_main_script.name)
    
    db_path = mapdl.ansys_workdir / (filename + '.db')
    assert db_path.exists()
    
    return db_path
    

def test_single_elc_sim(mapdl_tmpdir):
    mapdl, tmpdir = mapdl_tmpdir
    db_path = prepare_mesh_db(mapdl, tmpdir)
    
    # 4. run elasticity simulation in Ansys
    sim = ansys_simulations.Simulator(mapdl)
    
    # define material properties for different phases
    phase_mat_params = { 'WC': {'phase_number': 1, 'emod': 650, 
                                'pois': 0.22},
                          'Co': {'phase_number': 10000, 'emod': 210, 
                                 'pois': 0.31},
                          }
        
    options = {'solver_tolerance': 1e-02}
    sim.simulate_elcs(db_path.name, phase_mat_params, options=options)
    mapdl.exit()
    
    result_file = mapdl.ansys_workdir / 'out_elc.out'
    assert result_file.exists()
    
def test_single_wlf_sim(mapdl_tmpdir):
    mapdl, tmpdir = mapdl_tmpdir
    
    db_path = prepare_mesh_db(mapdl, tmpdir, element_types={1: 'solid70'})
    
    # 4. run elasticity simulation in Ansys
    sim = ansys_simulations.Simulator(mapdl)
    
    # define material properties for different phases
    phase_mat_params = { 'SiC': {'phase_number': 1, 'therm_cond': 185},
                        'Si': {'phase_number': 10000, 'therm_cond': 75} }
        
    options = {'solver_tolerance': 1e-02}
    sim.simulate_therm_cond(db_path.name, phase_mat_params, options=options)
    mapdl.exit()
    
    result_file_1 = mapdl.ansys_workdir / 'out_wlf.out'
    result_file_2 = mapdl.ansys_workdir / 'out_Fsum.txt'
    assert result_file_1.exists()
    assert result_file_2.exists()