# -*- coding: utf-8 -*-
"""
 Unittests for workflow automation pipeline
"""
import pytest
import sys
import pathlib
import numpy as np
import time
import re

sys.path.append("../src")   # this adds the mother folder  
                         # "my_python_scripts_folder/" to the python path 
                         # It will allow you to import your modules.
                         # Adjust depending where your tests scripts location
                         
from MPaut import ansys_simulations
from MPaut import ansys_subprocess 

    
def compare_results_elc(out_elcs_orig, res_new):    
    # compare data in original and new output
    
    # read values from original output file
    dat = np.genfromtxt(out_elcs_orig, comments='/%', skip_footer=1)
    # skip every second entry because it contains nan (description string 
    # converted to float)
    dat_orig = dat[1::2]
    
    fs_orig = dat_orig[0::2,:]
    es_orig = dat_orig[1::2,:]
    v_phase_orig = np.genfromtxt(out_elcs_orig, comments='/%', skip_header=48)
    
    print("fs_orig = ", fs_orig)
    print("es_orig = ", es_orig)
    print("v_phase_orig = ", v_phase_orig)
    
    assert(len(fs_orig) == len(res_new['sigma']))
    assert(len(es_orig) == len(res_new['epsilon']))
    assert(len(v_phase_orig) <= len(res_new['v_phase']))

    # generated elasticity parameters should match up to some precision    
    for record, data_orig in [('epsilon', es_orig), ('sigma', fs_orig)]:
        for i, row in enumerate(res_new[record]):
            for j, comp in enumerate(['xx', 'yy', 'zz', 'xy', 'xz', 'yz'], 1):
                diff = abs(data_orig[i,j] - res_new[record][row][comp])
                assert diff < 1e-2, f"result for {record} did not match at row {row}, component {comp}\n"\
                                    f" data_orig[{i},{j}] = {data_orig[i,j]}\n"\
                                    f" res_new[{record}][{row}][{comp}] = {res_new[record][row][comp]}"
                                    
     
    for i, phase in enumerate(res_new['v_phase'].items()):
        if i < len(v_phase_orig):
            diff = abs(phase[1] - v_phase_orig[i])
            assert diff < 1e-2, "phase volume fraction for phase {phase[0]} did not match original phase volume fraction"


def compare_results_wlf(out_wlf_orig, out_Fsum_orig, res_new):
    with open(out_Fsum_orig) as f:
        fsum_dat = f.read()
    reg = r"WLF\(dir = (?P<axis>.)\): (?P<value>[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)"
    wlfs = re.findall(reg, fsum_dat)
    
    for axis, value, _ in wlfs:
        diff = abs(res_new[axis]['thermal_cond'] - float(value))
        assert diff < 1e-2, f"thermal conductivity {res_new[axis]['thermal_cond']} in axis {axis} does not match original value {value}"
        
    reg = r"-> WLF\(mean-ifx\) = (?P<value>[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)"
    mean = re.search(reg, fsum_dat)
    
    diff = float(mean['value']) - res_new['mean']
    assert diff < 1e-2
     
    # compare data in original and new output
    dat = np.genfromtxt(out_wlf_orig, comments='/%')
    # skip every second entry because it contains nan (description string 
    # converted to float)
    dat_orig = dat[1::2,1:]
    
    print("orig = ", dat_orig)
    print("new = ", res_new)
    
    assert set(res_new.keys()) == {'x', 'y', 'z', 'mean', 'v_phase'}
    for ax in ['x', 'y', 'z']:
        assert set(res_new[ax].keys()) == {'qs', 'dts', 'thermal_cond'}
        assert set(res_new[ax]['qs'].keys()) == {'x', 'y', 'z'}
        assert set(res_new[ax]['dts'].keys()) == {'x', 'y', 'z'}
    
    dat_new = np.zeros(dat_orig.shape)
    for i, ax in enumerate(['x', 'y', 'z']):
        for j, direct in enumerate(['x', 'y', 'z']):
            dat_new[2*i, j] = res_new[ax]['qs'][direct]
            dat_new[2*i+1, j] = res_new[ax]['dts'][direct]

    assert np.allclose(dat_orig, dat_new, atol=1e-2, rtol=5e-2), "contents of output arrays does not match up to given tolerance"
       

def test_mock_elcs_single_WC_Co(mock_mapdl):
    resource_root = pathlib.Path('resources') / 'sim_elcs_WC_Co_single'
    
    # generate database with mesh
    mesh_gen = ansys_subprocess.AnsysMeshGenerator(mock_mapdl)
    mesh_gen.create_mesh_from_VoxSM_output(resource_root)
          
    # mock run for simulation of elasicity
    sim = ansys_simulations.ELCsSimulator(mock_mapdl)
    sim.db_checks = False
    
    phase_mat_params = { 'WC': {'phase_number': 1, 'emod': 650, 'pois': 0.22},
                          'Co': {'phase_number': 2, 'emod': 210, 'pois': 0.31} }
    options={'boundary_nodes_selection_tolerance': 0.01}
    
    sim.simulate('dummy.db', phase_mat_params, options=options)
  

def test_sim_elcs_single_WC_Co(mapdl):
    resource_root = pathlib.Path('resources') / 'sim_elcs_WC_Co_single'
        
    # generate database with mesh
    mesh_options = {'db_filename': 'mesh.db'}
    mesh_gen = ansys_subprocess.AnsysMeshGenerator(mapdl)
    #mesh_gen.create_mesh_from_VoxSM_output(resource_root, mesh_options)
    
    sim = ansys_simulations.ELCsSimulator(mapdl)
    
    phase_mat_params = { 'WC': {'phase_number': 1, 'emod': 650, 'pois': 0.22},
                          'Co': {'phase_number': 2, 'emod': 210, 'pois': 0.31} }
    options = {'boundary_nodes_selection_tolerance': 0.01}
    
    res = sim.simulate(mesh_options['db_filename'], phase_mat_params, options=options)
    compare_results_elc(resource_root / 'out_elc.out', res)

def test_sim_elcs_all_WC_Co(mapdl, scripts_dir):
    resource_root = pathlib.Path(scripts_dir)
    assert resource_root.exists(), f"resource file root for test not found at {resource_root.absolute()}"
    val_file = next(resource_root.glob('*.val'))
    assert val_file.exists()
        
    db_filename = 'mesh.db'
    # generate database with mesh
    mesh_options = {'db_filename': db_filename}
    mesh_gen = ansys_subprocess.AnsysMeshGenerator(mapdl)
    mesh_gen.create_mesh_from_VoxSM_output(resource_root, mesh_options)
    
    sim = ansys_simulations.ELCsSimulator(mapdl)
    
    assert db_filename in mapdl.list_files(), f"database file with mesh not found in ansys working directory {mapdl.directory}"
    
    # define material properties for different phases (distinguish different 
    # phase numbers for prism or sphere objects)
    if 'prism' in str(scripts_dir):
        if '2019' in str(scripts_dir): 
            # for some reason newer simulations use different emod for WC
            phase_mat_params = { 'WC': {'phase_number': 3, 'emod': 680, 
                                        'pois': 0.22},
                                  'Co': {'phase_number': 2, 'emod': 210, 
                                         'pois': 0.31},
                                  }
        else:
            phase_mat_params = { 'WC': {'phase_number': 3, 'emod': 650, 
                                        'pois': 0.22},
                                  'Co': {'phase_number': 2, 'emod': 210, 
                                         'pois': 0.31},
                                  'Pore': {'phase_number': 10000, 
                                           'emod': 1e-4 * 1e-9, 'pois': 1e-4}
                                  }
    else:
        phase_mat_params = { 'WC': {'phase_number': 1, 'emod': 650, 
                                    'pois': 0.22},
                              'Co': {'phase_number': 2, 'emod': 210, 
                                     'pois': 0.31},
                              'Pore': {'phase_number': 10000, 
                                       'emod': 1e-4 * 1e-9, 'pois': 1e-4}
                              }
        
    options = {}
    options['solver_tolerance'] = 1e-08
    if any(s in str(scripts_dir) for s in ['2016-04-14', 
                                         '2016-04-12_100part_volf80_sint']): 
        # in these tests a different tolerance for boundary node selection 
        # was used
        options['boundary_nodes_selection_tolerance'] = 0.01
        
    res = sim.simulate(db_filename, phase_mat_params, options=options)
        
    compare_results_elc(resource_root / 'out_elc.out', res)

    
def test_mock_wlf_all_SicSi(mock_mapdl, scripts_dir):
    resource_root = pathlib.Path(scripts_dir)

    # generate database with mesh
    mesh_gen = ansys_subprocess.AnsysMeshGenerator(mock_mapdl)
    mesh_info = mesh_gen.create_mesh_from_VoxSM_output(resource_root)
       
    # dummy simulation run for elasicity
    sim = ansys_simulations.ThermalConductivitySimulator(mock_mapdl)
    sim.db_checks = False
    
    # define material properties for different phases
    phase_mat_params = { 'SiC': {'phase_number': 3, 'therm_cond': 185},
                        'Si': {'phase_number': 2, 'therm_cond': 75},
                        'Pore': {'phase_number': 10000, 'therm_cond': 0.0262}
                        }
        
    options = {}
    options['solver_tolerance'] = 1e-08
    options['boundary_nodes_selection_tolerance'] = 0.01
    
    sim.simulate('dummy.db', phase_mat_params, options=options)
    
def test_sim_wlf_all_SicSi(tmpdir, mapdl, scripts_dir):
    resource_root = pathlib.Path(scripts_dir)
    assert resource_root.exists(), f"resource file root for test not found at {resource_root.absolute()}"
    val_file = next(resource_root.glob('*.val'))
    assert val_file.exists()
        
    db_filename = 'mesh.db'
    # generate database with mesh
    mesh_options = {'db_filename': db_filename}
    mesh_gen = ansys_subprocess.AnsysMeshGenerator(mapdl)
    mesh_info = mesh_gen.create_mesh_from_VoxSM_output(resource_root, mesh_options)
    
    sim = ansys_simulations.ThermalConductivitySimulator(mapdl)
    
    assert db_filename in mapdl.list_files(), f"database file with mesh not found in ansys working directory {mapdl.directory}"

    
    # define material properties for different phases
    phase_mat_params = { 'SiC': {'phase_number': 3, 'therm_cond': 185},
                        'Si': {'phase_number': 2, 'therm_cond': 75},
                        'Pore': {'phase_number': 10000, 'therm_cond': 0.0262}}
        
    options = {}
    options['solver_tolerance'] = 1e-08
    options['boundary_nodes_selection_tolerance'] = 0.01

    res = sim.simulate(db_filename, phase_mat_params, options=options)
    
    compare_results_wlf(resource_root / 'out_wlf.out', resource_root / 'out_Fsum.txt' , res)
    
# def test_sim_elcs_all_CMC_Sic(mapdl_tmpdir, elc_sims_CMC_Sic):
#     mapdl, tmpdir = mapdl_tmpdir
#     resource_root = pathlib.Path(elc_sims_CMC_Sic)
#     assert resource_root.exists()
#     val_file = next(resource_root.glob('*.val'))
#     assert val_file.exists(), f"resource file root for test not found at {resource_root.absolute()}"
            
#     # convert scripts in the resource root and run them to create mesh db file for simulations
#     create_mesh_db_file(mapdl, tmpdir, resource_root)
    
#     sim = ansys_simulations.Simulator(mapdl)

#     # find db name based on name of .val file
#     db_file = val_file.stem  
#     db_path = pathlib.Path(mapdl.ansys_workdir / (db_file + '.db')) 
#     assert db_path.exists(), f"database file with mesh not found at {db_path.absolute()}"
    
#     phase_mat_params = { 'SiC': {'phase_number': 3, 'emod': 475, 'pois': 0.17},
#                         'Si': {'phase_number': 2, 'emod': 160, 'pois': 0.22},
#                         'Pore': {'phase_number': 10000, 'emod': 1e-4 * 1e-9, 'pois': 0.2}
#                               }
#     sim.simulate_elcs(db_path.name, phase_mat_params, options={})
    
#     compare_results_elc(resource_root / 'out_elc.out', 
#                         mapdl.ansys_workdir / 'out_elc.out')


def test_mock_cte_WC_Co(mock_mapdl):
    resource_root = pathlib.Path('resources') / 'sim_cte_WC_Co' / '2019-09-04_150prism_vol75'
    
    # generate database with mesh
    mesh_gen = ansys_subprocess.AnsysMeshGenerator(mock_mapdl)
    mesh_gen.create_mesh_from_VoxSM_output(resource_root)

    # test simulator for coefficient of thermal expansion
    sim = ansys_simulations.ThermalStressSimulator(mock_mapdl)
    sim.db_checks = False
    
    # define material properties for different phases
    phase_mat_params = { 'WC': {'phase_number': 3, 'emod': 680, 'pois': 0.22, 'cte': 6.0},
                        'Co': {'phase_number': 2, 'emod': 210, 'pois': 0.31, 'cte': 13.0} }
    
    
    options = {'t_raum': 25,
               't_solid': 800}
    
    sim.simulate('mydb.db', params=phase_mat_params, options=options)
    
    
def test_sim_cte_WC_Co(tmpdir, mapdl):
    resource_root = pathlib.Path('resources') / 'sim_cte_WC_Co' / '2019-09-04_150prism_vol75'
        
    # generate database with mesh
    mesh_gen = ansys_subprocess.AnsysMeshGenerator(mapdl)
    mesh_gen.create_mesh_from_VoxSM_output(resource_root)
    
    sim = ansys_simulations.ThermalStressSimulator(mapdl)
    
    # find db name based on name of .val file
    db_file = 'RVE#1.db'
    db_path = pathlib.Path(mapdl.ansys_workdir / db_file) 
    assert db_path.exists(), f"database file with mesh not found at {db_path.absolute()}"
    
    # define material properties for different phases
    phase_mat_params = { 'WC': {'phase_number': 3, 'emod': 680, 'pois': 0.22, 'cte': 6.0},
                        'Co': {'phase_number': 2, 'emod': 210, 'pois': 0.31, 'cte': 13.0}}
    
    options = {'t_raum': 25,
               't_solid': 800,
               'solver_tolerance': 1e-3}
    
    sim.simulate(db_file, params=phase_mat_params, options=options)
        
def test_sim_prepare_output_file(mapdl):
    sim = ansys_simulations.Simulator(mapdl)
    
    outpath = mapdl.ansys_workdir / 'testfile.out'
    outpath.write_text('some text')
    
    # make sure we override existing file
    sim._prepare_output_file('testfile.out')
    assert len(outpath.read_text()) == 0, "output file was not overwritten"
    
def test_check_db_not_existing_error(mapdl):
    sim = ansys_simulations.Simulator(mapdl)
    
    # try running simulation with database with wrong file extension
    with pytest.raises(ValueError):
        sim._check_db_file('no_such_file.txt')
    
    # try running simulation with nonexisting db file
    with pytest.raises(FileNotFoundError):
        sim._check_db_file('no_such_file.db')
    
def test_check_db_sanity(mapdl):
    sim = ansys_simulations.Simulator(mapdl)
    
    # try running simulation with database that does not contain definition of 
    # RVE size
    mapdl.mapdl.save('test_no_L.db')   # create empty database
    with pytest.raises(ValueError):
        sim.mapdl.finish()
        sim.mapdl.run("/clear")
        sim.mapdl.run("/filname,ELCs")
        sim.mapdl.run("/PREP7")
        sim.mapdl.resume('test_no_L', "db")
        sim._check_db_sanity()
        
    # try running simulation with database that does not contain nodes
    mapdl.mapdl.run("L = 1")
    mapdl.mapdl.save('test_no_nodes.db')   # create database with L 
    with pytest.raises(ValueError):
        sim.mapdl.finish()
        sim.mapdl.run("/clear")
        sim.mapdl.run("/filname,ELCs")
        sim.mapdl.run("/PREP7")
        sim.mapdl.resume('test_no_nodes', "db")
        sim._check_db_sanity()

        
    # try running simulation with database that does not contain elements
    mapdl.mapdl.run("n,1, 1.1073296766370722E-05, 0, 0")
    mapdl.mapdl.save('test_no_elems.db')   # create database with L, 1 node
    with pytest.raises(ValueError):
        sim.mapdl.finish()
        sim.mapdl.run("/clear")
        sim.mapdl.run("/filname,ELCs")
        sim.mapdl.run("/PREP7")
        sim.mapdl.resume('test_no_elems', "db")
        sim._check_db_sanity()
        
    # try running simulation with database that does contain nodes and elements
    mapdl.mapdl.run("et,3,SHELL157")
    mapdl.mapdl.run("n,2, 1.6846727256207832E-05, 0, 0")
    mapdl.mapdl.run("n,3, 1.2605808556652014E-05, 2.7879834999921612E-06, 0")
    mapdl.mapdl.run("esel,none")
    mapdl.mapdl.run("type,3")
    mapdl.mapdl.run("e, 1, 2, 3, 3") 
    mapdl.mapdl.save('test_elem_nodes.db')   # create database with L, 4 nodes, 1 elem
    sim.mapdl.resume('test_elem_nodes', "db")
    sim._check_db_sanity()
