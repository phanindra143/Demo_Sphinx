# -*- coding: utf-8 -*-
"""
 Unittests for workflow automation pipeline
"""
import pytest
import sys
import shutil
import pathlib
sys.path.append("../src/")   # this adds the mother folder  
                         # "my_python_scripts_folder/" to the python path 
                         # It will allow you to import your modules.
                         # Adjust depending where your tests scripts location

from MPaut import voxsm_subprocess

def test_communicator_creation():
    voxsm_comm = voxsm_subprocess.VoxSM_Communicator(executable='../bin/VoxSM_2017_x64.exe')
    voxsm_comm.close()
    
def test_communicator_creation_fail():
    with pytest.raises(FileNotFoundError):
        voxsm_comm = voxsm_subprocess.VoxSM_Communicator(executable='no_such_file.exe')

@pytest.fixture
def voxsm_comm():
    voxsm_comm = voxsm_subprocess.VoxSM_Communicator(executable='../bin/VoxSM_2017_x64.exe')
    yield voxsm_comm
    voxsm_comm.close()
        
def test_switch_tabs(voxsm_comm):    
    # switch through tabs and check if expected texts are visible
    voxsm_comm._select_tab(1)
    assert ['[ Edge-Heap & Simplify Tests ]'] in [d.texts() for d in voxsm_comm.toplevel_dlg.descendants()]
    
    voxsm_comm._select_tab(2)
    assert ['*.smesh & Tetview:'] in [d.texts() for d in voxsm_comm.toplevel_dlg.descendants()]
    
    voxsm_comm._select_tab(3)
    assert ['> ANSYS  (header):'] in [d.texts() for d in voxsm_comm.toplevel_dlg.descendants()]
    
    voxsm_comm._select_tab(0)
    assert ['  >> scan Grid  (generate SMesh by MT*)'] in [d.texts() for d in voxsm_comm.toplevel_dlg.descendants()]
    
def test_print_particles_materials(voxsm_comm):
    voxsm_comm.print_particles()
    voxsm_comm.print_materials()
    
def test_load_voxel_file_fail(voxsm_comm):
    with pytest.raises(FileNotFoundError):
        voxsm_comm.open_voxel_file('resources/no_such_file.val')
    
def test_load_voxel_file(voxsm_comm):
    output = voxsm_comm.open_voxel_file('resources/voxels.val')
    assert '> load  VOX ...done' in output
    
def test_split_regions(voxsm_comm):
    voxsm_comm.open_voxel_file('resources/voxels.val')
    output = voxsm_comm.split_regions()
    assert '> split VOX::regions ...done' in output
    
def test_generate_mesh(voxsm_comm):
    voxsm_comm.open_voxel_file('resources/voxels.val')
    output = voxsm_comm.generate_mesh()
    assert '> scan Grid ...done' in output
    assert ' cases: 0x132462  1x53160  2x24634  3x5324  4x42  ' in output
    assert ' adjust_Edges: True, fair_RVE-B.: True' in output
    
def test_generate_and_store_mesh(tmpdir, voxsm_comm):
    # copy voxel file to temporary folder
    shutil.copy('resources/voxels.val', tmpdir)
    test_input = pathlib.Path(tmpdir, 'voxels.val')
    
    expected_files =['voxels.tmpSurf.node', 'voxels.tmpSurf.smesh']
    
    voxsm_comm.open_voxel_file(test_input)
    voxsm_comm.split_regions()
    voxsm_comm.generate_mesh()
    voxsm_comm.store_mesh()
    
    # check if files have been successfully created
    for f in expected_files:
        path = pathlib.Path(tmpdir, f)
        assert path.exists()
        
def test_smooth(tmpdir, voxsm_comm):
    voxsm_comm.open_voxel_file('resources/voxels.val')
    voxsm_comm.split_regions()
    voxsm_comm.generate_mesh()
    
    # type checks for arguments
    with pytest.raises(ValueError):
        voxsm_comm.smooth(k_BP=0.0)
    with pytest.raises(ValueError):    
        voxsm_comm.smooth(k_BP=1.0)
    with pytest.raises(ValueError):    
        voxsm_comm.smooth(iterations=0)
    with pytest.raises(ValueError):    
        voxsm_comm.smooth(iterations=-1)
    with pytest.raises(ValueError):    
        voxsm_comm.smooth(fix_vs_nn=0.0)
    with pytest.raises(ValueError):    
        voxsm_comm.smooth(lambd=0.0)
    with pytest.raises(ValueError):    
        voxsm_comm.smooth(lambd='0.0')
    with pytest.raises(TypeError):    
        voxsm_comm.smooth(lambd=object())
    with pytest.raises(ValueError):
        voxsm_comm.smooth(mode='no_such_mode')
    
    # smooth with default options
    voxsm_comm.smooth(iterations=1)
    
    # smooth with different modes
    voxsm_comm.smooth(iterations=1, mode='all')
    voxsm_comm.smooth(iterations=1, mode='edges')
    voxsm_comm.smooth(iterations=1, mode='faces')
            
def test_get_Fs_statistics(voxsm_comm):
    voxsm_comm.open_voxel_file('resources/voxels.val')
    voxsm_comm.split_regions()
    voxsm_comm.generate_mesh()
    output = voxsm_comm._get_Fs_statistics()
    assert output == {'fQ_min': 0.247656, 'fQ_max': 0.453634, 'eL_min': 1.67e-07, 'eL_max': 1.41e-06, 'fA_min': 2.08e-14, 'fA_max': 5e-13}
    
def test_adaptive_smooth(voxsm_comm):
    voxsm_comm.open_voxel_file('resources/voxels.val')
    voxsm_comm.split_regions()
    voxsm_comm.generate_mesh()
    
    # invalid parameter should raise exception
    with pytest.raises(ValueError):    
        voxsm_comm.adaptive_smooth(eL_min_factor=0.0)
        
    voxsm_comm.adaptive_smooth()
    
@pytest.mark.timeout(60)
def test_too_much_output(voxsm_comm):
    # too much output in the left panel of VoxSM used to cause problems because
    # only part of the output is returned by pywinauto and thus parsing the
    # output for new data could fail
    # this test is to make sure this does not happen again
    voxsm_comm.open_voxel_file('resources/voxels.val')
    voxsm_comm.split_regions()
    voxsm_comm.generate_mesh()
    
    # do 3 dummy simplify runs to create enough output for the problem to occur
    voxsm_comm.simplify({'runs': 0})
    voxsm_comm.simplify({'runs': 0})
    voxsm_comm.simplify({'runs': 0})
    
        
def test_simplify(voxsm_comm):
    voxsm_comm.open_voxel_file('resources/voxels.val')
    voxsm_comm.split_regions()
    voxsm_comm.generate_mesh()
    
    with pytest.raises(ValueError):
        voxsm_comm.simplify({'invalid_option': None})
    
    # test dummy simplification (runs = 0)
    info = voxsm_comm.simplify({'runs': 0})
    
    # test some checkboxes
    voxsm_comm.simplify({'runs': 0, 
                         'r3-only': True,
                        'r2-only': True,
                        'bad-Fs-only': True,
                        'high-cost-first': True,
                        'fix-corners': True,
                        'focal-point-r2': True,
                        'focal-point-r3': True})
    
    # test single run of the simplification with default options
    voxsm_comm.simplify({'runs': 1})
    
def test_generate_and_store_ansys(tmpdir, voxsm_comm):
    # copy voxel file to temporary folder
    shutil.copy('resources/voxels.val', tmpdir)
    test_input = pathlib.Path(tmpdir, 'voxels.val')
    
    expected_files =['_main.win', '1_nodes.win', '2_GB_Prisms.win', 
                      '3_SHELL_GB_RVE.win', '4_CMs_mesh.win']
    
    voxsm_comm.open_voxel_file(test_input)
    voxsm_comm.split_regions()
    voxsm_comm.generate_mesh()
    voxsm_comm.store_ansys()
    
    # check if files have been successfully created
    for f in expected_files:
        path = pathlib.Path(tmpdir, f)
        assert path.exists()
        
def test_generate_and_store_ansys_no_gb(tmpdir, voxsm_comm):
    # copy voxel file to temporary folder
    shutil.copy('resources/voxels.val', tmpdir)
    test_input = pathlib.Path(tmpdir, 'voxels.val')
    
    expected_files =['_main.win', '1_nodes.win', '2_SHELL_GB_RVE.win', 
                     '3_CMs_mesh.win']
    
    voxsm_comm.open_voxel_file(test_input)
    voxsm_comm.split_regions()
    voxsm_comm.generate_mesh()
    voxsm_comm.store_ansys(introduce_GB_prisms=False)
    
    # check if files have been successfully created
    for f in expected_files:
        path = pathlib.Path(tmpdir, f)
        assert path.exists()
