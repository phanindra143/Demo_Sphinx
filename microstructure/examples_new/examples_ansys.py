# -*- coding: utf-8 -*-
from ansys.mapdl import core as pymapdl
from MPaut import ansys_subprocess

# launch MAPDL instance locally
mapdl = pymapdl.launch_mapdl()

# alternatively, launch with remote MAPDL instance
#ip = '<remote-ip-here>'
#mapdl = pymapdl.Mapdl(ip=ip, port=50052, request_instance=False)

# create a mesh generator object by passing it an MAPDL instance
mesh_gen = ansys_subprocess.AnsysMeshGenerator(mapdl)
 	
# specify path to folder with VoxSM output files ('_main.win', '1_nodes.win', '2_SHELL_GB_RVE.win', etc.)
voxsm_data_folder = 'output'
 	
# the mesh is generated with options read from the files in the given folder
mesh_info = mesh_gen.create_mesh_from_VoxSM_output(voxsm_data_folder)

# create plots for the different materials in the RVE
for mat_nr in mesh_info['materials']:
    mapdl.esel(item='mat', vmin=mat_nr, vmax=mat_nr)
    if mapdl.mesh.n_elem > 0:
        mapdl.eplot()


# quit mapdl
mapdl.exit()