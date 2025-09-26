# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 12:24:51 2021

@author: pirkelma
"""
import sys
import numpy as np
import os
from pathlib import Path

sys.path.append("../src")   # this adds the mother folder  
                         # "my_python_scripts_folder/" to the python path 
                         # It will allow you to import your modules.
                         # Adjust depending where your tests scripts location
                         
from MPaut import sim_utils


def create_list(nparr):
    res = []
    for i in range(6):
        res.append({k: v for k,v in zip(['xx', 'yy', 'zz', 'xy', 'xz', 'yz'], nparr[i,:])})
    return res

def load_elc_data(file):
    # read values from elc output file and store as dicts
    dat = np.genfromtxt(file, comments='/%', skip_footer=1)
    
    # skip every second entry because it contains nan (description string 
    # converted to float)
    elc_dat = dat[1::2]
    fs = elc_dat[::2,1:]
    es = elc_dat[1::2,1:]
    
    # convert data to dicts
    sig_d = create_list(fs)
    eps_d = create_list(es)
    
    return sig_d, eps_d

def load_wlf_data(file):
    # read values from wlf output file and store as dicts
    dat = np.genfromtxt(file, comments='/%')
    
    # skip every second entry because it contains nan (description string 
    # converted to float)
    wlf_dat = dat[1::2]
    qs = wlf_dat[::2,1:]
    dts = wlf_dat[1::2,1:]
    
    # convert data to dicts
    q_d = [{k: v for k, v in zip(['x', 'y', 'z'], qs[i,:])} for i in range(3)]
    dt_d = [{k: v for k, v in zip(['x', 'y', 'z'], dts[i,:])} for i in range(3)]
    
    return q_d, dt_d

def test_stiffness_computation(elc_data):
    # elc_data[0] = out_elcs.out    data file
    # elc_data[1] = crystal.sgd     crystal Ansys output file with reference data
    
    # read values from elc output file
    sig_d, eps_d = load_elc_data(elc_data[0])
    
    # compute stiffness matrix C
    C, svd_ratio = sim_utils.compute_stiffness_matrix_svd(eps_d, sig_d)
    print("svd_ratio = ", svd_ratio)
    
    # read data from crystal output file for comparison
    with open(elc_data[1]) as f:
        lines = f.readlines()
        cref = []
        # read data for C
        for line in lines[1:22]:
            c = float(line.split('=')[1])
            cref.append(c)
        cref = np.array(cref) / 1e9
            
    # check if values match
    c = C[np.tril_indices(6)]
    assert np.allclose(c, cref, atol=1.e-5), "the entries of the stiffness matrix do not match"
    
def test_stiffness_computation_voigt_reuss():
    # check if we can reproduce the result from the given folder
    folder = "R:/166_320/Ablage_Simulationen/Modellbildung_Simulation_CMC-SiC_[Vorlauf+WiMi+MaVo]/04_04_2017_Modellierung_Matrix_mikro_ditt_[WiMi]/1_Volumenanteil-SiC-Si_ELC/Rein-ohne-Poren"
    
    elc_files = {}
    for root, dirs, files in os.walk(folder):
        if 'out_elc.out' in files:
            elc_files[str(Path(root).stem)] = Path(root) / 'out_elc.out'

    data_ref_voigt = {
        'E': np.array([216.70, 242.03, 270.72, 303.39, 341.65, 382.25, 427.11]),
        'nu':np.array([0.21, 0.20, 0.20, 0.19, 0.19, 0.18, 0.18]),
        'K': np.array([123.13, 135.20, 148.64, 163.70, 181.10, 199.27, 219.07]),
        'G':np.array([89.79, 100.71, 113.14, 127.36, 144.08, 161.93, 181.74])}
    
    data_ref_reuss = {
        'E': np.array([216.70, 242.02, 270.72, 303.39, 341.64, 382.25, 427.11]),
        'nu': np.array([0.21, 0.20, 0.20, 0.19, 0.19, 0.18, 0.18]),
        'K': np.array([123.12, 135.19, 148.64, 163.70, 181.10, 199.27, 219.07]),
        'G': np.array([89.79, 100.70, 113.14, 127.35, 144.08, 161.93, 181.74])
        }

    data_voigt = {}
    data_reuss = {}

    for name, file in elc_files.items():
        sig_d, eps_d = load_elc_data(file)
        
        # compute stiffness matrix C
        C, svd_ratio = sim_utils.compute_stiffness_matrix_svd(eps_d, sig_d)
        
        # compute voigt average
        voigt = sim_utils.voigt_average(C)
        data_voigt[name] = voigt
        
        # compute reuss average
        reuss = sim_utils.reuss_average(C)
        data_reuss[name] = reuss
        
    for i, data in enumerate(data_voigt.items()):
        name, dic = data
        for prop, value in dic.items():
            assert abs(data_ref_voigt[prop][i] - data_voigt[name][prop]) < 1e-2
            
    for i, data in enumerate(data_reuss.items()):
        name, dic = data
        for prop, value in dic.items():
            assert abs(data_ref_reuss[prop][i] - data_reuss[name][prop]) < 1e-2
    
def test_thermal_conductivity_computation(wlf_data):
    q_d, dt_d = load_wlf_data(wlf_data[0])
    
    K = sim_utils.compute_thermal_conductivity_matrix(q_d, dt_d)
    
    # read data from crystal output file for comparison
    with open(wlf_data[1]) as f:
        lines = f.readlines()
        kref = []
        # read data for C
        for line in lines[24:30]:
            k = float(line.split('=')[1])
            kref.append(k)
        kref = np.array(kref)

    k = K[np.tril_indices(3)]
    assert np.allclose(k, kref, atol=1.e-2), "the entries of the thermal conductivity matrix do not match"