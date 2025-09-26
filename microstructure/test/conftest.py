# -*- coding: utf-8 -*-
import pytest
import pathlib

from ansys.mapdl import core as pymapdl
from mock_mapdl import get_MockMAPDL

@pytest.fixture
def mock_mapdl():
    mapdl = get_MockMAPDL()
    yield mapdl
    
@pytest.fixture
def mapdl():
    mode = 'remote'
    if mode == 'local':
        # local MAPDL
        mapdl = pymapdl.launch_mapdl()
    elif mode == 'remote':
        # remote MAPDL
        mapdl = pymapdl.Mapdl(ip='localhost', port=50052, cleanup_on_exit=False,
                                   timeout=5, log_level='DEBUG')
    
    yield mapdl
    
    if mode == 'local':
        mapdl.exit()
        
                         
def pytest_generate_tests(metafunc):
    if metafunc.definition.name in ['test_mock_run_mesh_creation', 
                                    'test_run_mesh_creation', 
                                    'test_mock_mesh_creation_VoxSM', 
                                    'test_mesh_creation_VoxSM']:
        filelist = list(pathlib.Path('resources', 'sim_elcs_WC_Co').glob('*/**'))
        filelist.append(pathlib.Path('resources', 'sim_elcs_WC_Co_single'))
        filelist.append(pathlib.Path('resources', 'ansys_wak'))
        filelist.append(pathlib.Path('resources', 'ansys_sim_maco_1_run'))
        metafunc.parametrize("scripts_dir", filelist)    
    elif metafunc.definition.name == 'test_sim_elcs_all_WC_Co':
        filelist = list(pathlib.Path('resources', 'sim_elcs_WC_Co').glob('*/**'))
        metafunc.parametrize("scripts_dir", filelist)
    elif metafunc.definition.name in ['test_mock_wlf_all_SicSi',
                                      'test_sim_wlf_all_SicSi']:
        filelist = list(pathlib.Path('resources', 'sim_thermal_cond_SiC_Si',
                                     'Rein_ohne_Poren').glob('*/**'))
        filelist += list(pathlib.Path('resources', 'sim_thermal_cond_SiC_Si',
                                     'WLF-50SiC-Poren').glob('*/**'))
        metafunc.parametrize("scripts_dir", filelist)
    elif metafunc.definition.name in ['test_stiffness_computation']:
        elc_filelist = list(pathlib.Path('resources', 'crystal', 'elc').glob('*.out'))
        sgd_filelist = list(pathlib.Path('resources', 'crystal', 'elc').glob('*.sgd'))
        metafunc.parametrize("elc_data", zip(elc_filelist, sgd_filelist))
    elif metafunc.definition.name in ['test_thermal_conductivity_computation']:
        wlf_filelist = list(pathlib.Path('resources', 'crystal', 'wlf').glob('*.out'))
        sgd_filelist = list(pathlib.Path('resources', 'crystal', 'wlf').glob('*.sgd'))
        metafunc.parametrize("wlf_data", zip(wlf_filelist, sgd_filelist))
        