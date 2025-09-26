# -*- coding: utf-8 -*-
"""
 Unittests for workflow automation pipeline
"""
import pytest
import sys
import pathlib
import time

sys.path.append("../src")   # this adds the mother folder  
                         # "my_python_scripts_folder/" to the python path 
                         # It will allow you to import your modules.
                         # Adjust depending where your tests scripts location
from MPaut import ansys_subprocess
        
def test_mock_run_mesh_creation(mock_mapdl, scripts_dir):
    # mock test of mesh creation (does not actually perform calls to PyMAPDL)
    # but just tests general functionality of file parsing logic
    mapdl = mock_mapdl
    mesh_gen = ansys_subprocess.AnsysMeshGenerator(mapdl)
     
    ansys_scripts = scripts_dir
    
    node_file = ansys_scripts / '1_nodes.win'
    elem_file = ansys_scripts / '2_SHELL_GB_RVE.win'
    comp_file = ansys_scripts / '3_CMs_mesh.win'
    
    element_types = {1: "solid187",
                     2: "SHELL157",
                     3: "SHELL157"}
    
    db_filename=str(int(time.time())) + '.db'

    res = mesh_gen.create_mesh_db(node_file, elem_file, comp_file, 
                            element_types=element_types, 
                            db_filename=db_filename)
    
def test_run_mesh_creation(mapdl, scripts_dir):   
    # mesh creation test which carries out calls to PyMAPDL
    mesh_gen = ansys_subprocess.AnsysMeshGenerator(mapdl)
     
    ansys_scripts = scripts_dir
    
    # run the main module of the package
    node_file = ansys_scripts / '1_nodes.win'
    elem_file = ansys_scripts / '2_SHELL_GB_RVE.win'
    comp_file = ansys_scripts / '3_CMs_mesh.win'
    
    element_types = {1: "solid187",
                     2: "SHELL157",
                     3: "SHELL157"}
    
    db_filename=str(int(time.time())) + '.db'

    mesh_gen.create_mesh_db(node_file, elem_file, comp_file, 
                            element_types=element_types, 
                            db_filename=db_filename)
    
    assert (db_filename + '.db') in mapdl.list_files()
    

@pytest.mark.parametrize("scripts_dir", ['ansys_input_files_1', 'ansys_input_files_2'])    
def test_run_mesh_creation_gb_prisms(mapdl, scripts_dir):           
    mesh_gen = ansys_subprocess.AnsysMeshGenerator(mapdl)
    
    ansys_scripts = pathlib.Path('resources') / scripts_dir
    
    node_file = ansys_scripts / '1_nodes.win'
    gb_prisms_file = ansys_scripts / '2_GB_Prisms.win'
    elem_file = ansys_scripts / '3_SHELL_GB_RVE.win'
    comp_file = ansys_scripts / '4_CMs_mesh.win'

    
    element_types = {1: "solid187",
                     2: "SHELL157",
                     3: "SHELL157",
                     6: "solid231"}
    
    db_filename=str(int(time.time())) + '.db'
    mesh_gen.create_mesh_db(node_file, elem_file, comp_file, gb_prisms_file, element_types, 
                            db_filename=db_filename)
    
    assert (db_filename + '.db') in mapdl.list_files()
    
@pytest.mark.parametrize("scripts_dir", ['ansys_input_files_1', 'ansys_input_files_2'])    
def test_mock_run_mesh_creation_gb_prisms(mock_mapdl, scripts_dir):
    mapdl = mock_mapdl
    mesh_gen = ansys_subprocess.AnsysMeshGenerator(mapdl)
    
    ansys_scripts = pathlib.Path('resources') / scripts_dir
    
    node_file = ansys_scripts / '1_nodes.win'
    gb_prisms_file = ansys_scripts / '2_GB_Prisms.win'
    elem_file = ansys_scripts / '3_SHELL_GB_RVE.win'
    comp_file = ansys_scripts / '4_CMs_mesh.win'

    
    element_types = {1: "solid187",
                     2: "SHELL157",
                     3: "SHELL157",
                     6: "solid231"}
    
    db_filename=str(int(time.time())) + '.db'
    mesh_gen.create_mesh_db(node_file, elem_file, comp_file, gb_prisms_file, element_types, 
                            db_filename=db_filename)

def test_mock_mesh_creation_VoxSM_failing(mock_mapdl):
    mapdl = mock_mapdl
    mesh_gen = ansys_subprocess.AnsysMeshGenerator(mapdl)
    
    with pytest.raises(FileNotFoundError):
        scripts_dir = pathlib.Path('resources', 'invalid_voxsm_input', 'no_such_folder')
        mesh_gen.create_mesh_from_VoxSM_output(scripts_dir)
    
    with pytest.raises(FileNotFoundError):
        scripts_dir = pathlib.Path('resources', 'invalid_voxsm_input', 'no_nodes')
        mesh_gen.create_mesh_from_VoxSM_output(scripts_dir)
        
    with pytest.raises(FileNotFoundError):
        scripts_dir = pathlib.Path('resources', 'invalid_voxsm_input', 'no_elements')
        mesh_gen.create_mesh_from_VoxSM_output(scripts_dir)
        
    with pytest.raises(FileNotFoundError):
        scripts_dir = pathlib.Path('resources', 'invalid_voxsm_input', 'no_components')
        mesh_gen.create_mesh_from_VoxSM_output(scripts_dir)
        
    with pytest.raises(RuntimeError):
        scripts_dir = pathlib.Path('resources', 'invalid_voxsm_input', 'no_length')
        mesh_gen.create_mesh_from_VoxSM_output(scripts_dir)
        
    with pytest.raises(RuntimeError):
        scripts_dir = pathlib.Path('resources', 'invalid_voxsm_input', 'no_element_types')
        mesh_gen.create_mesh_from_VoxSM_output(scripts_dir)
            
def test_mock_mesh_creation_VoxSM(mock_mapdl, scripts_dir):
    mapdl = mock_mapdl
    mesh_gen = ansys_subprocess.AnsysMeshGenerator(mapdl)
    mesh_gen.create_mesh_from_VoxSM_output(scripts_dir)
    
def test_mesh_creation_VoxSM(mapdl, scripts_dir):
    mesh_gen = ansys_subprocess.AnsysMeshGenerator(mapdl)
    db_filename = str(int(time.time())) + '.db'
    options = {'db_filename': db_filename}
    mesh_gen.create_mesh_from_VoxSM_output(scripts_dir, options)
    assert (db_filename + '.db') in mapdl.list_files()