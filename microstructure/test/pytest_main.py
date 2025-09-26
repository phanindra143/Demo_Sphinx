# -*- coding: utf-8 -*-
# Entry point for pytest
#
# This allows debugging of pytest unit tests in Spyder (or command line).
# In Spyder, set your breakpoints as required, then run this script
# (no need to debug, run is enough).
# The debugger will break automatically on the pytest.main().
# Continue the execution to jump to your own breakpoints.
import pytest
import pdb

pdb.set_trace()

#pytest.main(['test_geoval.py'])

#pytest.main(['test_voxsm.py', '-k', 'test_simplify'])
pytest.main(['test_voxsm.py'])

#pytest.main(['test_ansys_run.py', '-k', 'test_mock_mesh_creation_VoxSM[scripts_dir20]'])

#pytest.main(['test_ansys_run.py', '-k', 'test_mock_mesh_creation_VoxSM[scripts_dir21]'])
#pytest.main(['test_ansys_run.py', '-k', 'test_mock_mesh_creation_VoxSM[scripts_dir20]'])

#pytest.main(['test_ansys_run.py', '-k', 'test_sequential_script_run_node_elem_creation'])
#pytest.main(['test_ansys_convert.py'])

pass