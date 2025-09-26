import numpy as np
import logging
from pathlib import Path
from .sim_utils import compute_stiffness_matrix_svd, voigt_average, reuss_average, hill_average

class Simulator:
    """Template class for material property simulations of RVEs in pyansys."""
    
    default_options = {}
    def __init__(self, mapdl):
        """Create a simulator object.
        
        You must pass an ``MAPDL`` instance which will handle the
        communication with ``Ansys``.
        

        Parameters
        ----------
        mapdl : PyMAPDL Object
            Handle for managing communication with pyansys.
        """
        self.mapdl = mapdl
        self.solver_tolerance = 1e-08
        self.db_checks = True
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        self.log_fh = logging.FileHandler('ansys_sim.log', mode='w')
        self.log_fh.setLevel(logging.DEBUG)
        self.logger.addHandler(self.log_fh)
        
    def simulate(self, db_file, params={}, options={}):
        """Carry out a material property simulation run.
        
        You should override this method with your own implementation.
        The method expects an ansys database file as input, which should contain
        the definition of the RVE mesh for the simulations.
        
        The other input parameters are the ``param`` dictionary, which should 
        be used to set various parameters for the simulations (such as the 
        definition of material parameters for the different phases in the mesh)
        and the ``options`` dictionary, which controls meta-parameters of the
        simulation process (e.g. number of iteration, tolerances, etc.).

        Parameters
        ----------
        db_file : pathlib.Path
            Path to the database with the mesh definition.
        params : dict, optional
            Dictionary for setting various paramters for the simulation. 
            The default is {}.
        options : dict, optional
            Dictionary for setting options of the simulation. 
            The default is {}.
        """
        # override this method for your simulation
        pass
    
    def _setup_sim(self, db_file, options):
        """Setup up simulation by loading database file, performing some checks
        and preparing the output file.
        

        Parameters
        ----------
        db_file : TYPE
            DESCRIPTION.
        options : TYPE
            DESCRIPTION.

        Returns
        -------
        output_path : pathlib.Path
            Path of the output file for writing results to.

        """
        self.logger.debug("Setting up simulation with "\
                         f"db_file = {db_file}\n"\
                         f"options = {options}")
        self._check_db_file(db_file)
            
        # set options for the simulation (use default when user did not
        # provide an option)
        for o in set(self.default_options.keys()) - set(options.keys()):
            options[o] = self.default_options[o]
                
        # batch
        self.mapdl.finish()
        self.mapdl.clear()
        self.mapdl.run("/filname,WLF")
        self.mapdl.prep7()

        self.mapdl.resume(Path(db_file).stem, "db")
        
        # perform some checks if database file is ok
        self._check_db_sanity()

    def _check_db_file(self, db_file):
        """Checks if the provided database file exists in the current Ansys
        working directory and raises Exceptions if it does not.
        

        Parameters
        ----------
        db_file : str
            Filename of the database file.
        """
        if self.db_checks:
            if not db_file in self.mapdl.list_files():
                raise FileNotFoundError(f"Database file with definition of mesh not found in Ansys working directory {self.mapdl.directory}")
       
    def _check_db_sanity(self):
        """Check whether the loaded database file is good for simulations.
        
        It is checked, whether there are nodes and elements declared in the 
        database.
        """
        if self.db_checks:
            # get number of nodes and elements and make sure there are some
            self.mapdl.allsel("all")
            if not self.mapdl.mesh.n_node > 0:
                raise RuntimeError("Database does not contain mesh nodes. Please investigate!")
            if not self.mapdl.mesh.n_elem > 0:
                raise RuntimeError("Database does not contain mesh elements. Please investigate!")
                
            # TODO: check if number of materials defined matches number of materials
            # for which material parameters were provided
            #  there seems to be a problem when querying the number of materials
            #  *get, matcount, MAT,,COUNT
            #  -> should report number of defined materials
            #  *get, matmax, MAT,,NUM,MAX
            #  -> should report the highest defined material number
            # however, this only works after material parameters have been assigned
            # to a material number
            # what we need is to query the material number for each existing element
            # to check that no elements exist for which no material parameters have
            # been defined, or give a warning when material parameters have been
            # defined without any elements of the given material type
            # maybe *GET, Par, ELEM, 0, MATM could help?
            #  -> yields highest material number that is referenced by an element
        
    def _compute_phase_volumes(self, phase_data):
        """Compute the volume of the RVE and the volume fractions of the 
        individual phases"
        

        Parameters
        ----------
        phase_data : list
            list of dicts with information about the phases (phase number, etc.)

        Returns
        -------
        v_RVE : float
            total volume of RVE
        v_phase : dict
            volume fraction of individual phases
        """
        self.logger.debug(f"computing phase volumes with phase_data = {phase_data}")
        v_mat = {}
        for mat_data in phase_data:
            mat_num = mat_data['phase_number']
            self.mapdl.allsel("all")
            self.mapdl.esel("s", "mat", "", mat_num)  #volumenanteil fuer material berechnen
            self.mapdl.etable("e_vol", "volu", "")
            self.mapdl.ssum()
            v_mat[mat_num] =  self.mapdl.get(entity='ssum', entnum=0, 
                                             item1='item', it1num='e_vol')
            self.mapdl.etable("e_vol", "eras")
            
        # Volumen des gesamten Wuerfels bestimmen (v_i) und Elementtabelle mit Volumen anlegen
        self.mapdl.allsel("all")
        self.mapdl.etable("e_vol", "volu", "")
        self.mapdl.etable("s_1", "s", 1)
        self.mapdl.smult("sv", "s_1", "e_vol")
        self.mapdl.ssum()
        v_RVE = self.mapdl.get(entity='ssum', entnum=0, 
                             item1='item', it1num='e_vol')
        v_phase = {mat_data['phase_number']: v_mat[mat_data['phase_number']] / v_RVE 
                       for mat_data in phase_data}
        return v_RVE, v_phase
    
    def _write_values(self, filepath, ifx, value_dict, key_list, key_list_prefix=''):
        """Append the values in ``value_dict`` to the given output file in the
        format described below.
        
        This function reproduces the same output format as the original Ansys
        code which used the ``vwrite`` command.
        For example, the output of a dictionary ``ffs = {'xx': 0.05085, ..., 'yz': -0.02441 }``
        by calling
            >>> self._write_values('text.txt', 1, ffs, 
                                   key_list=['xx','yy','zz','xy','xz','yz'], 
                                   key_list_prefix='f')
        might look as follows:
            ifx            fxx            fyy            fzz            fxy            fxz            fyz     
/%
        1.00000        0.05085        0.06485       49.07120       -0.04103       -0.12161       -0.02441
/%
        The first column is the current iteration ``ifx``.
        The order of the following columns is determined by the ``key_list`` 
        parameter. It is possible to specify a prefix for the keys in the output
        with the ``key_list_prefix``.
        After each row follows a new line with a comment sign ``/%``.
        
        Parameters
        ----------
        filepath : Path
            Path to the output file. The file will be opened in append mode and
            closed after writing.
        ifx : integer
            Current iteration.
        value_dict : dict
            Dictionary with values to be written in the file.
        key_list : list of string
            Keys use for obtaining values from ``value_dict``. The order 
            determines the order of the values in the output.
        key_list_prefix : string
            Prefix that will be placed in front of each entry of ``key_list`` 
            in the output.

        """
        with open(filepath, 'a') as outfile:
            np.savetxt(outfile, np.array([['ifx'] + [key_list_prefix + k for k in key_list]]), 
                           fmt='% 15s', footer='/%', comments='')
            np.savetxt(outfile, np.array([[ifx] + [value_dict[k] for k in key_list]]), 
                           fmt='% 15f', footer='/%', comments='')

    
class ThermalConductivitySimulator(Simulator):
    default_options = {'boundary_nodes_selection_tolerance': 0.01,
                       'solver_tolerance': 1e-08,
                       }
        
    def simulate(self, db_file, phase_mat_params, options={}):
        """Run simulation of thermal conductivity for a RVE.
        
        This will compute the thermal conductivity of the RVE by applying a
        temperature gradient across two opposing faces of the RVE cube and
        evaluating the resulting (static) heat flow within the RVE.
        
        The simulation considers the thermal conductivity in all three axis (x,
        y and z).
        
        To run the simulation you must specify a database file containing the
        definition of the RVE mesh and the ``phase_mat_params`` dictionary 
        which should contain the phase number (as defined in the mesh) and the 
        associated thermal conductivity of the constituent phases of the RVE.
        
        The result of the simulation will be written to an output file which 
        will be placed in the current Ansys working directory.
        
        Optionally, you can pass the ``option`` dictionary to set various 
        options for the simulation (such as tolerances, output filename, etc.).
        

        Parameters
        ----------
        db_file : string
            Database with definition of nodes, elements, and mesh for the 
            simulation
        phase_mat_params : dict
            Dictionary of phases and corresponding material parameters
             e.g. { 'SiC': {'phase_number': 3, 'therm_cond': 185},
            'Si': {'phase_number': 2, 'therm_cond': 75} }
        options : dict
            Dictionary with options for controlling the simulation.
            
            The following defaults are used:
                {
                    'boundary_nodes_selection_tolerance': 0.01,
                     'solver_tolerance': 1e-08,
                 }
            Name of the file for storing the results of the simulation.
            The file will be placed in the current Ansys working directory.
            Not that if the file already exists it will be overwritten.
            The default is ``'out_wlf.out'``.

        """
        self.logger.info("running simulation of thermal conductivity")
        self.logger.debug(f" db_file = {db_file}")
        self.logger.debug(f" phase_mat_params = {phase_mat_params}")
        self.logger.debug(f" options = {options}")

        # source script: R:\166_320\Ablage_Simulationen\
        #    Modellbildung_Simulation_CMC-SiC_[Vorlauf+WiMi+MaVo]\
        #    04_04_2017_Modellierung_Matrix_mikro_ditt_[WiMi]\
        #    2_Waermeleitfähigket_SiC-Si\_WLF.win
        
        # TODO started with converting script for thermal conductivity simulation
        #  need a RVE to test it with -> look in the folders above and generate
        #  one from the voxel file
        self._setup_sim(db_file, options)
        
        # get length of RVE from the mesh
        Lx, Ly, Lz = self.mapdl.mesh.nodes.max(axis=0)
        
        if len(set([Lx, Ly, Lz])) > 1:
            raise NotImplementedError("The loaded mesh has different dimension in x, y, and z. This case is not implemented yet.")
        else:
            Ls = {'x': Lx, 'y': Ly, 'z': Lz}
        
        # *** Definition of material parameters ***
        for phase_name, mat_data in phase_mat_params.items():            
            # *** Attribute material to different phases ***    
            self.logger.debug("assigning thermal conductivity of "\
                             f"{mat_data['therm_cond']} to material number "\
                             f"{mat_data['phase_number']}")
            self.mapdl.mp("kxx", mat_data['phase_number'], mat_data['therm_cond'])

        # *** Parameters ***
        self.mapdl.run("/graphics,power")
        self.mapdl.run("/view,1,1,1,1")
        self.mapdl.run("/number,1")
        self.mapdl.run("/pnum,mat,1")
        self.mapdl.run("/edge,,0,  ")  # 1: all edges of mesh, 0: only Particle-edges
        self.mapdl.run("/rgb,index,100,100,100,0 ")  # white BG
        self.mapdl.run("/rgb,index,0,0,0,15      ")  # black labels

        self.mapdl.save("test", "db", "")
 
        thermal_cond = {}
        # simulate heat flow in all 3 axis
        for ifx, ax in enumerate(['x', 'y', 'z'], 1):
            self.logger.debug(f"computing thermal conductivity in {ax}-axis ...")

            self.mapdl.resume("test", "db")
            
            # get length of RVE in current ax
            L = Ls[ax]
            delver = L * options['boundary_nodes_selection_tolerance']  # tolerance for selection of boundary nodes
            
            self.mapdl.allsel("all")
            self.mapdl.finish()
            self.mapdl.run("/solu")
            # Temperaturen auf ax=0 und ax=l Flaechen setzen
            self.mapdl.allsel("all")
            self.mapdl.nsel("s", "loc", ax, -delver, delver)
            self.mapdl.d("all", "temp", 0)
            self.mapdl.allsel("all")
            self.mapdl.nsel("s", "loc", ax, L-delver, L+delver)
            self.mapdl.d("all", "temp", 1)
            # *** SOLVE ***
            self.logger.debug("starting solve ...")
            self.mapdl.allsel("all")
            self.mapdl.finish()
            self.mapdl.run("/solu")
            self.mapdl.run("/status,solu")
            self.mapdl.eqslv("jcg", options['solver_tolerance'])  #JCG solver
            self.mapdl.allsel("all")
            self.mapdl.solve()
            self.mapdl.finish()
            self.logger.debug("solve finished!")

            
            # *** SET POSTPROCESSING ***
            self.logger.debug("starting postprocessing ...")
            self.mapdl.post1()
            v_RVE, v_phase = self._compute_phase_volumes(phase_mat_params.values())
            print("phase volumes: ", v_phase)

            self.mapdl.allsel()
            self.mapdl.etable("e_vol", "volu", "")
            qs = {}
            dts = {}
            for v in ['x', 'y', 'z']:
                self.mapdl.etable("e_tf", "tf", f"{v}")
                self.mapdl.etable("e_tg", "tg", f"{v}")
                self.mapdl.smult("tfv", "e_tf", "e_vol")
                self.mapdl.smult("tgv", "e_tg", "e_vol")
                self.mapdl.ssum()
                m_i = self.mapdl.get(entity="ssum", entnum=0, item1="item",
                                      it1num="tgv")
                n_i = self.mapdl.get(entity="ssum", entnum=0, item1="item",
                                      it1num="tfv")
                qs[v] = n_i / v_RVE
                dts[v] = m_i / v_RVE
                self.mapdl.etable("e_tf", "eras")
                self.mapdl.etable("e_tg", "eras")
                self.mapdl.etable("tfv", "eras")
                self.mapdl.etable("tgv", "eras")

            self.mapdl.nsel("S", "LOC", ax, -delver, delver)
            self.mapdl.fsum(0, "ALL")
            wlz = self.mapdl.get(entity="FSUM", item1="item", it1num="HEAT")
            
            # compute thermal conductivity
            th_cond = wlz / L
            
            # store thermal conductivity for current axis in dict
            thermal_cond[ax] = {'qs': qs,
                                'dts': dts,
                                'thermal_cond': th_cond}
            
            self.logger.debug("postprocessing finished!")
            self.logger.debug(f"resulting thermal conductivity in {ax}-axis: "\
                             f"{thermal_cond[ax]}")

            # plot:
            self.mapdl.allsel()
            self.mapdl.run("/show,jpeg")
            self.mapdl.plnsol("temp")
            self.mapdl.run("/show,close")
            
        # compute mean of thermal conductivities
        th_cond_mean = np.array([thermal_cond[ax]['thermal_cond'] for ax in ['x', 'y', 'z']]).mean()
        thermal_cond['mean'] = th_cond_mean
        
        thermal_cond['v_phase'] = v_phase

        self.mapdl.save("sol_wlf", "db")
        
        self.logger.info("finished simulation of thermal conductivity. "\
                         f"resulting thermal conductivities: {thermal_cond}")
                    
        return thermal_cond

        
class ELCsSimulator(Simulator):
    default_options = {'boundary_nodes_selection_tolerance': 0.005,
                   'delrot_factor': 1e-4,
                   'delshi_factor':1.5e-4,
                   'solver_tolerance': 1e-08,
                   } 
    
    def simulate(self, db_file, phase_mat_params, options={}):
        """Run simulations and calculate the elastic properties for a RVE.
        
        You must specify the mesh for the elasticity simulation by passing a
        database file where the mesh is already created. In addition, you must
        specify a dictionary with the material properties for the different 
        phases in the mesh.
        
        The simulation will perform six load steps, applying small 
        displacements for each face of the RVE cube and computing the 
        resulting stress and strain tensors. From those, we compute the 
        elasticity tensor, which is then used to get estimates for the 
        modulus of elasticity ``E``, poisson ratio ``nu``, bulk modulus ``K`` 
        and shear modulus ``G`` using the Voigt-Reuss-Hill averaging method.

        Parameters
        ----------
        db_file : string
            Name of the database file with definition of nodes, elements, and 
            mesh to use in the simulation. The file must be located 
            in the current ansys working directory.
        phase_mat_params : dict
            Dictionary of phases and corresponding material parameters e.g. 
                { 'WC': {'phase_number': 3, 'emod': 680, 'pois': 0.22},
                'Co': {'phase_number': 2, 'emod': 210, 'pois': 0.31},
                'Pore': {'phase_number': 10000, 'emod': 1e-4 * 1e-9, 'pois': 1e-4}
                }
            The elastic modulus should be provided in ``GPa``.
        options : dict, optional
            Dictionary with options for controlling the simulation.
            
            If not provided the following defaults will be used:
                {
                    'boundary_nodes_selection_tolerance': 0.005,
                     'delrot_factor': 1e-4,
                     'delshi_factor':1.5e-4,
                     'solver_tolerance': 1e-08,
                 }

        Returns
        -------
        dict
            Dictionary with the results of the simulation. It contains the
            following data:
                - ``'stiffness_tensor'``: resulting stiffness tensor C from the 
                  simulation computed using 
                  :py:func:`MPaut.sim_utils.compute_stiffness_matrix_svd`
                - ``'svd_ratio'``: ratio of minium and maximum singular values 
                  from the singular value decomposition used in the computation
                  of the stiffness matrix
                - ``'voigt_avg'``: material properties computed by the 
                  voigt average, see :py:func:`MPaut.sim_utils.voigt_average`
                - ``'reuss_avg'``: material properties computed by the reuss
                  average, see :py:func:`MPaut.sim_utils.reuss_average`
                - ``'hill_avg'``: material properties computed by the hill 
                  average, see :py:func:`MPaut.sim_utils.hill_average`
                - ``'sigma'``: entries of the strain tensor from each load step
                - ``'epsilon'``: entries of the stress tensor from each load 
                  steps
                - ``'v_phase'``: volume fraction of the mesh phases

        """
        self.logger.info("running simulation of elasticity")
        self.logger.debug(f" db_file = {db_file}")
        self.logger.debug(f" phase_mat_params = {phase_mat_params}")
        self.logger.debug(f" options = {options}")
        
        self._setup_sim(db_file, options)
        
        # get length of RVE from the mesh
        Lx, Ly, Lz = self.mapdl.mesh.nodes.max(axis=0)
        
        if len(set([Lx, Ly, Lz])) > 1:
            raise NotImplementedError("The loaded mesh has different dimension in x, y, and z. This case is not implemented yet.")
        else:
            L = Lx
                
        # *** Definition of material parameters ***
        for phase_name, mat_data in phase_mat_params.items():            
            # *** Attribute material to different phases ***
            self.logger.debug("assigning material parameters to material number "\
                             f"{mat_data['phase_number']}: ex = {mat_data['emod'] * 1e9}, "\
                             f"prxy = {mat_data['pois']}")
            self.mapdl.mp("ex", mat_data['phase_number'], mat_data['emod'] * 1e9)
            self.mapdl.mp("prxy", mat_data['phase_number'], mat_data['pois'])
        
        # dictionary for storing simulation results
        res = {'sigma': {}, 'epsilon': {}, 'v_phase': None}
       
        # Simulate deformation in six principle directions
        self.mapdl.save("work", "db", "")
        for ifx in range(1, 7):
            self.logger.debug(f" load step = {ifx}")

            # resume from blank db for next simulation
            self.mapdl.resume("work", "db")
            
            delver = L * options['boundary_nodes_selection_tolerance']  # tolerance for selection of boundary nodes
            delrot = options['delrot_factor'] * L    # Shear strain     # TODO use L_vx instead
            delshi = options['delshi_factor'] * L    # Tensile strain   # TODO use L_vz instead
            
            # *** SET LOADS ***
            self.mapdl.prep7()
            self.mapdl.lsclear("all")  # delete all boundary conditions

            if ifx % 3 == 1:
                axes = ['x', 'y', 'z']
            elif ifx % 3 == 2:
                axes = ['z', 'x', 'y']
            elif ifx % 3 == 0:
                axes = ['y', 'z', 'x']

            self.mapdl.allsel("all")
            self.mapdl.finish()
            self.mapdl.run("/solu")

            if ifx < 4:
                # Innere Ebenen auf Verschiebung 0 setzen
                for ax in axes:
                    self.mapdl.allsel("all")
                    self.mapdl.nsel("s", "loc", ax, -delver, delver)
                    self.mapdl.d("all", "u" + ax, 0)
                
                # Knoten auf den Aussenebenen axes[0] = L und axes[1] = 0 in Richtungen senkrecht
                # zur Zugspannung koppeln (zwangsweise gleiche Verschiebung)
                for i, ax in enumerate([axes[0], axes[1]], start=2):
                    self.mapdl.allsel("all")
                    self.mapdl.nsel("s", "loc", ax, L-delver, L+delver)
                    self.mapdl.cp(i, "u" + ax, "all")

                # tensile strain
                self.mapdl.allsel("all")
                self.mapdl.nsel("s", "LOC", axes[2], L-delver, L+delver)
                self.mapdl.d("all", "u" + axes[2], delshi)
            else:
                vx, vy, vz = axes
                # simple shear auf vy=0 und vy=l Ebenen,
                # tensile strain auf vz=0 und vz=l Ebenen
                # Aussenflaechen auswaehlen und Verschiebung setzen
                self.mapdl.nsel("s", "ext")
                self.mapdl.d("all", f"u{vz}", 0)                    # 'z'-Komponente fuer alle Aussenflaechen fixieren	 
                self.mapdl.nsel("r", "LOC", vy, -delver, delver)    #  Innenflaeche ('y'=0) auswaehlen
                self.mapdl.d("all", "u" + vx, 0)                    #  'x'-Komponente dieser Flaeche fixieren
                self.mapdl.allsel("all")
                self.mapdl.nsel("s", "ext")
                self.mapdl.nsel("r", "LOC", vy, L-delver, L+delver) # Aussenflaeche ('y'=L) auswaehlen # TODO use L_vy
                self.mapdl.d("all", "u" + vx, delrot)               # 'x'-Komponente dieser Flaeche auf Verschiebung "delrot" fixieren
                self.mapdl.allsel("all")
                self.mapdl.nsel("s", "ext")
                self.mapdl.nsel("r", "LOC", vx, -delver, delver)    # Innenflaeche ('x'=0) auswaehlen
                self.mapdl.d("all", "u" + vy, 0)                    # 'y'-Komponente dieser Flaeche fixieren
                self.mapdl.allsel("all")
                self.mapdl.nsel("s", "ext")
                self.mapdl.nsel("r", "LOC", vx, L-delver, L+delver) # Aussenflaeche ('x'=L) auswaehlen
                self.mapdl.d("all", "u" + vy, 0)                    # 'y'-Komponente dieser Flaeche fixieren

            # *** SOLVE ***
            self.logger.debug("starting solve ...")
            self.mapdl.allsel()
            self.mapdl.run("/status,solu")
            self.mapdl.eqslv("jcg", options['solver_tolerance'])  #JCG solver
            self.mapdl.solve()
            self.mapdl.finish()
            self.logger.debug("solve finished!")
            
            # *** SET POSTPROCESSING ***
            self.logger.debug("starting postprocessing ...")
            self.mapdl.post1()
            v_RVE, v_phase = self._compute_phase_volumes(phase_mat_params.values())
            print("phase volumes: ", v_phase)
            
            sv_i = self.mapdl.get(entity="ssum", entnum=0, item1="item",
                                  it1num="sv")
            f_z = sv_i / L**3
            print("mean tensile strain: ", f_z)
            
            vis = ['x', 'y', 'z', 'xy', 'yz', 'xz']
            vvs = ['xx', 'yy', 'zz', 'xy', 'yz', 'xz']
            ees = {}
            ffs = {}
            for ni in range(6):
                self.mapdl.etable(f"e_el{ni}", "epel", vis[ni])    # component elastic strain  in x, y, z, xy, yz, xz
                self.mapdl.etable(f"s_el{ni}", "s", vis[ni])       # component stress          in x, y, z, xy, yz, xz
                self.mapdl.smult("ev_i", f"e_el{ni}", "e_vol")
                self.mapdl.smult("sv_i", f"s_el{ni}", "e_vol")
                self.mapdl.ssum()
                e_ni = self.mapdl.get(entity="ssum", entnum=0, item1="item",
                                      it1num="ev_i")
                s_ni = self.mapdl.get(entity="ssum", entnum=0, item1="item",
                                      it1num="sv_i")
                
                ees[vvs[ni]] = e_ni / v_RVE * 1000
                ffs[vvs[ni]] = s_ni / v_RVE * 1e-6

                self.mapdl.etable("ev_i", "eras")
                self.mapdl.etable("sv_i", "eras")
            self.mapdl.etable("eras")

            # record simulation results in dictionary
            res['sigma'][ifx] = ffs            
            res['epsilon'][ifx] = ees
            if res['v_phase'] is None:
                res['v_phase'] = v_phase
                
            self.logger.debug("postprocessing finished!")
            self.logger.debug(f"resulting elasticity from load step {ifx}: "\
                             f"e = {ees}, f = {ffs}")


            self.mapdl.save("sol6_elc", "db", "")
        
        self.logger.info("finished simulation of elasticity. ")
            
        # compute stiffness tensor and elastic constants
        self.logger.info("computing stiffness tensor and elastic constants.")
        
        C, svd_ratio = compute_stiffness_matrix_svd(res['epsilon'].values(), 
                                                    res['sigma'].values())
        res['stiffness_tensor'] = C
        res['svd_ratio'] = svd_ratio
        res['voigt_avg'] = voigt_average(C)
        res['reuss_avg'] = reuss_average(C)
        res['hill_avg'] = hill_average(C)
        
        self.logger.info(f"result = {res}")

        return res
           
class ThermalStressSimulator(Simulator):
    default_options = {
                       'solver_tolerance': 1e-08,
                        'boundary_nodes_selection_tolerance': 0.005,
                        't_room': 25,
                        't_solid': 800
                        }
    
    def simulate(self, db_file, params={}, options={}):
        """Simulate the coefficient of thermal expansion and the corresponding
        thermal stresses in the RVE.
        
        Parameters
        ----------
        db_file : TYPE
            DESCRIPTION.
        params : TYPE, optional
            DESCRIPTION. The default is {}.
        options : dictionary, optional
            Dictionary for controlling various aspects of the simulations. 
            
            t_room = 'Einsatztemperatur', für die die thermischen Spannungen berechnet werden
            t_solid = Temperatur, bei der (bei Aufheizen von Raumtemp.) die Streckgrenze von Cobalt erreicht wird bzw. Beginn des elastischen Verhaltens

            
            The default is {}.

        Returns
        -------
        None.

        """
        self._setup_sim(db_file, options)
        
        # *** Definition of material parameters ***
        for phase_name, mat_data in params.items():
            # *** Attribute material to different phases ***
            self.mapdl.mp("ex", mat_data['phase_number'], mat_data['emod'] * 1e9)
            self.mapdl.mp("prxy", mat_data['phase_number'], mat_data['pois'])
            
            # coefficient of thermal expansion
            self.mapdl.mp("alpx", mat_data['phase_number'], mat_data['cte'] *1e-6)
                   

        # *** SET LOADS ***
        self.mapdl.lsclear("all")  #Löscht alle vorhandenen Randbedingungen
        
        # Stringvariable für Koordinatenrichtungen einführen
        v1, v2, v3 = 'x', 'y', 'z'
        vx, vy, vz = 'x', 'y', 'z'

        if 'L' in self.mapdl.parameters._parm:
                # get length of RVE in current axis from the database
                L = self.mapdl.parameters['L']
        else:
            if len(set([self.mapdl.parameters[d] for d in ['Lx', 'Ly', 'Lz']])) == 1:    
                # dimensions are the same in all 3 axis, so we can just use
                # length of RVE in x axis
                L = self.mapdl.parameters['Lx'] 
            else:
                raise NotImplementedError("The loaded mesh has different dimension in x, y, and z. This case is not implemented yet.")
        delver = L * options['boundary_nodes_selection_tolerance']  # tolerance for selection of boundary nodes

        self.mapdl.allsel("all")
        self.mapdl.finish()
        self.mapdl.run("/solu")
        
        # * Temperaturdifferenz setzen
        self.mapdl.tunif(options['t_room'])  # final temperature
        self.mapdl.tref(options['t_solid'])  # initial temperature
        if options['t_room'] < options['t_solid']:
            for phase_name, mat_data in params.items():
                self.mapdl.mpamod(mat_data['phase_number'], options['t_room'])  #nötig, wenn Endtemperatur kleiner als TREF ist
            
        # Innere Ebenen auf Verschiebung 0 setzen
        for ax in ['x', 'y', 'z']:
            self.mapdl.allsel("all")
            self.mapdl.nsel("s", "loc", ax, -delver, delver)
            self.mapdl.d("all", "u" + ax, 0)
        
        # Äußere Ebenen koppeln
        for i, ax in enumerate(['x', 'y', 'z'], start=1):
            self.mapdl.allsel("all")
            self.mapdl.nsel("s", "loc", ax, L-delver, L+delver)
            self.mapdl.cp(i, "u" + ax, "all")

        
        # *** SOLVE ***
        self.mapdl.allsel("all")
        self.mapdl.run("solcontrol,on")
        self.mapdl.nsubst(1)
        self.mapdl.eqslv("jcg", options['solver_tolerance'])
        self.mapdl.run("/status,solu")
        self.mapdl.solve()
        self.mapdl.finish()
        self.mapdl.post1()

        # *** SET POSTPROCESSING ***
        v_RVE, v_phase = self._compute_phase_volumes(params.values())
        print("phase volumes: ", v_phase)

        # *** thermal expansion coefficient ***
        ctes = {}
        for axis in ['z', 'y', 'x']:
            self.mapdl.allsel("all")
            self.mapdl.nsel("r", "loc", axis, L-delver, L+delver)   # TODO: check if we need L or l here (originally it was l...). Same 3 lines below.
            self.mapdl.nsort("u", axis)
            #self.mapdl.run(f"*get,wak,sort,,max")
            wak = self.mapdl.get(entity="sort", item1="max")
            ctes[axis] = wak / (L * (options['t_solid'] - options['t_room']))
        
        # *** thermal stresses ***
        self._output_thermal_stresses_nodes(L, params)
        self._output_thermal_stresses_elements(L, params, 'principal')       
        self._output_thermal_stresses_elements(L, params, 'equivalent')

        self.mapdl.save("sol_ths", "db", "", "", "")
        self.mapdl.exit()
        
    def _output_thermal_stresses_nodes(self, L, params):
        """Output of the calculated thermal stresses for all nodes for 
        subsequent statistical evaluation with Origin
    
        Parameters
        ----------
        L : float
            Size of the RVE (in meters).
        params : dict
            Dictionary with phase numbers.

        Returns
        -------
        None.

        """
        self.mapdl.nsel("all")
        self.mapdl.run("*get,nmin,node,0,num,min")
        self.mapdl.run("*get,nmax,node,0,num,max")
        nmin = int(self.mapdl.parameters['nmin'])
        nmax = int(self.mapdl.parameters['nmax'])

        d_rand = L/50
        
        for phase_name, mat_data in params.items():
            # select all elements corresponding to a material (identified by 
            # the phase number)
            self.mapdl.esel("s", "mat", "", mat_data['phase_number'])
            self.mapdl.nsle("s", "active", "")
            
            # remove elements at the RVE boundary from the selection
            for ax in ['x', 'y', 'z']:
                self.mapdl.esel("u", "loc", ax, 0, d_rand)
                self.mapdl.esel("u", "loc", ax, L-d_rand, L)
            self.mapdl.run(f"/output,testmat{mat_data['phase_number']},out,,append,")
            data = {}
            # TODO improve speed of data retrival
            for ni in range(nmin, nmax):
                # get principal stresses and component stresses
                d = []
                for scp in [1, 2, 3, 'x', 'y', 'z']:
                    d.append(self.mapdl.get("v,s{scp},node,{ni},s,{scp}"))
                data[ni] = np.array(d)
            return data
        
    def _output_thermal_stresses_elements(self, L, params, mode='principal'):
        """Output calculated thermal stresses for all elements 
        for subsequent statistical analysis with Origin.
        
        The volume of the elements is also output to allow for volume 
        weighting of the stresses.
        

        Parameters
        ----------
        L : float
            Size of the RVE (in meters).
        params : dict
            Dictionary with phase numbers.
        mode : str
            Output mode for thermal stresses. Possible values are ``'principal'``
            and ``'equivalent'``.
            The default is ``'principal'``.
        """
        if not mode in ['principal', 'equivalent']:
            raise ValueError("Invalid mode for element stress calculation. "\
                             "Valid modes are 'principal', 'equivalent'.")
        
        d_rand = L/100
        for phase_name, mat_data in params.items():
            # select all elements corresponding to a material (identified by 
            # the phase number)
            self.mapdl.esel("s", "mat", "", mat_data['phase_number'])
            
            # remove elements at the RVE boundary from the selection
            for ax in ['x', 'y', 'z']:
                self.mapdl.esel("u", "cent", ax, 0, d_rand)
                self.mapdl.esel("u", "cent", ax, L-d_rand, L)
    
            if mode == 'principal':
                # get principal stresses for all selected elements
                for i in range(1,4):
                    self.mapdl.etable(f"th_s{i}", "S", i, "avg")
            elif mode == 'equivalent':
                # get equivalent stresses
                self.mapdl.etable(f"eqv_s", "S", 'eqv', "avg")
                
            # get volume for all selected elements
            self.mapdl.etable("vol_el", "volu", "", "")

            # output the obtained volume and thermal stresses to file            
            if mode == 'principal':
                self.mapdl.run(f"/output,elem_mat{mat_data['phase_number']},out,,append,")
                self.mapdl.run("/page,,,-1")
                self.mapdl.pretab("vol_el", "th_s1", "th_s2", "th_s3")
            elif mode == 'equivalent':
                self.mapdl.run(f"/output,elem_mat{mat_data['phase_number']}_eqv,out,,append,")
                self.mapdl.run("/page,,,-1")
                self.mapdl.pretab("vol_el", "eqv_s")
            self.mapdl.run("/output,term")
            self.mapdl.etable("eras")
    
        
