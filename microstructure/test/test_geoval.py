# -*- coding: utf-8 -*-
"""
 Unittests for workflow automation pipeline
"""
import pytest
import sys
import pathlib

sys.path.append("../src/")   # this adds the mother folder  
                         # "my_python_scripts_folder/" to the python path 
                         # It will allow you to import your modules.
                         # Adjust depending where your tests scripts location
from MPaut import geoval_subprocess


GEOVAL_EXECUTABLE = '../bin/geo_val_parallel.exe'

def test_communicator_creation():
    geo_comm = geoval_subprocess.GeoVal_Communicator(executable=GEOVAL_EXECUTABLE)
    geo_comm.close()
    
def test_debug_output(tmpdir):
    geo_comm = geoval_subprocess.GeoVal_Communicator(executable=GEOVAL_EXECUTABLE, 
                                   output_folder=tmpdir,
                                   debug_output=True)
    geo_comm.end_communication()
    geo_comm.close()
    
    debug_file = pathlib.Path(tmpdir, 'debug.pro')
    
    assert debug_file.exists()
    df = open(debug_file)
    debug_output = "".join(df.readlines())
    assert "quit" in debug_output
    
def test_no_debug_output(tmpdir):
    geo_comm = geoval_subprocess.GeoVal_Communicator(executable=GEOVAL_EXECUTABLE, 
                                   output_folder=tmpdir,
                                   debug_output=False)
    geo_comm.end_communication()
    geo_comm.close()
    
    debug_file = pathlib.Path(tmpdir, 'debug.pro')
    
    assert not debug_file.exists()
    
def test_communicator_creation_fail():
    with pytest.raises(FileNotFoundError):
        geo_comm = geoval_subprocess.GeoVal_Communicator(executable='no_such_file.exe')
        
def test_object_create_and_store(tmpdir):
    filename = 'testfile'
    voxel_path = pathlib.Path(tmpdir, filename + '.val')
    object_path = pathlib.Path(tmpdir, filename + '.obj')
    
    geo_comm = geoval_subprocess.GeoVal_Communicator(executable=GEOVAL_EXECUTABLE, output_folder=tmpdir)
    geo_comm.initialize_rve(rve_dims=32)
    geo_comm.introduce_objects(N=15)
    geo_comm.store_voxels(filename + '.val')
    geo_comm.store_objects(filename + '.obj')
    
    
    # check if files have been successfully created
    assert voxel_path.exists()
    assert object_path.exists()
    geo_comm.close()
        
# fixture to reduce code needed for starting GeoVal in following tests
@pytest.fixture()
def geo_comm():
    geo_comm = geoval_subprocess.GeoVal_Communicator(executable=GEOVAL_EXECUTABLE)
    yield geo_comm
    geo_comm.close()
    
# fixture to reduce code needed for starting GeoVal in following tests
@pytest.fixture()
def geo_comm_tmpdir(tmpdir):
    geo_comm = geoval_subprocess.GeoVal_Communicator(executable=GEOVAL_EXECUTABLE, output_folder=tmpdir)
    yield geo_comm, tmpdir
    geo_comm.close()

def test_rand_seed(geo_comm):
    geo_comm.set_randseed(42)
   
def test_init_rve(geo_comm):
    geo_comm.initialize_rve(rve_dims=32, voxel_size_um=1.0)
    
def test_object_introduce(geo_comm):
    geo_comm.introduce_objects(N=15)
    
    geo_comm.introduce_objects(N=10)
    
    geo_comm.introduce_objects(N=5)
    
    geo_comm.introduce_objects(N=2)
    
    with pytest.raises(ValueError):
        geo_comm.introduce_objects(N=5, object_type='invalid_object_type')
        
    for object_type in geo_comm.default_shape_descriptors.keys():
        with pytest.raises(ValueError):
            geo_comm.introduce_objects(N=5, object_type=object_type, 
                                       shape_description={'invalid shape descriptor': None})
    
    
def test_object_introduce_spheres(geo_comm):
    geo_comm.introduce_objects(N=5, object_type='sphere')
    geo_comm.introduce_objects(N=5, object_type='sphere', shape_description={'radius': 5e-6})
    
def test_object_introduce_prisms(geo_comm):
    geo_comm.introduce_objects(N=5, object_type='prism')
    geo_comm.introduce_objects(N=5, object_type='prism', shape_description={'edge_length': 4.0e-6, 
                                                                      'thickness': 2.0e-6, 
                                                                      'n_edges': 5})
    
  
def test_object_introduce_tubes(geo_comm):
    
    geo_comm.introduce_objects(N=5, object_type='tube')
    geo_comm.introduce_objects(N=5, object_type='tube', shape_description={'radius': 5.0e-6, 
                                                                      'length': 20.0e-6, 
                                                                      'inner_radius': 3.0e-6})
        
  
def test_object_introduce_voronoi(geo_comm):
    geo_comm.introduce_objects(N=5, object_type='voronoi_polyeder')
    geo_comm.introduce_objects(N=5, object_type='voronoi_polyeder', shape_description={'radius': 5.0e-6})

@pytest.mark.parametrize("n_faces", [4,6,8,12,20])
def test_object_introduce_platonic_solid(geo_comm, n_faces):
    geo_comm.introduce_objects(N=5, object_type='platonic_solid',
                               shape_description={'n_faces': n_faces})
       
def test_object_introduce_platonic_solid_invalid_faces(geo_comm):
    # test invalid number of faces
    with pytest.raises(ValueError):
        f = 7
        geo_comm.introduce_objects(N=5, object_type='platonic_solid', 
                                   shape_description={'n_faces': f})
 
def test_object_introduce_fibre(geo_comm):
    geo_comm.introduce_objects(N=5, object_type='fibre', 
                               shape_description={'radius': 10e-6,
                                                  'shell': 1e-6})
    
def test_object_introduce_random_distribution(geo_comm):
    # test if specifying gauss and log_normal distribution works without error
    geo_comm.introduce_objects(N=5, distribution='gauss')
    geo_comm.introduce_objects(N=5, distribution='log_normal')
    with pytest.raises(ValueError):
        geo_comm.introduce_objects(N=5, distribution='some_other_distribution')
    
def test_object_introduce_random_seed(geo_comm):
    # test if creating RVE with same random seed produces the same result
    geo_comm.introduce_objects(N=10, randseed=42)
    vol_fracs_1 = geo_comm.get_volume_fractions()
    
    # create new RVE with same random seed
    geo_comm.initialize_rve()   # reset RVE
    geo_comm.introduce_objects(N=10, randseed=42)
    vol_fracs_2 = geo_comm.get_volume_fractions()
    assert vol_fracs_1 == vol_fracs_2 # use volume fraction to check if RVE are identical (quick and dirty)
    
    # setting random seed manually should also work
    geo_comm.initialize_rve() # reset RVE
    geo_comm.set_randseed(42)
    geo_comm.introduce_objects(N=10)
    vol_fracs_3 = geo_comm.get_volume_fractions()
    assert vol_fracs_1 == vol_fracs_3
    
    # test if using not the same random seed gives a different RVE
    geo_comm.initialize_rve() # reset RVE
    geo_comm.introduce_objects(N=10)
    vol_fracs_4 = geo_comm.get_volume_fractions()
    assert vol_fracs_1 != vol_fracs_4

    
def test_object_introduce_cuts(geo_comm):
    # first create objects without cuts and save volume fractions
    geo_comm.introduce_objects(N=10, number_of_cuts=0, randseed=42)
    vol_fracs_no_cuts = geo_comm.get_volume_fractions()

    # now create objects with one cuts and make sure that volume fraction is
    # smaller
    geo_comm.initialize_rve() # reset RVE
    geo_comm.introduce_objects(N=10, number_of_cuts=1, randseed=42)
    vol_fracs_1_cut = geo_comm.get_volume_fractions()
    assert vol_fracs_1_cut[1] < vol_fracs_no_cuts[1]
    
    # now objects with two cuts and check that volume fraction is even smaller
    geo_comm.initialize_rve() # reset RVE
    geo_comm.introduce_objects(N=10, number_of_cuts=2, randseed=42)
    vol_fracs_2_cuts = geo_comm.get_volume_fractions()
    assert vol_fracs_2_cuts[1] < vol_fracs_1_cut[1]
    
    # make sure that Exception is raised for more than two cuts
    with pytest.raises(ValueError):
        geo_comm.introduce_objects(N=10, number_of_cuts=3)
  
def test_volume_analysis(geo_comm):
    geo_comm.introduce_objects(N=5,object_type='sphere')
    analysis = geo_comm.get_volume_fractions()
    assert {1} == set(analysis.keys())    # make sure we get a report for all phases
    assert all([vol > 0.0 for vol in analysis.values()])            # all volumes should be positive
    
    geo_comm.introduce_objects(N=5,object_type='tube')
    analysis = geo_comm.get_volume_fractions()
    assert {1, 2} == set(analysis.keys())    # make sure we get a report for all phases
    assert all([vol > 0.0 for vol in analysis.values()])            # all volumes should be positive
    
    geo_comm.introduce_objects(N=5, object_type='prism')
    analysis = geo_comm.get_volume_fractions()
    assert {1, 2, 3} == set(analysis.keys())    # make sure we get a report for all phases
    assert all([vol > 0.0 for vol in analysis.values()])            # all volumes should be positive
    
    
def test_object_analysis(geo_comm):
    # introduce objects of every type (except voronoi) and check if object
    # analysis reports the correct number of introduced objects and all
    # expected shape descriptors
    sphere_shape_descriptors =  {'radius', 'center_x', 'center_y', 'center_z', 
                                 'direction_x', 'direction_y', 'direction_z'}
    tube_shape_descriptors = {'radius', 'length', 'inner-radius',
                               'center_x', 'center_y', 'center_z', 
                               'direction_x', 'direction_y', 'direction_z'}
    prism_shape_descriptors = {'edge_length', 'thickness','#_edges_(<6)', 
                               'center_x', 'center_y', 'center_z', 
                               'direction_x', 'direction_y', 'direction_z',
                               'direction2_x', 'direction2_y', 'direction2_z'}
    platonic_solid_shape_descriptors = {'edge_length', 'variation','faces_4,6,8,12,20', 
                               'center_x', 'center_y', 'center_z', 
                               'direction_x', 'direction_y', 'direction_z',
                               'direction2_x', 'direction2_y', 'direction2_z'}
    fibre_shape_descriptors =  {'radius', 'center_x', 'center_y', 
                                 'direction_x', 'direction_y', 'direction_z'}
     
    geo_comm.introduce_objects(N=1, object_type='sphere')
    analysis = geo_comm.get_object_analysis()
    assert {1} == set(analysis.keys())
    assert analysis[1]['object_type'] == 'sphere'
    assert analysis[1]['object_count'] == 1   
    assert set(analysis[1]['shape_params'].keys()) == sphere_shape_descriptors
    assert all(set(analysis[1]['shape_params'][k].keys()) == {'mean', 'variance'} for k in sphere_shape_descriptors)
    
    geo_comm.introduce_objects(N=2, object_type='sphere')
    analysis = geo_comm.get_object_analysis()
    assert {1, 7} == set(analysis.keys())
    assert analysis[7]['object_type'] == 'sphere'
    assert analysis[7]['object_count'] == 2
    assert set(analysis[7]['shape_params'].keys()) == sphere_shape_descriptors
    assert all(set(analysis[7]['shape_params'][k].keys()) == {'mean', 'variance'} for k in sphere_shape_descriptors)
    
    geo_comm.introduce_objects(N=3, object_type='tube')
    analysis = geo_comm.get_object_analysis()
    assert {1, 2, 7} == set(analysis.keys())
    assert analysis[2]['object_type'] == 'tube'
    assert analysis[2]['object_count'] == 3
    assert set(analysis[2]['shape_params'].keys()) == tube_shape_descriptors
    assert all(set(analysis[2]['shape_params'][k].keys()) == {'mean', 'variance'} for k in tube_shape_descriptors)
    
    geo_comm.introduce_objects(N=4, object_type='prism')
    analysis = geo_comm.get_object_analysis()
    assert {1, 2, 3, 7} == set(analysis.keys())
    assert analysis[3]['object_type'] == 'prism'
    assert analysis[3]['object_count'] == 4
    assert set(analysis[3]['shape_params'].keys()) == prism_shape_descriptors
    assert all(set(analysis[3]['shape_params'][k].keys()) == {'mean', 'variance'} for k in prism_shape_descriptors)
    
    geo_comm.introduce_objects(N=5, object_type='platonic_solid')
    analysis = geo_comm.get_object_analysis()
    assert {1, 2, 3, 5, 7} == set(analysis.keys())
    assert analysis[5]['object_type'] == 'platonic_solid'
    assert analysis[5]['object_count'] == 5
    assert set(analysis[5]['shape_params'].keys()) == platonic_solid_shape_descriptors
    assert all(set(analysis[5]['shape_params'][k].keys()) == {'mean', 'variance'} for k in platonic_solid_shape_descriptors)
    
    geo_comm.introduce_objects(N=6, object_type='fibre')
    analysis = geo_comm.get_object_analysis()
    assert {1, 2, 3, 5, 6, 7} == set(analysis.keys())
    assert analysis[6]['object_type'] == 'fibre'
    assert analysis[6]['object_count'] == 6
    assert set(analysis[6]['shape_params'].keys()) == fibre_shape_descriptors
    assert all(set(analysis[6]['shape_params'][k].keys()) == {'mean', 'variance'} for k in fibre_shape_descriptors)

def test_chord_length_analysis(geo_comm):  
    geo_comm.introduce_objects(N=5,object_type='sphere')
    analysis = geo_comm.get_chord_length_analysis()
    assert {'phase_chord_lengths', 'interface_fractions', 'interface_per_volume_1/um'} == set(analysis.keys())
    assert {0, 1} == set(analysis['phase_chord_lengths'].keys())
    assert all({'mean_chord_length', 'variance', 'particle_count', 'volume_fraction'} == set(analysis['phase_chord_lengths'][k]) for k in analysis['phase_chord_lengths'])
    assert abs(sum(analysis['interface_fractions'].values()) - 1) < 1.0e-4
    
    geo_comm.introduce_objects(N=10,object_type='sphere')
    analysis = geo_comm.get_chord_length_analysis()
    assert {0, 1, 7} == set(analysis['phase_chord_lengths'].keys())
    assert all({'mean_chord_length', 'variance', 'particle_count', 'volume_fraction'} == set(analysis['phase_chord_lengths'][k]) for k in analysis['phase_chord_lengths'])
    assert abs(sum(analysis['interface_fractions'].values()) - 1) < 1.0e-4

    geo_comm.introduce_objects(N=7,object_type='prism')
    analysis = geo_comm.get_chord_length_analysis()
    assert {0, 1, 3, 7} == set(analysis['phase_chord_lengths'].keys())
    assert all({'mean_chord_length', 'variance', 'particle_count', 'volume_fraction'} == set(analysis['phase_chord_lengths'][k]) for k in analysis['phase_chord_lengths'])
    assert abs(sum(analysis['interface_fractions'].values()) - 1) < 1.0e-4
    
@pytest.mark.parametrize('mode',['unscaled', 'area_scaled', 'fully_scaled'])
def test_variance_analysis(geo_comm, mode):
    # introduce some objects to test with
    geo_comm.introduce_objects(N=10,object_type='sphere')
    geo_comm.introduce_objects(N=10,object_type='prism')
    
    with pytest.raises(ValueError):
        analysis = geo_comm.get_variance_analysis(mode='no_such_mode')
    
    # run variance analysis
    analysis = geo_comm.get_variance_analysis(mode)
    
    # check if we get expected results
    assert set(analysis.keys()) == {f'variance_{mode}_8', f'variance_{mode}_16', 
                                    f'variance_{mode}_32', 'porosity'}
    assert all(set(analysis[var].keys()) == {0, 1, 3} 
               for var in [f'variance_{mode}_8', f'variance_{mode}_16', 
                                    f'variance_{mode}_32'])
    assert set(analysis['porosity'].keys()) == {'min', 'max'}
    assert all(all(type(v) == float for v in analysis[var].values()) 
               for var in [f'variance_{mode}_8', f'variance_{mode}_16', 
                                    f'variance_{mode}_32'])
        
    # introduce some more objects
    geo_comm.introduce_objects(N=10,object_type='sphere')
    geo_comm.introduce_objects(N=10,object_type='sphere')
    
    # run another analysis
    analysis = geo_comm.get_variance_analysis(mode)
    
    # check again if expected output is obtained
    assert set(analysis.keys()) == {f'variance_{mode}_8', f'variance_{mode}_16', 
                                    f'variance_{mode}_32',
                                    'porosity'}
    assert all(set(analysis[var].keys()) == {0, 1, 3, 7, 13} 
               for var in [f'variance_{mode}_8', f'variance_{mode}_16', 
                                    f'variance_{mode}_32'])
    assert set(analysis['porosity'].keys()) == {'min', 'max'}
    assert all(all(type(v) == float for v in analysis[var].values()) 
               for var in [f'variance_{mode}_8', f'variance_{mode}_16', 
                                    f'variance_{mode}_32'])
    
def test_variance_analysis_all(geo_comm):
    # introduce some objects to test with
    geo_comm.introduce_objects(N=10,object_type='sphere')
    geo_comm.introduce_objects(N=10,object_type='prism')

    # test if we can run multiple variance analysis sequentially    
    analysis_unscaled_0 = geo_comm.get_variance_analysis()
    analysis_unscaled_1 = geo_comm.get_variance_analysis('unscaled')
    analysis_area_scaled = geo_comm.get_variance_analysis('area_scaled')
    analysis_fully_scaled = geo_comm.get_variance_analysis('fully_scaled')
    
    # do some basic checks to see if analysis results have been created
    assert 'variance_unscaled_8' in analysis_unscaled_0
    assert  set(analysis_unscaled_0['variance_unscaled_8'].keys()) == {0, 1, 3} 
    
    assert 'variance_unscaled_8' in analysis_unscaled_1
    assert  set(analysis_unscaled_1['variance_unscaled_8'].keys()) == {0, 1, 3} 
    
    assert 'variance_area_scaled_8' in analysis_area_scaled
    assert  set(analysis_area_scaled['variance_area_scaled_8'].keys()) == {0, 1, 3} 
    
    assert 'variance_fully_scaled_8' in analysis_fully_scaled
    assert  set(analysis_fully_scaled['variance_fully_scaled_8'].keys()) == {0, 1, 3} 

def test_region_analysis(geo_comm):
    geo_comm.introduce_objects(N=5,object_type='sphere')
    analysis = geo_comm.get_3d_region_analysis()
    assert {1} == set(analysis.keys())    # make sure we get a volume report for all phases
    assert all([len(rep) > 0 for rep in analysis.values()])            # check if report has some content
    
    geo_comm.introduce_objects(N=5,object_type='tube')
    analysis = geo_comm.get_3d_region_analysis()
    assert {1, 2} == set(analysis.keys())    # make sure we get a volume report for all phases
    assert all([len(rep) > 0 for rep in analysis.values()])            # check if report has some content
    
    geo_comm.introduce_objects(N=5, object_type='prism')
    analysis = geo_comm.get_3d_region_analysis()
    assert {1, 2, 3} == set(analysis.keys())    # make sure we get a volume report for all phases
    assert all([len(rep) > 0 for rep in analysis.values()])            # check if report has some content    

  
def test_split_objects(geo_comm):
    geo_comm.introduce_objects(N=50)
    vol_fracs = geo_comm.get_volume_fractions()
    assert len(vol_fracs.keys()) == 1 # in the beginning there should only be one phase
    
    geo_comm.split_objects(1, 0.5)
    vol_fracs = geo_comm.get_volume_fractions()
    assert len(vol_fracs.keys()) == 2 # make sure that after split a new phase is introduced
    
  
def test_transform_objects(geo_comm):    
    geo_comm.introduce_objects(N=50, object_type='sphere', 
                           shape_description={'radius': 5.0e-6})
    vol_fracs = geo_comm.get_volume_fractions()
    assert len(vol_fracs.keys()) == 1 # in the beginning there should only be one phase
    
    geo_comm.transform_objects(25, 1, 'prism', shape_description={})
    vol_fracs = geo_comm.get_volume_fractions()
    assert len(vol_fracs.keys()) == 2 # now there should be two phases
    
    geo_comm.transform_objects(10, 1, 'tube', shape_description={})
    vol_fracs = geo_comm.get_volume_fractions()
    assert len(vol_fracs.keys()) == 3 # now there should be three phases
    
def test_set_overlap(geo_comm):
    geo_comm.initialize_rve(rve_dims=32)
    geo_comm.introduce_objects(N=1, shape_description={'radius': 15e-6}, randseed=42)
    geo_comm.introduce_objects(N=1, shape_description={'radius': 15e-6},)
  
    # invalid phases
    with pytest.raises(ValueError):
        geo_comm.set_overlap({3: 'shared', 18: 'shared'})
    # invalid format for priority
    with pytest.raises(ValueError):
        geo_comm.set_overlap({1: 'shared'})
    # invalid (negative) priority
    with pytest.raises(ValueError):
        geo_comm.set_overlap({1: (-1, 'shared')})
    # invalid tie-breaker rule
    with pytest.raises(ValueError):
        geo_comm.set_overlap({1: (0, 'no-such-rule')})
        
    # first we set phase 1 to higher priority -> should have higher volume fraction
    geo_comm.set_overlap({1: (0, 'shared'), 7: (1, 'shared')})
    vol_fracs_0 = geo_comm.get_volume_fractions()
    print(vol_fracs_0)
    assert vol_fracs_0[1] > vol_fracs_0[7]
    
    # now we change priorities -> phase 7 should have higher volume fraction
    geo_comm.set_overlap({1: (1, 'shared'), 7: (0, 'shared')})
    vol_fracs_1 = geo_comm.get_volume_fractions()
    print(vol_fracs_1)
    assert vol_fracs_1[1] < vol_fracs_1[7]
    
    # now we set them to the same priority with different tie-breaker-rules
    # rule: random -> we should have volume fraction somewhere between the 
    # previous cases
    geo_comm.set_overlap({1: (1, 'random'), 7: (1, 'random')})
    vol_fracs_rand = geo_comm.get_volume_fractions()
    assert vol_fracs_1[1] <= vol_fracs_rand[1] <= vol_fracs_0[1]
    assert vol_fracs_0[7] <= vol_fracs_rand[7] <= vol_fracs_1[7]
    
    # rule: voronoi -> volume fractions should be almost the same
    geo_comm.set_overlap({1: (1, 'voronoi'), 7: (1, 'voronoi')})
    vol_fracs_voronoi = geo_comm.get_volume_fractions()
    diff = abs(vol_fracs_voronoi[1] - vol_fracs_voronoi[7])/(vol_fracs_voronoi[1] + vol_fracs_voronoi[7])
    assert diff < 0.05
    

def test_dilation(geo_comm):
    geo_comm.introduce_objects(N=10)

    phase = 1
    for nn in range(1, 4):
        for rep in range(1, 5):
            vol_frac = geo_comm.get_volume_fractions()  # volume fraction before dilation operation
            geo_comm.dilation(number_of_neighbors=nn, phase=phase, repetitions=rep)
            vol_frac_new = geo_comm.get_volume_fractions()  # volume fraction after dilation operation
            assert vol_frac[phase] < vol_frac_new[phase]    # make sure that dilation increases the volume
            
def test_screenshot(geo_comm_tmpdir):
    # create a single RVE, mesh it and run Ansys simulation of elasticity
    geo_comm, tmpdir = geo_comm_tmpdir
    
    # 1. create RVE
    filename = 'testfile'
    voxel_path = pathlib.Path(tmpdir, filename + '.val')
    object_path = pathlib.Path(tmpdir, filename + '.obj')
    screenshot_path = pathlib.Path(tmpdir, filename + '.jpg')
    
    geo_comm.initialize_rve(rve_dims=32)
    geo_comm.introduce_objects(N=15)
    geo_comm.view_voxels(screenshot_file=screenshot_path.name)

    # make sure screenshot file is created
    assert screenshot_path.exists(), ".jpg was not created"