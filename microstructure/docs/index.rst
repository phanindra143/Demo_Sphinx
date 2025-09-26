.. MPaut documentation master file, created by
   sphinx-quickstart on Wed Dec  9 13:21:40 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Documentation for MPaut (Microstructure Property Automation)
============================================================
MPaut is a collection of python scripts for automatic generation and 
simulation of microstructures.
The goal is to provide tools for generating large datasets of realistic 
microstructures. 
These will serve as the basis for advanced machine learning algorithms in 
order to accelerate the development of ceramic materials with specific 
material properties.

MPaut extends the existing microstructure generation tools ``GeoVal`` and 
``VoxSM`` developed at `HTL <https://www.htl.fraunhofer.de/>`_ in the previous 
years by a python interface.
This makes it possible to generate large numbers of microstrutures 
automatically for which various material properties are computed by Finite 
Element analysis in ``ANSYS``.

Installation
------------
Please install the following packages in order to use MPaut:
 - `pywinauto <https://pypi.org/project/pywinauto/>`_
 - `pywin32 <https://pypi.org/project/pywin32/>`_
 - `numpy <https://pypi.org/project/numpy/>`_
 
Optionally, if you want 3D visualization of the generated voxel 
microstructures, you also need the following packages:
 - `pyqtgraph <https://pypi.org/project/pyqtgraph/>`_
 - `pyopengl <https://pypi.org/project/PyOpenGL/>`_
 - `PyQt5 <https://pypi.org/project/PyQt5/>`_
 
For FE simulations of generated RVEs you need:
 - `ansys-mapdl-core <https://github.com/pyansys/pymapdl/>`_
 
For convencience you can also install ``MPaut`` from an archive through pip, 
which automatically installs the required dependencies for you::
  pip install MPaut-<version>.tar.gz


.. note:: 

    After the installation of ``pywin32`` you need to issue the following 
    command in your conda environment once, otherwise ``pywinauto`` will not 
    work correctly::
     python <path_to_conda_env>\Scripts\pywin32_postinstall.py -install

General project idea
--------------------
The pipeline for simulating material properties for a microstructure consists 
of the following steps:

1. Generation of a voxel representative volume element (RVE) in ``GeoVal``
2. Meshing of the voxel RVE with ``VoxSM``
3. Simulation of the meshed RVE with ``ANSYS``

These individual steps have been automated by adding a python interface for 
``GeoVal`` and ``VoxSM``, resp. using the python interface to ``ANSYS`` 
provided by `PyMAPDL <https://mapdldocs.pyansys.com/>`_.
The following pages briefly explain how these steps have been implemented in 
``MPaut`` and provide some examples of use.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   geoval.rst
   voxsm.rst
   ansys.rst

.. automodule:: MPaut
	:members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
