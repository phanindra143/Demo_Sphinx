# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 09:04:29 2020

@author: pirkelma
"""
import sys
import re
import subprocess
import logging
from MPaut.pyqtgraph_voxel_visualization import view_RVE
from pathlib import Path
import os

logging.basicConfig(format=None, datefmt=None)

class GeoVal_Communicator:
    """Class for communicating with ``GeoVal`` from python.
    
    Objects of this class will start ``GeoVal`` as a subprocess and allow to 
    control it from within python. This enables the creation of representative 
    volume elements (RVEs) programatically by calling most of GeoVal's object 
    and voxel operations in a python script.
    
    This way it becomes possible to generate large numbers of RVEs automatically
    e.g. for parameter studies or to generate RVEs with specific properties
    which would take long to create by hand using the GUI.
    """
    valid_object_types = ['sphere', 'tube', 'prism', 'voronoi_polyeder', 
                          'platonic_solid', 'fibre']
    type_dict = {t : i for i, t in enumerate(valid_object_types, 1)}
    default_shape_descriptors = {
        'sphere': {'radius': 5.0e-6},
        'tube': {'radius': 5.0e-6, 'length': 20.0e-6, 'inner_radius': 3.0e-6},
        'prism': {'edge_length': 5.0e-6, 'thickness': 5.0e-6, 'n_edges': 4},
        'voronoi_polyeder': {'radius': 5.0e-6},
        'platonic_solid': {'edge_length': 10.0e-6, 'variation': 5.0e-6, 'n_faces': 6},
        'fibre': {'radius': 10.0e-6, 'shell': 1.0e-6},
        }
       
    def __init__(self, executable='geo_val.exe', output_folder='output',
                 debug_output=True):        
        """Create communicator for programatically controlling GeoVal.
        
        This will create a python object which can be used to generate 
        representative volume elements (RVEs) from within python.

        Parameters
        ----------
        executable : str, optional
            Path to the GeoVal executable. The default is ``'geo_val.exe'``.
        output_folder : str, optional
            Folder where created files will be stored. The default is ``'output'``.
        debug_output : bool, optional
            Indicates whether or not the commands sent to GeoVal should be 
            logged in a debug file. The default is ``True``.

        """
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(exist_ok=True, parents=True)
        
        self.logger = logging.getLogger('GeoVal')
        self.logger.setLevel(logging.DEBUG)
        self.log_fh = logging.FileHandler(self.output_folder / 'geoval_automation.log', mode='w')
        self.log_fh.setLevel(logging.INFO)
        self.logger.addHandler(self.log_fh)

        executable_path = Path(executable)
        if executable_path.exists():
            # start process and open communication pipes        
            self.process = subprocess.Popen([executable, '--cmdline'], stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE, 
                                            stdin=subprocess.PIPE)
        else:
            raise FileNotFoundError(f"error: GeoVal executable could not be found at: {executable_path.absolute()}")
        
        if debug_output:
            debug_output_file = 'debug.pro'
            path = self.output_folder / debug_output_file
            if not path.parent.exists():
                path.parent.mkdir(parents=True)
            self.debug_output_file = path
            # clear existing data in debug output file
            self.debug_output_file.write_text('')
        else:
            self.debug_output_file = None
            
        self.rve_dims = None
        self.voxel_size = None
        
    def set_randseed(self, seed):
        """Set the seed for GeoVals random number generator.
        
        This is useful for generating deterministic RVEs.

        Parameters
        ----------
        seed : int
            Random seed for the GeoVals RNG.

        """
        self.logger.info(f"Setting random seed {seed}")
        self.__process_cmds([f"do_set_randseed: {seed}"])
           
    def __send_cmd(self, cmd):
        if self.debug_output_file is not None:
            with self.debug_output_file.open("a") as f:
                f.write("{} \n".format(cmd))
                
        self.process.stdin.write("{} \n".format(cmd).encode())
        self.process.stdin.flush()
        
    def __read_output(self):
        output = ""
        for line in iter(self.process.stdout.readline, b''):
            # if "Unknown command!" in line.decode():
            #     raise Exception("Error: an unknown command was passed to the \
            #                     script. Please investigate!")
            output += line.decode()
            if line.strip().decode() == 'done':
                    break
        return output
        
    def __process_cmds(self, cmds):     
        # send commands to the process
        for cmd in cmds:    
            self.__send_cmd(cmd.strip())
        
        # wait for the processing to finish
        if len(cmds) > 0:
            return self.__wait_for_cmd_completion()
        else:
            print("warning: no commands entered!")
            return ""
        
    def __wait_for_cmd_completion(self):
        # wait for command to finish and return the output
        return self.__read_output()
    
    def _get_shape_params(self, object_type, shape_description):
        # define parameters describing the introduced objects
        shape_param_1 = 0
        shape_param_2 = 0
        shape_param_3 = 0
        shape_description = shape_description.copy()
        descriptors = set(shape_description.keys())
        valid_descriptors = set(GeoVal_Communicator.default_shape_descriptors[object_type].keys())
        if not descriptors.issubset(valid_descriptors): # shape description parameters passed that do not match the ones needed for the given object type
            raise ValueError(f"Invalid shape descriptors '{descriptors}' for objects of type '{object_type}'. Valid descriptors are {valid_descriptors}")
        else:
            # fill in missing shape description parameters with default values
            for param in valid_descriptors - descriptors:
                shape_description[param] = GeoVal_Communicator.default_shape_descriptors[object_type][param]

        if object_type == 'sphere':
            shape_param_1 = shape_description['radius']
        elif object_type == 'tube':
            shape_param_1 = shape_description['radius']     # radius
            shape_param_2 = shape_description['length']     # length
            shape_param_3 = shape_description['inner_radius']      # inner radius
        elif object_type == 'prism':
            shape_param_1 = shape_description['edge_length']     # edge length
            shape_param_2 = shape_description['thickness']     # thickness
            shape_param_3 = shape_description['n_edges']      # number of edges
        elif object_type == 'voronoi_polyeder':
            shape_param_1 = shape_description['radius']
        elif object_type == 'platonic_solid':
            shape_param_1 = shape_description['edge_length']
            shape_param_2 = shape_description['variation']
            if shape_description['n_faces'] not in [4, 6, 8, 12, 20]:
                raise ValueError("Invalid number of faces for platonic solid. Possible values are [4, 6, 8, 12, 20].")
            else:
                # we need to multiply by 1e-6 because GeoVal assumes the input 
                # is in um and internally multiplies the value by 1e6 to set 
                # number of faces
                shape_param_3 = shape_description['n_faces'] * 1e-6
        elif object_type == 'fibre':
            shape_param_1 = shape_description['radius']
            shape_param_2 = shape_description['shell']
            
        return shape_param_1, shape_param_2, shape_param_3
        
    def initialize_rve(self, rve_dims=64, voxel_size_um=1.0, z_multiplier=1.0):
        """Initialize the RVE. 
        
        You can specify the dimensions of the RVE and the size of the voxels.

        Parameters
        ----------
        rve_dims : int, optional
            Dimensions of the RVE. The default is ``64``.
        
        voxel_size : float, optional
            Size of the voxels of the RVE in um. The default is ``1.0``.
            
        z_multiplier : float, optional
            Multiplier for creating RVEs with more or fewer voxels in the 
            z-axis.
            The default is ``1.0``, which creates a cubical RVE (same number 
            of voxels in x, y and z).

        """
        self.rve_dims = rve_dims
        self.voxel_size = voxel_size_um
                
        cmds = f""" Setting:  0 1
                    Setting:  1 0
                    Setting:  2 1
                    Setting:  3 1
                    Setting:  4 1
                    do_initialize: 
                    set_sc:  {self.voxel_size}
                    set_nnm: 1 {self.rve_dims}
                    set_nnm: 2 {self.rve_dims}
                    set_nnm: 3 {int(self.rve_dims*z_multiplier)}
                    """
        self.__process_cmds(cmds.split('\n'))
        
    def introduce_objects(self, N=10, object_type='sphere', shape_description={},
                          number_of_cuts=0, distribution='gauss',
                          randseed=None):
        """Add new objects to the RVE.
        
        Create new objects of the given object type in the RVE. You can specify
        the number of objects added as well as a shape description for the 
        objects.
        It is also possible to pass a seed for the random number generator 
        (this can be used to ensure reproducibility of the RVE generation).

        Parameters
        ----------
        N : integer, optional
            Number of objects introduced. 
            
            The default is ``10``.
        object_type : string, optional
            Type of objects introduced. Possible values are ``'sphere'``, 
            ``'tube'``, ``'prism'`` and ``'voronoi_polyeder'``.
            
            The default is ``'sphere'``.
        shape_description : dict, optional
            Specifies properties of the introduced objects.
            
            - For ``'sphere'`` it defines the radius, e.g. ``{'radius': 5.0e-6}``
            - For ``'tube'`` it defines radius, length, and inner radius, e.g. 
              ``{'radius': 5.0e-6, 'length': 20.0e-6, 'inner_radius': 3.0e-6}``
            - For ``'prism'`` it defines edge length, thickness, and number of edges, 
              e.g. ``{'edge_length': 5.0e-6, 'thickness': 5.0e-6, 'n_edges': 4}``
            - For ``'voronoi_polyeder'`` it defines the radius of the spheres used in
              the creation of the voronoi polyeders, e.g. ``{'radius': 5.0e-6}``
            - For ``'platonic_solid'`` it defines edge length, variation of the 
              edge length, and number of faces of the platonic solid, 
              e.g. ``{'edge_length': 10.0e-6, 'variation': 5.0e-6, 'n_faces': 6}``.
              Allowed values for ``'n_faces'`` are ``4, 6, 8, 12, 20``.
            - For ``'fibre'`` it defines radius and shell of the fibre.
              e.g. ``{'radius': 10.0e-6, 'shell': 1.0e-6}``.
            
            If a ``shape_description`` is not specified the defaults from the 
            above examples are used.
        number_of_cuts : integer, optional
            Cuts away parts of each introduced object, setting only the voxels
            remaining after the cut. Up to two cuts are possible, so valid 
            values are ``0``, ``1`` or ``2``.
            
            The default is ``0``, which means no cuts are performed.  
        distribution : string, optional
            Random distribution used for generating object positions/sizes.
            Possible values are ``'gauss'``, ``'log_normal'``. 
            
            The default is ``'gauss'``.
        randseed : integer, optional
            Set a random seed before introducing objects. This is parameter was
            added for convenience and essentially does the same as calling 
            :func:`~MPaut.geoval_subprocess.GeoVal_Communicator.set_randseed`
            immediately before introducing new objects.

            
        .. warning::
            Due to limitations in ``GeoVal``, it is only possible to introduce objects 
            of a given type at most *four* times. This means you can call 
            ``introduce_objects(...)`` a maximum of four times for each ``object_type``, 
            independent of the number of objects introduced in each call.
            
            At the moment no check is performed, so you have to keep track of the 
            number of calls yourself.
        """
        """
        set_pobjec: 1  1.30000000000000E+0001  # number of objects
        set_pobjec: 30  0.00000000000000E+0000  # std dev ???
        set_pobjec: 2  1.00000000000000E+0000  # object type (1 = sphere, 2 = tube, 3 = prism, ...)
        set_pobjec: 3  0.00000000000000E+0000  # center position (random, random_sel, ...) ???
        set_pobjec: 4  3.00000000000000E+0000  # phase number
        set_pobjec: 5  0.00000000000000E+0000  # distribution (gauss, log-normal, file)
        set_pobjec: 6  7.00000000000000E-0006  # radius (sphere, tube)
        set_pobjec: 7  0.00000000000000E+0000  # length (tube)
        set_pobjec: 8  0.00000000000000E+0000  # inner radius (tube)
        set_pobjec: 9  0.00000000000000E+0000  # number of cuts
        set_pobjec: 10  1.00000000000000E+0000 # multiplier x orientation
        set_pobjec: 11  1.00000000000000E+0000 # multiplier y orientation
        set_pobjec: 12  0.00000000000000E+0000 # ???
        do_setvoxel: 
        do_intro_objects: 
            """
        if not object_type in set(GeoVal_Communicator.valid_object_types):
            raise ValueError(f"Invalid object type '{object_type}'. Possible object types are {set(GeoVal_Communicator.type_dict.keys())}")
            
        if not number_of_cuts in [0,1,2]:
            raise ValueError("Invalid number of cuts specified. Possible values are 0, 1 or 2.")
            
        if distribution == 'gauss':
            dist = 0
        elif distribution == 'log_normal':
            dist = 1
        else:
            raise ValueError("Random distributions other than 'gauss' and 'log_normal' are not supported yet!")
            
        self.logger.info(f"Introducing {N} objects of type {object_type}")
        
        cmds = ""
        if self.rve_dims is None or self.voxel_size is None:
            # if the RVE has not been initialized we initialize it with the default settings
            self.initialize_rve()
            
        if randseed is not None:
            self.set_randseed(randseed)
     
        type_id = GeoVal_Communicator.type_dict[object_type]
        
        sp1, sp2, sp3 = self._get_shape_params(object_type, shape_description)
        
        cmds = cmds + f"""set_pobjec: 1  {N}
                    set_pobjec: 30   0
                    set_pobjec: 2  {type_id}
                    set_pobjec: 3  0.00000000000000E+0000
                    set_pobjec: 5  {dist}
                    set_pobjec: 6  {sp1}
                    set_pobjec: 7  {sp2}
                    set_pobjec: 8  {sp3}
                    set_pobjec: 9  {number_of_cuts}
                    set_pobjec: 10  1.00000000000000E+0000
                    set_pobjec: 11  1.00000000000000E+0000
                    set_pobjec: 12  0.00000000000000E+0000
                    do_setvoxel: 
                    do_intro_objects:  """
        self.__process_cmds(cmds.split('\n'))

    def split_objects(self, phase, fraction=0.5):
        """Split a fraction of the objects of a given phase into a new phase.
        
        Parameters
        ----------
        phase : integer
            Number of the phase for which objects will be split.
        fraction : float, optional
            Fraction of objects that remain in the old phase. 
            Possible values are ``0 &lt fraction &lt 1``. The default is 
            ``0.5`` which means half of the objects are assigned to the new 
            phase.

        """
        if not 0.0 < fraction < 1.0:
            raise ValueError("Split fraction needs to be between 0 and 1!")
        else:
            fraction *= 100.0    # GeoVal wants percentage so we multiply by 10
            
        # voxel analysis to get current phases
        phase_volume_dict = self.get_volume_fractions()
        if not phase in phase_volume_dict.keys():
            raise ValueError(f"Cannot split objects because there are no voxels of phase {phase} in the RVE")
                
        # apply the split
        cmds = f"""  do_splitobjec: {phase} {fraction}
                    do_setvoxel:"""

        self.__process_cmds(cmds.split('\n'))
        
    def transform_objects(self, object_count, object_phase, new_object_type, 
                          shape_description={}):
        """Transform a number of objects of a given phase to objects of a new type.
        
        You must specify the phase and the number of objects to transform, as 
        well as the new type for transformed objects. 
        You can also set the shape properties for the transformed object using
        the ``shape_description`` (see the documentation of 
        :func:`~MPaut.geoval_subprocess.GeoVal_Communicator.introduce_objects` 
        for a detailed explanation of this parameter)

        Parameters
        ----------
        object_count : integer
            Number of objects that will be transformed.
        object_phase : integer
            Phase of the transformed objects.
        new_object_type : string
            Type of target objects after transformation. 
            Possible values are ``'sphere'``, ``'tube'``, ``'prism'`` and 
            ``'voronoi_polyeder'``.
        shape_description : dict
            Specifies shape properties of the transformed objects.
            For a detailed description see: :func:`~MPaut.geoval_subprocess.GeoVal_Communicator.introduce_objects`
        """
        
        new_object_type_id = GeoVal_Communicator.type_dict[new_object_type]
        
        if not object_phase in self.get_volume_fractions().keys():
            raise ValueError(f"There are no objects of phase {object_phase} to transform.")
            
        sp1, sp2, sp3 = self._get_shape_params(new_object_type, shape_description)

        cmds = f"""  set_pobjec: 1  {object_count}
                    set_pobjec: 30  0.00000000000000E+0000
                    set_pobjec: 2  {new_object_type_id}
                    set_pobjec: 3  0.00000000000000E+0000
                    set_pobjec: 4  {object_phase}
                    set_pobjec: 5  0.00000000000000E+0000
                    set_pobjec: 6  {sp1}
                    set_pobjec: 7  {sp2}
                    set_pobjec: 8  {sp3}
                    set_pobjec: 9  0.00000000000000E+0000
                    set_pobjec: 10  1.00000000000000E+0000
                    set_pobjec: 11  1.00000000000000E+0000
                    set_pobjec: 12  0.00000000000000E+0000
                    do_setvoxel: 
                    do_transform_objects: """
        self.__process_cmds(cmds.split('\n'))
        
    def set_overlap(self, overlap_priorities):
        """Sets overlap priority for each phase.
        
        You can specify a priority for each phase present in the current RVE.
        This will determine to which phase voxels will be assigned if they are
        in overlapping regions of multiple objects.
        A lower priority means that this phase will have precedence for voxel
        assignment.
        
        If the priority for two phases is equal, a tie-breaker rule will 
        determine the assignment. Currently, there are four different rules:
            
            - ``'random'``: assignment of voxels to a phase is determined randomly 
              for each object of the phases. All of the contested voxels will 
              be assigned to one of the objects.
            - ``'voronoi'``: assignment of the voxels happens based on the voronoi
              distance to the center of the objects. This means a voxel will be
              assigned to the phase of the object closest to the voxel.
            - ``'interface'``: **TODO: UNDOCUMENTED**
            - ``'shared'``: **TODO: UNDOCUMENTED**

        Parameters
        ----------
        overlap_priorities : dict
            Dictionary with phase numbers as keys and a tuple of priority + 
            tie-break-rule as values, e.g.
            ``overlap_priorities = {1: (1, 'voronoi'), 7: (0, 'random')}``
            
            The phase number must be a valid number of voxels currently present
            in the RVE. The priority must be an integer >= 0 and the 
            tie-breaker-rule can be any of ``'shared', 'random', 'interface', 
            'voronoi'`` (see above).
            
        """       
        # voxel analysis to get current phases
        phase_volume_dict = self.get_volume_fractions()
        valid_phases = set(phase_volume_dict.keys())
        given_phases = set(overlap_priorities.keys())
        # make sure only existing phases are specified
        if not given_phases.issubset(valid_phases):
            raise ValueError(f"Cannot set priorities because there are no voxels of phase {given_phases - valid_phases} in the RVE")

        overlap_tie_breakers = {'shared': 0, 
                                'random': 1, 
                                'interface': 2, 
                                'voronoi': 3}     
        
        for p, prio in overlap_priorities.items():
            if not (type(prio) == tuple and len(prio) == 2):
                raise ValueError(f"Invalid format for overlap priority of phase {p}. "\
                                 "Expected format is (<priority>, <tie-break-rule>), "\
                                 "where <priority> is an integer >= 0 and "\
                                 "<tie-breaker-rule> is one of "\
                                 f"{list(overlap_tie_breakers.keys())}. "\
                                 f"Got '{prio}'.")
            if not (type(prio[0]) == int and prio[0] >= 0):
                raise ValueError(f"Invalid overlap priority for phase {p}. "\
                                 "Priority must be an integer >= 0. "\
                                 f"Got {prio[0]}.")
            if not (type(prio[1]) == str and prio[1] in overlap_tie_breakers.keys()):
                raise ValueError("Invalid overlap tie-breaker rule for "\
                                 f"phase {p}. Valid tie-breaker rules are "\
                                 f"{list(overlap_tie_breakers.keys())}. "\
                                 f"Got '{prio[1]}'.""")
    
        
        for phase, prio_def in overlap_priorities.items():
            prio = 10 * prio_def[0] + overlap_tie_breakers[prio_def[1]]
            cmd = f"set_ovlap: {phase} {prio}"
            self.__process_cmds([cmd])
        cmd = "do_setvoxel: \n"
        self.__send_cmd(cmd)
        

    def end_communication(self):
        """Terminate the communication with the GeoVal process. 
        
        This will hand back control of GeoVal back to the GUI. 
        Note that any changes to the RVE made from the GUI will not be 
        reflected in python.

        """
        self.__send_cmd("quit\n")
    
    def close(self):
        """
        Quits the GeoVal program.
        """
        self.process.kill()

    def distribute(self):
        """Distribute the objects in the RVE by applying repulsion."""
        self.logger.info("Distributing objects")
        
        electrostatic_repulsion = 0
        variation_electrostatic_repulsion = 1
        hard_sphere_repulsion = 1
        variation_hard_sphere_repulsion = 1
        power_law_exponent = 1
        cluster_type = 0
        number_of_clusters = 0
        cluster_size_um = 2.0e-5
        variation_cluster_size_um = 0
        displacement_percentage_cluster_size = 40.0
        fraction_displaced_particles_percentage = 100.0
        sedimentation = 0
        variation_sedimentation = 0
        number_of_neighbors = 3
        distance_law_exponent = 1.0
        density_limit = 0.0
        cmds = f""" set_pobjec: 1  {electrostatic_repulsion}
                    set_pobjec: 11  {variation_electrostatic_repulsion}
                    set_pobjec: 2  {hard_sphere_repulsion}
                    set_pobjec: 12  {variation_hard_sphere_repulsion}
                    set_pobjec: 3  {power_law_exponent}
                    set_pobjec: 4  {cluster_type}
                    set_pobjec: 5  {number_of_clusters}
                    set_pobjec: 6  {cluster_size_um}
                    set_pobjec: 16  {variation_cluster_size_um}
                    set_pobjec: 7  {displacement_percentage_cluster_size}
                    set_pobjec: 8  {fraction_displaced_particles_percentage}
                    set_pobjec: 9  {sedimentation}
                    set_pobjec: 10  {variation_sedimentation}
                    do_setvoxel: 
                    do_distribute_objects: {number_of_neighbors} {distance_law_exponent} {density_limit}"""
        self.__process_cmds(cmds.split('\n'))
            
    def get_volume_fractions(self):
        """
        Get the voxel volume fractions for all the phases in the RVE.

        Returns
        -------
        phase_volume_dict : dict
            contains as keys the phase number and as values the corresponding volume 
            fraction between 0.0 and 1.0
        """
        output = self.__process_cmds(["do_voxel_analysis:"])
            
        phase_volume_dict = {}
        
        rx = re.compile("Volume fraction (?P<phase_id>\\d+)\\s+(?P<volume>\\d*\\.?\\d+)\\s*")
        match_res = rx.finditer(output)
        
        # parse output for volume information
        for m in match_res:
            phase = int(m['phase_id'])
            phase_volume_dict[phase] = float(m['volume'])
        
        return phase_volume_dict
    
    def get_object_analysis(self):
        """
        Get analysis of objects in the current RVE.

        Returns
        -------
        phase_object_dict : dict
            contains as keys the phase number and as values information (such
            as number of objects, object shape descriptors, etc.) about the 
            objects of the given phase in the RVE
        """
        output = self.__process_cmds(["do_object_analysis:"])
        
        float_re = r"([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)"
        
        # search for blocks of object information
        object_block = r"Number of objects type (?P<object_type>[A-Z_]+) :\s*(?P<object_count>\d+)\s+\(Phase number:(?P<phase_number>\d+)\)\s*(?P<object_info>(\n\S+ of object type .+$)+)"
        rx = re.compile(object_block, re.MULTILINE)
        match_res = rx.finditer(output)
        
        phase_object_dict = {}
        # parse each object information block and extract parameters
        for m in match_res:
            current_object_info = {}
            current_object_info['object_type'] = m['object_type'].lower()
            current_object_info['object_count'] = int(m['object_count'])
            phase_number = int(m['phase_number'])
            object_info = m['object_info']
            
            subrx = re.compile(r"(?P<descriptor>\S+) of object type {0} :\s*(?P<mean>{1}) \+- (?P<variance>{1})".format(m['object_type'], float_re), re.MULTILINE)
            submatch_res = subrx.finditer(object_info)
            params = {}
            for subm in submatch_res:
                params[subm['descriptor'].lower()] = {'mean': float(subm['mean']), 
                                                      'variance': float(subm['variance'])} 
            current_object_info['shape_params'] = params
            phase_object_dict[phase_number] = current_object_info
        
        return phase_object_dict
    
    def get_chord_length_analysis(self):
        """Runs chord length analysis for the current RVE.
        
        Returns
        -------
        res : dict
            Dictionary containing result of the chord length analysis.
            The analysis computes the mean and variance of the chord lengths of 
            all particles of every phase of the RVE, the volume and interface 
            fractions and the interface per volume.

        """
        output = self.__process_cmds(["do_chord_length_analysis:"])
        
        float_re = r"([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)"
        # search for blocks of chord length information
        chord_analysis_block = r"Number particles (?P<phase>\d+):\s*(?P<particle_count>\d+)\s*\nVolume fraction \1 \(Chord lengths\):\s*(?P<volume_fraction>{0})\s*\nMean chord length \1 in um:\s*(?P<mean>{0}) \+- (?P<variance>{0})".format(float_re)
        rx = re.compile(chord_analysis_block, re.MULTILINE)
        match_res = rx.finditer(output)
        
        res = {}
        
        phase_chord_dict = {}
        for m in match_res:
            chord_info = {}
            chord_info['volume_fraction'] = float(m['volume_fraction'])
            chord_info['mean_chord_length'] = float(m['mean']) * 1e-6
            chord_info['variance'] = float(m['variance']) * 1e-6
            chord_info['particle_count'] = int(m['particle_count'])
            phase_chord_dict[int(m['phase'])] = chord_info
        res['phase_chord_lengths'] = phase_chord_dict
            
        interface_analysis_block = r"Interface fraction (?P<phase_1>\d+)-(?P<phase_2>\d+) \(Chord lengths\):\s*(?P<interface_fraction>{0})".format(float_re)
        rx = re.compile(interface_analysis_block, re.MULTILINE)
        match_res = rx.finditer(output)
        
        interface_fraction_dict = {}
        for m in match_res:
            p1 = int(m['phase_1'])
            p2 = int(m['phase_2'])
            frac = float(m['interface_fraction'])
            interface_fraction_dict[(p1,p2)] = frac
        res['interface_fractions'] = interface_fraction_dict
        
        interface_per_volume = r"Interface/Volume in 1/um:\s*(?P<interface_per_volume>{0})".format(float_re)
        rx = re.compile(interface_per_volume, re.MULTILINE)
        m = rx.search(output)
        res['interface_per_volume_1/um'] = float(m['interface_per_volume'])
    
        return res
    
    def get_variance_analysis(self, mode='unscaled'):
        """Run variance analysis on the current RVE.

        Parameters
        ----------
        mode : str, optional
            Mode to use for the variance analysis. Possible values are
            ``'unscaled'``, ``'area_scaled'``, ``'fully_scaled'``.
            The default is ``'unscaled'``.

        Returns
        -------
        res : dict
            Dictionary containing the result of the variance analysis in the 
            following form:
                {'variance_<mode>_8': {<phase_0>: <variance_phase_0>,
                                       ...
                                       <phase_n>: <variance_phase_n>},
                 'variance_<mode>_16': {<phase_0>: <variance_phase_0>,
                                        ...
                                        <phase_n>: <variance_phase_n>},
                 'variance_<mode>_32': {<phase_0>: <variance_phase_0>,
                                        ...
                                        <phase_n>: <variance_phase_n>},
                 'porosity': {'min': <min_porosity_fraction>,
                              'max': <max_porosity_fraction>}
                 }
        """
        mode_ids = {'unscaled': 0, 'area_scaled': 1, 'fully_scaled': 2}
        
        if not mode in mode_ids:
            raise ValueError(f"Invalid mode for variance analysis. Possible modes are {set(mode_ids.keys())}")
            
        output = self.__process_cmds([f"do_variance_analysis: {mode_ids[mode]}"])
        
        float_re = r"([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)"
        variance_re = r".*ariance (?P<size>\d+)\s+um of phase (?P<phase>\d+):\s+(?P<variance>{0}).*".format(float_re)
        rx = re.compile(variance_re, re.MULTILINE)
        match_res = rx.finditer(output)
        
        res = {f'variance_{mode}_8': {}, f'variance_{mode}_16': {}, f'variance_{mode}_32': {}}
        
        for m in match_res:
            size = int(m['size'])
            phase = int(m['phase'])
            variance = float(m['variance'])
            res[f'variance_{mode}_{size}'][phase] = variance
            
        porosity_re = r"Minimum porosity:\s*(?P<min_porosity>\d+)%, Maximum porosity:\s*(?P<max_porosity>\d+)%"
        rx = re.compile(porosity_re, re.MULTILINE)
        match_res = rx.search(output)
        min_porosity = float(match_res['min_porosity']) * 0.01
        max_porosity = float(match_res['max_porosity']) * 0.01
        res['porosity'] = {'min': min_porosity, 'max': max_porosity}
        
        return res
    
    
    def get_3d_region_analysis(self):
        """Get the 3-dimensional region analysis for all phases in the RVE.
        
        This analysis contains information about number of separate regions, 
        volumes, surfaces, etc. for each phase.

        Returns
        -------
        phase_region_dict : dict
            contains as keys the phase number and as values a dictionary of
            data from the region analysis for the phase.

        """
        existing_phases = self.get_volume_fractions().keys()

        output = self.__process_cmds(["do_3d_region_analysis:"])
        
        phase_region_dict = {}
         # parse output for volume information
        for phase_id in existing_phases:
            phase_region_dict[phase_id] = {}
            
            number_re = '\\d*\\.?\\d+'
            named_number_re = lambda name: f'(?P<{name}>\\d*\\.?\\d+(E[\\+-]\\d+)?)'
            # generate a dict of proprerties to look for
            # KEY will be replaced by the name of the property below to create 
            # named capturing groups
            info_regexs = {
                'region_count': f"Number of regions phase {phase_id} :\\s+KEY\\s*",
                'total_anisotropy' : f"Total anisotropy of regions phase {phase_id} :\\s+KEY\\s*",
                'region_volume': f"Volume of regions phase {phase_id} in voxel:\\s+KEY \\+- {number_re}\\s*",
                'region_volume_variance': f"Volume of regions phase {phase_id} in voxel:\\s+{number_re} \\+- KEY\\s*",
                'region_volume_min': f"Volume of regions phase {phase_id} in voxel \\(Min-Max\\):\\s+KEY - {number_re}\\s*",
                'region_volume_max': f"Volume of regions phase {phase_id} in voxel \\(Min-Max\\):\\s+{number_re} - KEY\\s*",
                'region_volume_um': f"Volume of regions phase {phase_id} in um\\^3:\\s+KEY \\+- {number_re}\\s*",
                'region_volume_um_variance': f"Volume of regions phase {phase_id} in um\\^3:\\s+{number_re} \\+- KEY\\s*",
                'equiv_diam': f"Equivalent diameter of regions phase {phase_id} in um:\\s+KEY \\+- {number_re}\\s*",
                'equiv_diam_variance': f"Equivalent diameter of regions phase {phase_id} in um:\\s+{number_re} \\+- KEY\\s*",
                'surf_volume_ratio' : f"Surface/volume ratio of regions phase {phase_id} in 1/um :\\s+KEY \\+- {number_re}\\s*",
                'surf_volume_ratio_variance' : f"Surface/volume ratio of regions phase {phase_id} in 1/um :\\s+{number_re} \\+- KEY\\s*",
                'edge_surf_ratio' : f"Edge/surface ratio of regions phase {phase_id} in 1/um :\\s+KEY \\+- {number_re}\\s*",
                'edge_surf_ratio_variance' : f"Edge/surface ratio of regions phase {phase_id} in 1/um :\\s+{number_re} \\+- KEY\\s*",
                'corner_edge_ratio': f"Corner/edge ratio of regions phase {phase_id} in 1/um :\\s+KEY \\+- {number_re}\\s*",
                'corner_edge_ratio_variance': f"Corner/edge ratio of regions phase {phase_id} in 1/um :\\s+{number_re} \\+- KEY\\s*",
                'neighbor_count' : f"Number of neighbors per region of regions phase {phase_id} :\\s+KEY \\+- {number_re}\\s*",
                'neighbor_count_variance' : f"Number of neighbors per region of regions phase {phase_id} :\\s+{number_re} \\+- KEY\\s*",
                'local_anisotropy' : f"Local anisotropy of regions phase {phase_id} :\\s+KEY \\+- {number_re}\\s*",
                'local_anisotropy_variance' : f"Local anisotropy of regions phase {phase_id} :\\s+{number_re} \\+- KEY\\s*"
                }
            # replace KEY by the name of the capturing group
            for info, info_re in info_regexs.items():
                info_regexs[info] = info_re.replace('KEY', named_number_re(info))
            
            # parse the output
            for info, info_re in info_regexs.items():                
                rx = re.compile(info_re)
                res = rx.search(output)
                if res is None:
                    print(f"output:\n {output}\n\nerror: the above output could not be parsed for {info}. \nused regex: {info_re}\n")
                    sys.exit(1)
                else:
                    phase_region_dict[phase_id][info] = float(res[info])
        return phase_region_dict
            
    def set_volume_fraction(self, phase_volume_dict, iterations=1, distribute_after=True):
        """Set the volume fraction for the phases in the passed dict.
        
        The volume of the other phases is kept (approximately) constant.
        
        It is possible to iteratively increase the volume fraction by 
        specifying the number of iterations. This way the volume will be 
        increased sucessively which, combined with distributing the objects 
        after each increase step, can be used to create RVEs with less overlap.

        Parameters
        ----------
        phase_volume_dict : dict
            contains as keys the phases and as values the desired volume 
            fraction as a percentage between ``0.0`` and ``100.0``
        iterations: integer
            increasing the volume fraction iteratively instead of directly
            setting the target volume fraction. The default is ``1``, which sets 
            the volume directly.
        distribute_after: bool
            distribute particles after changing the volume fraction. 
            The default is ``True``.

        """
        current_phase_volumes = self.get_volume_fractions()
        self.logger.info("Setting volume fractions.")
        self.logger.info(f"Target volume fractions:  {phase_volume_dict}")
        self.logger.info(f"Initial volume fractions: {current_phase_volumes}")

        if set(phase_volume_dict).issubset(set(current_phase_volumes)):  # check if all of the phases are present
            for ii in range(iterations):
                cmds = []
                for phase_id, volume_fraction_percentage in phase_volume_dict.items():  # set new volume fractions
                    partial_volume_fraction_percentage = volume_fraction_percentage * (ii+1) / iterations
                    cmds.append(f"set_tphases: {phase_id}  {partial_volume_fraction_percentage}")
                unchanged_phases = set(current_phase_volumes) - set(phase_volume_dict)
                for phase_id in unchanged_phases:   # keep old volume fractions for phases not in the phase_volume_dict
                    volume_fraction_percentage = current_phase_volumes[phase_id]
                    cmds.append(f"set_tphases: {phase_id}  {volume_fraction_percentage}")
                cmds.append("do_setvoxel: ")
                cmds.append("do_matchphases: 0")
                
                self.__process_cmds(cmds)
                
                if distribute_after:
                    self.distribute()
        else:
            print(f"error: cannot change volume fraction because the following phases do not exist: {set(phase_volume_dict) - set(current_phase_volumes)}")
            sys.exit(1)
            
        current_phase_volumes = self.get_volume_fractions()
        self.logger.info(f"Done setting volume fractions. Final volume fractions: {current_phase_volumes}")
        
    def intro_at_interfaces(self, mode='corners', phase=1, fraction=1.0):
        """Introduce new voxels at the interfaces between the existing phases.

        Parameters
        ----------
        mode : string, optional
            Where to introduce the new voxels. Possible values are ``'corners'``, 
            ``'edges'``, ``'faces'``. The default is ``'corners'``.
        phase : int, optional
            Phase number for the introduced voxels. The default is ``1``.
        fraction : float, optional
            At what fraction of the corners, edges or faces should new voxels 
            be introduced.
            Possible values are between ``0.0`` and ``1.0``. The default is ``1.0``.
        """
        mode_index_dict = {'corners': 1, 
                               'edges': 2, 
                               'faces': 3}
        if not mode in mode_index_dict:
            raise Exception(f"Invalid mode {mode} for introduction of voxel at interfaces. Possible modes are {set(mode_index_dict.keys())}")
        mode_index = mode_index_dict[mode]
        
        cmds = f""" set_pobjec: 16  {mode_index}
                    set_pobjec: 17  {phase}
                    set_pobjec: 18  {fraction}
                    do_intro_inter: 
                """
        self.__process_cmds(cmds.split('\n'))
            

            
    def delete_small_regions(self, phase=-1, voxel_margin=10):
        """Delete small regions in the given phase.

        Parameters
        ----------
        phase : int, optional
            Number of the phase for which regions should be deleted. 
            A value of ``-1`` deletes small regions of all phases. 
            The default is ``-1``.
        voxel_margin : int, optional
            Minimum number of voxel for a region. All regions with less voxels 
            that this value will be deleted. The default is ``10``.

        """
        cmds = f""" set_pobjec: 13  1
                    set_pobjec: 14  {phase}
                    set_pobjec: 15  {voxel_margin}
                    do_del_small:  """
        self.__process_cmds(cmds.split('\n'))
        
    def iterative_delete_small_regions(self, margin_fraction_of_mean=0.05):
        """Delete regions that are smaller than a fraction of the mean volume 
        for each phase.
        
        The deletion happens iteratively, successively increasing the cutoff 
        until there are no more regions with smaller volume than the fraction 
        of the mean volume of all regions of a phase.

        Parameters
        ----------
        margin_fraction_of_mean : float, optional
            Determines below what fraction of the mean region volume regions 
            should be deleted. Possible values are between ``0.0`` and ``1.0``. 
            The default is ``0.05``.

        """
        self.logger.info("Deleting small regions iteratively")
        phase_region_dict = self.get_3d_region_analysis()
        cutoffs = {}
        current_min_volumes = {}
        corrections = {}
        
        for phase_nr, data in phase_region_dict.items():
            cutoffs[phase_nr] = data['region_volume'] * margin_fraction_of_mean
            current_min_volumes[phase_nr] = data['region_volume_min']
            corrections[phase_nr] = 1
            self.logger.info(f"Initial minimal volume in phase {phase_nr}: {current_min_volumes[phase_nr]}")
            
        
        while any([min_volume < cutoff for min_volume, cutoff in zip(current_min_volumes.values(), cutoffs.values())]):
            phase_region_dict = self.get_3d_region_analysis()
            for phase_nr, data in phase_region_dict.items():
                current_min_volumes[phase_nr] = data['region_volume_min']
                if current_min_volumes[phase_nr] < cutoffs[phase_nr]:
                    print(f"deleting small regions for phase {phase_nr}. current volume: {current_min_volumes[phase_nr]} target volume: {cutoffs[phase_nr]}  correction: {corrections[phase_nr]}")
                    self.delete_small_regions(phase=phase_nr, voxel_margin=cutoffs[phase_nr] + corrections[phase_nr])
                    corrections[phase_nr] *= 2
                    
        phase_region_dict = self.get_3d_region_analysis()
        for phase_nr, data in phase_region_dict.items():
            self.logger.info(f"Final minimal volume in phase {phase_nr}: {current_min_volumes[phase_nr]}")
            
    def dilation(self, number_of_neighbors, phase, repetitions=1):
        """Perform dilation operations on voxels of the given phase.
        
        The dilation takes the neighbor voxels into account and a dilation only
        happens when enough neighboring voxels are present.

        Parameters
        ----------
        number_of_neighbors : integer
            Minimum number of neighbors to consider for dilation operation.
            Possible values are between ``5`` and ``1`` 
        phase : integer
            Phase number of voxels to apply the operation to.
        repetitions : integer, optional
            Number of times the dilation operation is repeated. 
            The default is ``1``.
        """
        number_of_neighbors_dict = {5: 0, 4: 1, 3: 2, 2: 3, 1: 4}
        try:
            number_of_neighbors_id = number_of_neighbors_dict[number_of_neighbors]
        except KeyError:
            raise KeyError("Invalid mode parameter of number of neighbors to consider for dilation operations.")
            
        if not phase in self.get_volume_fractions().keys():
            raise ValueError(f"There are no voxels of phase {phase} for dilation operation.")
            
        if not repetitions > 0:
            raise ValueError("Number of repetitions for dilation operation must be positive")
            
        cmds = f"""  set_pobjec: 4  {number_of_neighbors_id}
                    set_pobjec: 5  {phase}
                    set_pobjec: 6  {repetitions}
                    do_dilation:"""
        self.__process_cmds(cmds.split('\n'))
        
    def store_voxels(self, filename):
        """Store the voxel data of the RVE in a file in GeoVals voxel file 
        format (.val).

        Parameters
        ----------
        filename : str
            Filename of the voxel output file.
        """
        path = self.output_folder / filename
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        self.__process_cmds([f'do_store_voxels: {path.absolute()}'])
        
    def store_objects(self, filename):
        """Store the object data of the RVE in a file in GeoVals object file 
        format (.obj).

        Parameters
        ----------
        filename : str
            Filename of the object output file.
        """
        path = self.output_folder / filename
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        self.__process_cmds([f'do_store_objects: {path.absolute()}'])
        
    def view_voxels(self, screenshot_file=None):
        """3D view of the generated voxel structure.
        """
        self.store_voxels('tmp_voxels.val')
        
        voxel_file_path = self.output_folder / 'tmp_voxels.val'
        vol_fracs = self.get_volume_fractions()
        phases = vol_fracs.keys()
        if screenshot_file is not None:
            screenshot_file = self.output_folder / screenshot_file
        view_RVE(voxel_file_path, phases, screenshot_file)
        os.remove(voxel_file_path)
