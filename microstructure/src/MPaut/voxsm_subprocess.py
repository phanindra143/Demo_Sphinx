# -*- coding: utf-8 -*-
import re
import logging
from pprint import pformat
from pathlib import Path
from subprocess import Popen
from pywinauto import Desktop

class VoxSM_Communicator:
    """Communicator class for calling ``VoxSM`` from within python.
    
    Instances of this class will launch ``VoxSM`` and interface with it through 
    ``pywinauto``. You can use most of ``VoxSM's`` features for loading voxel files,
    generating and modifying meshes programmatically.
    
    Note that the objects do not store an internal state and that no extensive 
    checks are performed as to whether a method is currently save to execute 
    (e.g. simplify the mesh when no mesh is currently loaded).
    """
    simplify_default_options = {
            'err-(cost)-max': 1e-5,
            'runs': 5,
            'folding-min': 0.1,
            'Es-per-V-max': 12,
            'FQ-min': 0.16,
            'lmin/lmed-min': 0.22,
            'lmed^2/A-max' : 10.8,
            'FA-max': 1e-12,
            'FA-min': 1e-15,
            'eL(r4)-max': 1e-6,
            'eL(r3)-max': 4e-6,
            'eL-growFac': 5.8,
            'pinch-close-eL': True,
            'd-min': 1e-7,
            'd-fac': 0.15,
            'use-costs': True,
            'intersection-test': True,
            'r3-only': False,
            'r2-only': False,
            'bad-Fs-only': False,
            'high-cost-first': False,
            'fix-corners': False,
            'focal-point-r2': False,
            'focal-point-r3': False,
            }
    
    default_element_types = {1: 'solid187', 2: 'SHELL157', 3: 'SHELL157', 
                             4: 'Targe170',5: 'Conta174', 6:'solid23'}
    
    def __init__(self, executable, logging_dir=''):
        """ When creating a communicator object you must specify the executable 
        for ``VoxSM``.

        Parameters
        ----------
        executable : str
            Path to the ``VoxSM`` executable.

        Raises
        ------
        FileNotFoundError
            Is raised when the executable cannot be found at the given path.
        """
        # logger for protocol
        self.protocol_log = logging.getLogger('VoxSM protocol')
        self.protocol_log.setLevel(logging.INFO)
        protocol_log = logging.FileHandler(Path(logging_dir) / 'voxsm_protocol.log', mode='w')
        protocol_log.setLevel(logging.INFO)
        self.protocol_log.addHandler(protocol_log)

        formatter = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s] %(message)s')        
        # logger for status
        self.status_log = logging.getLogger('VoxSM status')
        self.status_log.setLevel(logging.DEBUG)
        status_log_fh = logging.FileHandler(Path(logging_dir) / 'voxsm_status.log', mode='w')
        status_log_fh.setLevel(logging.DEBUG)
        status_log_fh.setFormatter(formatter)
        self.status_log.addHandler(status_log_fh)
        status_log_c = logging.StreamHandler()
        status_log_c.setLevel(logging.INFO)
        status_log_c.setFormatter(formatter)
        self.status_log.addHandler(status_log_c)
        
        executable_path = Path(executable)
        if executable_path.exists():
            self.subprocess = Popen(executable)
            self.desktop = Desktop(backend="uia")
            
            voxsm_window_title = ' VoxSM  v3.0 - beta     [2017, g.seifert @ Fraunhofer ISC-HTL]'
            self.toplevel_dlg = self.desktop.window(title=voxsm_window_title)
            
            self._setup_wrapper_handles()
        else:
            self.status_log.error(f"error: VoxSM executable could not be found at '{executable_path.absolute()}'")
            raise FileNotFoundError("error: VoxSM executable could not be found", executable_path.absolute())
            
        self.status_log.debug(f"Launching VoxSM executable at '{executable_path.absolute()}'")
            
    def _setup_wrapper_handles(self):
        self.handles = {}
                
        # status output (left edit field)
        self.handles['status output'] = self.toplevel_dlg.child_window(auto_id="richTextBox_message", control_type="Edit").wrapper_object()
        
        # file loading menu
        self.handles['file menu'] = self.toplevel_dlg.child_window(title="File", control_type="MenuItem").wrapper_object()
        
        # tab control
        self.handles['tab control'] = self.toplevel_dlg.child_window(auto_id="tabControl1", control_type="Tab").wrapper_object()

        ## VOX tab ##
        self._select_tab(0)
        # subtab vox menu strip
        self.handles['vox menu strip'] = self.toplevel_dlg.child_window(title="menuStrip2", auto_id="menuStrip2", control_type="MenuBar").wrapper_object()
        
        # remember handle for split regions buttion
        self.handles['vox menu strip'].type_keys('{TAB}{TAB}~')
        self.handles['split regions'] = self.toplevel_dlg.child_window(title="split regions", control_type="MenuItem").wrapper_object()
        self.handles['vox menu strip'].type_keys(2*'{ESC}')
        
        ## global MESH tab ##
        self._select_tab(1)
        self.handles['mesh status'] = self.toplevel_dlg.child_window(auto_id="richTextBox_MESHstatus", control_type="Edit").wrapper_object()
        self.handles['global mesh tab'] = self.toplevel_dlg.child_window(auto_id="tabControl2", control_type="Tab").wrapper_object()
        self.handles['global MESH Statistics menu strip'] = self.toplevel_dlg.child_window(title="menuStrip3", auto_id="menuStrip3", control_type="MenuBar").wrapper_object()
        
        # inputs for smooth
        self.handles['global mesh tab'].type_keys(5 * '{LEFT}' + 2 * '{RIGHT}' + '~')
        self.handles['do smooth'] = self.toplevel_dlg.child_window(title="do smooth", auto_id="button_smooth_do", control_type="Button").wrapper_object()
        self.handles['input_k_BP'] = self.toplevel_dlg.child_window(title="k_BP = (<1!)", auto_id="textBox_smooth_kBP", control_type="Edit").wrapper_object()   
        self.handles["input_iterations"] = self.toplevel_dlg.child_window(title="iterations N =", auto_id="textBox_smoothN", control_type="Edit").wrapper_object()  
        self.handles["input_lambda"] = self.toplevel_dlg.child_window(title="lambda = (>0!)", auto_id="textBox_smooth_lambda", control_type="Edit").wrapper_object()  
        self.handles["input_fix_vs_nn"] = self.toplevel_dlg.child_window(title="Fix Vs with near Neighbors: \r\n\r\n   |v-n| <", auto_id="textBox_smooth_skipD", control_type="Edit").wrapper_object()  
        self.handles['all Vertices'] = self.toplevel_dlg.child_window(title="all Vertices", auto_id="radioButton_Smooth_rAll", control_type="RadioButton").wrapper_object()
        self.handles['r3+ only (edges)'] = self.toplevel_dlg.child_window(title="r3+ only (edges)", auto_id="radioButton_Smooth_r3pOnly", control_type="RadioButton").wrapper_object()
        self.handles['r2 only'] = self.toplevel_dlg.child_window(title="r2 only", auto_id="radioButton_Smooth_r2Only", control_type="RadioButton").wrapper_object()
        
        # inputs for simplify
        self.handles['global mesh tab'].type_keys(5 * '{LEFT}' + 3 * '{RIGHT}' + '~')
        
        option_automation_id_mapping = {
            'err-(cost)-max': 'textBox_Simp_errmax',
            'runs': 'textBox_Simp_sRuns',
            'folding-min': 'textBox_Simp_foldingNumMin',
            'Es-per-V-max': 'textBox_Simp_VsEsMax',
            'FQ-min': 'textBox_Simp_FQmin',
            'lmin/lmed-min': 'textBox_Simp_lminlmedMin',
            'lmed^2/A-max' : 'textBox_Simp_lmed2Amax',
            'FA-max': 'textBox_Simp_FAmax',
            'FA-min': 'textBox_Simp_FAmin',
            'eL(r4)-max': 'textBox_Simp_eLr4Max',
            'eL(r3)-max': 'textBox_Simp_eLr3pMax',
            'eL-growFac': 'textBox_Simp_eLfac',
            'pinch-close-eL': 'checkBox_Simp_PC',
            'd-min': 'textBox_Simp_PCdMin',
            'd-fac': 'textBox_Simp_PCfac',
            'use-costs': 'checkBox_Simp_useCosts',
            'intersection-test': 'checkBox_Simp_IntersectionT',
            'r3-only': 'checkBox_Simp_eR3pOnly',
            'r2-only': 'checkBox_Simp_noEr3p',
            'bad-Fs-only': 'checkBox_Simp_badFsEH',
            'high-cost-first': 'checkBox_Simp_inverseSort',
            'fix-corners': 'checkBox_Simp_fixR4p',
            'focal-point-r2': 'checkbox_Simp_FPr2',
            'focal-point-r3': 'checkBox_Simp_FPr3p',
            }
        for option_name, auto_id in option_automation_id_mapping.items():
            if 'textBox' in auto_id:
                self.handles[option_name] = self.toplevel_dlg.child_window(auto_id=auto_id, control_type="Edit").wrapper_object()
            elif 'check' in auto_id:
                self.handles[option_name] = self.toplevel_dlg.child_window(auto_id=auto_id, control_type="CheckBox").wrapper_object()

        # buttons for building edge heap and running simplify
        self.handles['build Edge-HEAP'] = self.toplevel_dlg.child_window(title="build   \r\nEdge-HEAP ", auto_id="button_Simp_builtHeap", control_type="Button").wrapper_object()
        self.handles['do SIMPLIFY Mesh'] = self.toplevel_dlg.child_window(title="do SIMPLIFY Mesh", auto_id="button_Simp_contractHeap", control_type="Button").wrapper_object()

        ## surface mesh& TV | TG tab ##
        self._select_tab(2)
        self.handles['call TetView'] = self.toplevel_dlg.child_window(title="call TetView", auto_id="checkBox_callTV", control_type="CheckBox").wrapper_object()
        self.handles['hide RVE boundary'] = self.toplevel_dlg.child_window(title="hide RVE boundary", auto_id="checkBox_hideRVE", control_type="CheckBox").wrapper_object()
        self.handles['write mesh'] = self.toplevel_dlg.child_window(title="write to  *.node & *.smesh\r\n", auto_id="button_smesh", control_type="Button").wrapper_object()
        self.handles['material colors only'] = self.toplevel_dlg.child_window(title="material colors  only", auto_id="checkBox_MatColorOnly", control_type="CheckBox").wrapper_object()

        ## >> ANSYS tab ##
        self._select_tab(3)
        self.handles['write ansys'] = self.toplevel_dlg.child_window(title="gMesh (Vs, Fs, CMs)\r\nto  ANSYS-code *.win", auto_id="button_vm_gm", control_type="Button").wrapper_object()
        self.handles['gb_checkbox'] = self.toplevel_dlg.child_window(title="introduce solid GB-Prisms\r\nGB-thickness [m] = \r\n ( ~1/10 eLmin )", auto_id="checkBox_vm_solidGB", control_type="CheckBox").wrapper_object()
        self.handles['gb_thickness_edit'] = self.toplevel_dlg.child_window(auto_id="textBox_vm_hGB", control_type="Edit").wrapper_object()
        self.handles['ansys_header'] = self.toplevel_dlg.child_window(title="( uses  > ANSYS - header.)", auto_id="richTextBox_vm_winHeader", control_type="Edit").wrapper_object()
        
            
    def _select_tab(self, number):
        """Switch to the specified tab in the right ``VoxSM`` window.

        Parameters
        ----------
        number : int
            number indicating which tab:
                1 -> VOX
                2 -> global MESH
                3 -> surface mesh & TV | TG
                4 -> >> ANSYS

        """
        self.status_log.debug(f"Switching to tab {number}")
        # first we move as far left as possible and then from there we move 
        # right <number> of times
        select_cmd = '{LEFT}' * 5 + '{RIGHT}' * number + '~'
        self.handles['tab control'].type_keys(select_cmd)
    
    def _wait_for_output(self, target_output, old_lines_count):
        """Wait for the target output to appear in the left console of the 
        ``VoxSM`` program.

        Parameters
        ----------
        target_output : string
            The desired output to look out for
        old_lines_count : integer
            The number of console lines before the command producing the 
            output was submitted. This must be retrieved beforehand

        Returns
        -------
        output : list
            A list containing all of the lines of the output

        """
        self.status_log.debug(f"Waiting for target_output='{target_output}' with old_lines_count={old_lines_count}.")
        output = {}
        done = False
        while not done: # we have to read the output in a while loop because 
                        # it may happen that previous output gets changed
            current_output = self.handles['status output'].get_value().split('\r')
            # read the new console output
            for i, line in enumerate(current_output[old_lines_count:]):    
                output[i] = line
            
            # check if we find the target output in the console output
            done = any([target_output in line for line in output.values()])
            
        # we need to clear the output regularly because otherwise for the 
        # following commands self.status_output.get_value() will not return
        # the full output and thus the wait may never finish
        # we just dump all of the output after more than 100 lines have been
        # written
        if len(self.handles['status output'].get_value().split('\r')) > 75:
            self.handles['status output'].set_text('Output was cleared from python.\r')
            
        return list(output.values())
    
    def _confirm_dialog(self, dialog_title, confirm_btn_text):
        """Helper method for pressing confirmation button in the popup dialog.
        
        Searches for the dialog with the given title and pressed 'Enter' on the
        button with the specified name.   

        Parameters
        ----------
        dialog_title : ``str``
            Title of the confirmation that was opened.
        confirm_btn_text : ``str``
            Text of the confirmation button.

        """
        self.status_log.debug(f"Waiting for dialog with dialog_title='{dialog_title}' to appear")
        cnf_btn = self.toplevel_dlg.child_window(title=confirm_btn_text, control_type="Button")
        cnf_btn.wait('visible')
        self.status_log.debug(f"Pressing confirm button with confirm_btn_text='{confirm_btn_text}'")
        cnf_btn.type_keys('~')

    def open_voxel_file(self, path):
        """Open the GeoVal voxel file (extension .val) at the given path and 
        load the data into ``VoxSM``.

        Parameters
        ----------
        path : string
            Path of the voxel file

        """
        path = Path(path)
        
        self.protocol_log.info(f"open_voxel_file: path={path.absolute()}")
        self.status_log.info(f"Opening voxel file at path='{path.absolute()}'.")
        
        if not path.exists():
            self.status_log.error(f"Voxel file not found at path='{path.absolute()}'")
            raise FileNotFoundError("error: voxel file not found", path.absolute())

        old_lines_count = self.handles['status output'].get_value().count('\r')

        self.handles['file menu'].type_keys('f') # -> file
        self.handles['file menu'].type_keys('o') # -> open

        filename_input = self.toplevel_dlg.child_window(title="Dateiname:", auto_id="1148", control_type="Edit").wrapper_object()
        open_btn = self.toplevel_dlg.child_window(title="Öffnen", auto_id="1")

        filename_input.set_text(str(path.resolve()))
        
        # press ENTER on 'Öffnen' button
        open_btn.type_keys('~')

        return self._wait_for_output('load  VOX ...done', old_lines_count)


    def split_regions(self):
        """Split the voxel geometry into connected regions."""
        self.protocol_log.info("split_regions: ")
        self.status_log.info(f"Splitting regions.")
        self._select_tab(0)
        
        old_lines_count = self.handles['status output'].get_value().count('\r')
        
        # navigate to 'print RTB' --(1xRIGHT)-> 'Modify' --> 'split regions'
        self.handles['vox menu strip'].type_keys('{TAB}{TAB}~')
        self.handles['split regions'].type_keys('~')
        
        # confirm
        self._confirm_dialog('split VOX:', 'OK')
        
        return self._wait_for_output('split VOX::regions ...done', old_lines_count)
        
        
    def generate_mesh(self):
        """Generate a mesh from the voxels using ``VoxSM's`` marching 
        tetrahedron method."""
        self.protocol_log.info("generate_mesh: ")
        self.status_log.info(f"Generating mesh.")
        self._select_tab(0)  # VOX tab
        
        old_lines_count = self.handles['status output'].get_value().count('\r')
        
        # navigate to 'print RTB' --(2xRIGHT)-> '>> scan Grid'
        self.handles['vox menu strip'].type_keys('{TAB}{TAB}{TAB}~')
        
        # confirm
        self._confirm_dialog('confirm', 'OK')
        
        return self._wait_for_output('scan Grid ...done', old_lines_count)
        
    
    def _get_Fs_statistics(self):
        """Get statistics information about triangles in the mesh.

        Returns
        -------
        stats : dict
            Dictionary with parameter description as keys and corresponding 
            statistics as value.

        """
        self.status_log.debug(f"Obtaining Fs statistics.")
        self._select_tab(1) # global MESH tab
        
        old_lines_count = self.handles['status output'].get_value().count('\r')
        
        # navigate to '[ model RTB ]': Tab --(3xLEFT)-> 'Enter' -> 'ALT + g'
        # -> DOWN -> Enter
        self.handles['global mesh tab'].type_keys('{LEFT}{LEFT}{LEFT}~')
        
        self.handles['global MESH Statistics menu strip'].type_keys('g{DOWN}~')
        
        output = self._wait_for_output('fQ', old_lines_count)
        output = "".join(output)
        named_number_re = lambda name: r'(?P<{name}>\d*\.?\d+(e[\+-]\d\d)?)'.format(name=name)
        
        stats = {}
        
        rx = re.compile(f"fA: {named_number_re('fA_min')} - {named_number_re('fA_max')}")
        res = rx.search(output)
        stats = {**res.groupdict(), **stats}
        
        rx = re.compile(f"eL: {named_number_re('eL_min')} - {named_number_re('eL_max')}")
        res = rx.search(output)
        stats = {**res.groupdict(), **stats}
        
        rx = re.compile(f"fQ: {named_number_re('fQ_min')} - {named_number_re('fQ_max')}")
        res = rx.search(output)
        stats = {**res.groupdict(), **stats}
        
        stats = { name: float(stat) for name, stat in stats.items()}
        
        self.status_log.debug(f"fs_statistics = {pformat(stats)}")

        return stats
    
    def smooth(self, iterations=100, k_BP=0.02, lambd='auto', fix_vs_nn=2.0e-7,
               mode='all'):
        """Run smoothing operations on the mesh.
        
        This will call ``VoxSM's`` smoothing algorithm. You can control the 
        smoothing operations by specifying additional options.
        
        For a more detailed description of the parameters see pages 61f. in 
        this :download:`document <../_static/2013_Thomas_Mueller_Dissertation.pdf>`
        and page 16 in this :download:`document <../_static/dokumentation_programme.pdf>`.

        Parameters
        ----------
        iterations : int, optional
            Number of rounds for the smoothing. Must be greater zero. The default is ``100``.
        k_BP : float, optional
            Controls the *waviness* of the surfaces. Must be between ``0`` and ``1.0``. 
            The default is ``0.02``.
        lambd : str or float, optional
            Scale factor influencing the smoothing. The default is ``'auto'``.
        fix_vs_nn : float, optional
            Skip distance to near neighbors, below which nodes will not be moved. 
            Must be positive. The default is ``2.0e-7``.
        mode : string, optional
            Mode for selecting vertices for smoothing.
            Possible values are ``'all'`` which considers all vertices for
            smoothing operations, ``'edges'`` which only considers edges at the
            boundary of at least three particles and ``'faces'`` which only
            considers edges at the faces of two particles.
            The default is ``'all'``.

        """
        self.protocol_log.info(f"smooth: iterations={iterations}, "\
                         f"k_BP={k_BP}, lambd={lambd}, fix_vs_nn={fix_vs_nn}, "\
                         f"mode={mode}")
        self.status_log.info("Smoothing mesh.")
        self.status_log.debug(f"options for smooth: iterations={iterations}, "\
                         f"k_BP={k_BP}, lambd={lambd}, fix_vs_nn={fix_vs_nn}, "\
                         f"mode={mode}")
        iterations = int(iterations)
        if not iterations > 0:
            self.status_log.error(f"Invalid value iterations={iterations} for smooth.")
            raise ValueError(f"Invalid number of iterations = {iterations} for smoothing operation. Iterations must be greater than zero!")
        if not 0.0 < k_BP < 1.0:
            self.status_log.error(f"Invalid value k_BP={k_BP} for smooth.")
            raise ValueError(f"Invalid factor k_BP = {k_BP} for smoothing operation. k_BP must be between 0 and 1!")
        if not type(lambd) in [str, int, float]:
            self.status_log.error(f"Invalid type type(lambd)={type(lambd)} for smooth.")
            raise TypeError(f"Invalid type for lambd for smoothing operation. You specified '{type(lambd)}' but lambd must be a number or string!")
        else:
            if type(lambd) == str and not lambd == 'auto':
                self.status_log.error(f"Invalid value lambd={lambd} for smooth.")
                raise ValueError(f"Invalid scale factor lambd = {lambd}. lambd must be a positive value or 'auto'!")
            if type(lambd) in [float, int] and not lambd > 0.0:
                self.status_log.error(f"Invalid value lambd={lambd} for smooth.")
                raise ValueError(f"Invalid scale factor lambd = {lambd}. lambd must be a positive value or 'auto'!")
        if not 0.0 < fix_vs_nn:
            self.status_log.error(f"Invalid value fix_vs_nn={fix_vs_nn} for smooth.")
            raise ValueError(f"Invalid skip distance fix_vs_nn={fix_vs_nn} for smoothing operation. fix_vs_nn must be positive!")
        if not mode in ['all', 'edges', 'faces']:
            self.status_log.error(f"Invalid mode='{mode}' for smooth.")
            raise ValueError(f"Invalid mode '{mode}' for smoothing operation. Possible modes are 'all', 'edges', 'faces'")
        
        #self._select_tab(1) # global MESH tab
        
        old_lines_count = self.handles['status output'].get_value().count('\r')
        
        # set options
        self.handles['input_k_BP'].set_text(str(k_BP))
        self.handles['input_iterations'].set_text(str(iterations))
        self.handles['input_lambda'].set_text(str(lambd))
        self.handles['input_fix_vs_nn'].set_text(str(fix_vs_nn))
        if mode == 'all':
            self.handles['all Vertices'].select()
        elif mode == 'edges':
            self.handles['r3+ only (edges)'].select()
        elif mode == 'faces':
            self.handles['r2 only'].select()
         
        # press Enter on 'do smooth' button
        self.handles['do smooth'].click()
        
        # confirm
        ok_btn = self.desktop.window(title='confirm smooth parameters:')['OK']
        ok_btn.wait('visible')
        ok_btn.type_keys('~')
        
        return self._wait_for_output('iterate ...done', old_lines_count)
        
    def adaptive_smooth(self, eL_min_factor=0.75):
        """Smooth the current mesh with some automatically chosen options.
        
        Does the same as :func:`~MPaut.voxsm_subprocess.smooth` except that the 
        parameter ``fix_vs_nn`` will be determined automatically by a factor 
        multiplied by the current minimum length of mesh elements (``eL_min``).

        Parameters
        ----------
        eL_min_factor : float, optional
            This factor determines which value for ``fix_vs_nn`` will be used. 
            The default ``0.75`` means that ``0.75 * eL_min`` will be used

        Raises
        ------
        RuntimeWarning
            It may happen that the smoothing introduces triangles with a small
            area (``< 1e-16``) which will later cause problems during the meshing 
            in ANSYS. When this happens an exception is raised that can be 
            handled by the user.

        """
        self.status_log.info(f"Performing adaptive mesh smoothing.")
        self.status_log.debug(f"Parameters for adaptive mesh smoothing: eL_min_factor={eL_min_factor}")

        if not 0.0 < eL_min_factor:
            self.status_log.error(f"Invalid value eL_min_factor={eL_min_factor}.")
            raise ValueError("eL_min_factor must be positive!")
        
        # one smoothing run for all vertices
        stats = self._get_Fs_statistics()
        fix_vs_nn = stats['eL_min'] * eL_min_factor
        self.smooth(fix_vs_nn=fix_vs_nn)
        stats_after_smooth = self._get_Fs_statistics()
        fA_min = stats_after_smooth['fA_min']
        if  fA_min < 1e-16:
            self.status_log.warning(f"Smoothing introduced triangles with small fA! fA_min = {fA_min}\nthis will cause problems in ANSYS!")
            raise RuntimeWarning(f"smoothing introduced triangles with small fA! fA_min = {fA_min}\nthis will cause problems in ANSYS")
        
        # another run only for edges
        self.smooth(fix_vs_nn=fix_vs_nn, mode='edges')
        stats_after_smooth = self._get_Fs_statistics()
        fA_min = stats_after_smooth['fA_min']
        if  fA_min < 1e-16:
            self.status_log.warning(f"Smoothing introduced triangles with small fA! fA_min = {fA_min}\nthis will cause problems in ANSYS!")
            raise RuntimeWarning(f"smoothing introduced triangles with small fA! fA_min = {fA_min}\nthis will cause problems in ANSYS")
        
        # final run only for faces
        self.smooth(fix_vs_nn=fix_vs_nn, mode='faces')
        stats_after_smooth = self._get_Fs_statistics()
        fA_min = stats_after_smooth['fA_min']
        if  fA_min < 1e-16:
            self.status_log.warning(f"Smoothing introduced triangles with small fA! fA_min = {fA_min}\nthis will cause problems in ANSYS!")
            raise RuntimeWarning(f"smoothing introduced triangles with small fA! fA_min = {fA_min}\nthis will cause problems in ANSYS")
        
        
    def simplify(self, option_dict={}): 
        """Run the mesh simplification algorithm implemented in ``VoxSM`` on
        the current mesh.
        
        You can specify options for the mesh simplification as described on 
        pages 63f. in this :download:`document <../_static/2013_Thomas_Mueller_Dissertation.pdf>`.
        
        At the moment no checks are performed for the passed options, i.e. you
        need to make sure that you only pass reasonable values for the options.

        Parameters
        ----------
        option_dict : dict, optional
            The default is ``{}`` which means the default options from 
            :py:const:`~MPaut.voxsm_subprocess.VoxSM_Communicator.simplify_default_options`
            will be used.

        """
        self.protocol_log.info(f"simplify: option_dict={pformat(option_dict)}")
        self.status_log.info(f"Performing mesh simplification.")
        self.status_log.debug(f"Options used for simplify: option_dict={pformat(option_dict)}")

        
        if not set(option_dict.keys()).issubset(set(VoxSM_Communicator.simplify_default_options.keys())):
            self.status_log.error(f"Invalid options {set(option_dict.keys()) - set(VoxSM_Communicator.simplify_default_options.keys())} specified for simplify operation.")
            raise ValueError(f"Invalid options {set(option_dict.keys()) - set(VoxSM_Communicator.simplify_default_options.keys())} specified for simplify operation.")
            
        self._select_tab(1) # global MESH tab
        
        old_lines_count = self.handles['status output'].get_value().count('\r')
        
         # set user defined options
        for option, value in option_dict.items():
            input_field = self.handles[option]
            if type(value) == bool:
                if input_field.get_toggle_state() != value:
                    input_field.toggle()
            else:
                input_field.set_text(str(value))
        # set default options for options not given by the user
        for option in set(VoxSM_Communicator.simplify_default_options.keys()) - set(option_dict.keys()):
            input_field = self.handles[option]
            value = VoxSM_Communicator.simplify_default_options[option]
            if type(value) == bool:
                if input_field.get_toggle_state() != value:
                    input_field.toggle()
            else:
                input_field.set_text(str(value))
           
        # build edge heap
        self.handles['build Edge-HEAP'].click()
        
        # wait until edge heap is built
        self._wait_for_output('building Heap ...done ', old_lines_count)
        
        old_lines_count = self.handles['status output'].get_value().count('\r')
        
        # do SIMPLIFY Mesh
        self.handles['global mesh tab'].type_keys(5 * '{LEFT}' + 3 * '{RIGHT}' + '~')
        self.handles['do SIMPLIFY Mesh'].type_keys('~')
        
        # confirm
        self._confirm_dialog('confirm', 'OK')
        
        # wait until simplify is complete
        output = self._wait_for_output('# (', old_lines_count)    # '# (' indicates that command has finished because time is printed
        
        # parse output of simplify operation
        simplify_stats = self._parse_simplify_output("\n".join(output))
        
        self.status_log.debug(f"statistics of simplify operation: {pformat(simplify_stats)}")
        
        return simplify_stats

    def _parse_simplify_output(self, output):
        """Parse the output of the simplify command in the left panel of VoxSM 
        to obtain information about the simplify operation.
        

        Parameters
        ----------
        output : string
            Output as displayed in the left panel of VoxSM.

        Returns
        -------
        output_dict : dict
            Dictionary with information about the selected parameters and the
            completed operation.

        """
        self.status_log.debug(f"Parsing output of simplify operation. output='\n{output}'")
        
        float_re = r"([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)"
        simplify_stats = {}
        
        # number of edges
        m = re.search(r"iterate\s+(?P<value>\d+) edges", output)
        simplify_stats['n_edges_total'] = int(m['value'])
        
        # number of deleted vertices and triangles
        m = re.search(r"V- (?P<deleted_vertices>\d+), F- (?P<deleted_faces>\d+)", output)
        simplify_stats['deleted_vertices'] = int(m['deleted_vertices'])
        simplify_stats['deleted_faces'] = int(m['deleted_faces'])
        
        # statistics of simplify operation
        stats = ["accepted & contracted", "Costs", "Vregs", 
                 "pinched corner", "Fs folding", "FA max", "FA min", 
                 "FQ lmin/med", "FQ lmed^2/A", "FQ shewchuk", "Vs numEsMax", 
                 "eLmax(r3+)", "EP", "Es have =2Fs(reg)", "eL-growthFactor", 
                 "Vs have >=3Es", "pinch close", "Fs intersect"]
        
        for s in stats:
            m = re.search(r"(?P<n_edges>\d+) \(\s*(?P<percentage>{0}|NaN)%\).*".format(float_re) + re.escape(s), output)
            n_edges = int(m['n_edges'])
            percentage = float(m['percentage'])
            simplify_stats[s] = {'n_edges': n_edges,
                                 'percentage': percentage}
        
        return simplify_stats
    
    def _get_mesh_info(self):
        """Get info about the currently loaded mesh.
        
        This returns the data as displayed in the top-right text edit box of 
        the global mesh tab.
        
        Returns
        -------
        mesh_info : dict
            Dictionary with number of vertices, faces and egdes of the current
            mesh
        """
        self.status_log.debug(f"Getting information about the mesh.")

        mesh_info = {}
        mesh_status = self.handles['mesh status'].get_value()
        desired_info = ['vertices', 'faces', 'edges']
        for d in desired_info:
            m = re.search(r"{0}\s*:\s+(?P<value>\d+)".format(d), mesh_status)
            mesh_info[d] = int(m['value'])
            
        self.status_log.debug(f"mesh_info = {pformat(mesh_info)}")

        return mesh_info
    
    def adaptive_simplify(self, max_vertices=50000, repeat_threshold=5):
        """Run heuristic adaptive mesh simplification until the given number of vertices is reached.
        
        This function will sucessively call :func:`~MPaut.voxsm_subprocess.simplify`
        with heuristically adjusted options.
        
        First, only the faces of particles (i.e. triangles which are adjacent
        to at most two different particles) will be simplified.
        This step is repeated as long as more than a certain percentage of edges 
        (controllable by the ``repeat_threshold`` parameter) are collapsed in 
        each run.
        
        When simplification of the faces no longer improves the mesh, the focus
        switches to the edges of particles (i.e. triangles that are adjacent
        to more than two particles). Here the simplification is also carried 
        out until there is no improvement according to the number of collapsed
        edges (again using the ``repeat_threshold`` parameter).

        The above two steps will be repeated with increasing the size of the 
        parameters controlling the maximum length and size of edges and 
        triangles until there are less than the specified number of 
        ``max_vertices`` remaining in the mesh.
        
        Currently, there is no maximum number of repetitions so the algorithm
        could possible run forever if the mesh simplification runs into some
        kind of dead end.

        Parameters
        ----------
        max_vertices : int, optional
            Target number of vertices in the mesh. The adaptive simplification
            procedure will continue while more vertices are present in the mesh.
            The default is ``50000``.
        repeat_threshold : float, optional
            Percentage value which controls when the simplification runs of
            faces/edges are stopped and the simplification parameters are 
            increased.
            The default is ``5`` which means that the simplification with a
            given option will continue until less than ``5%`` of edges are
            collapsed.

        Returns
        -------
        mesh_info : dict
            Dictionary containing information about the number of vertices and
            faces in the final mesh.

        """
        self.status_log.info("Running adaptive mesh simplification.")
        self.status_log.debug(f"adaptive_simplify options: max_vertices={max_vertices}, repeat_threshold={repeat_threshold}")
        options = {'runs': 1}
        
        mesh_info = self._get_mesh_info()
        while mesh_info['vertices'] > max_vertices:
            stats = self._get_Fs_statistics()
            # set options for the current level
            options['FA-max'] = stats['fA_max'] * 10
            options['eL(r4)-max'] = stats['eL_max']
            options['eL(r3)-max'] = 4 * options['eL(r4)-max']
        
            # simplify faces first until there is no improvement 
            # (less than repeat_threshold% of edges collapsed)
            done = False
            while not done:
                options['r2-only'] = True
                options['r3-only'] = False
                stats = self.simplify(options)
                mesh_info = self._get_mesh_info()

                # continue until the desired number of vertices is reached or
                # there is no significant progress
                done = mesh_info['vertices'] <= max_vertices or \
                    stats['accepted & contracted']['percentage'] < repeat_threshold
                
            # if we have not already reached the desired number of vertices
            # we now simplify triangles at particle edges until there is no 
            # improvement
            done = mesh_info['vertices'] <= max_vertices
            while not done:
                options['r2-only'] = False
                options['r3-only'] = True
                stats = self.simplify(options)
                mesh_info = self._get_mesh_info()
                done = mesh_info['vertices'] <= max_vertices or \
                    stats['accepted & contracted']['percentage'] < repeat_threshold
        
        fs_stats = self._get_Fs_statistics()
        mesh_stats = {o: mesh_info[o] for o in ['vertices', 'faces']}
        final_mesh_info = {**fs_stats, **mesh_stats}
        self.status_log.info(f"Adaptive mesh simplification completed.")
        self.status_log.debug(f"Properties of final mesh: {pformat(final_mesh_info)}.")
        
        return final_mesh_info
        
    def store_mesh(self, call_tetview=False, hide_RVE_boundary=False, material_colors_only=True):
        """Store the current mesh in a file.
        
        This generates a ``.node`` file and a ``.smesh`` file.
        The filename is determined by the filename of the loaded voxel 
        file.
        E.g. ``voxels.val`` -> ``voxels.tmpSurf.node``, ``voxels.tmpSurf.smesh``
        
        Parameters
        ----------
        call_tetview : bool, optional
            Start TetView after the file was written to view the generated mesh. 
            The default is ``False``.
        hide_RVE_boundary : bool, optional
            Hide the boundary of the RVE in the TetView mesh. 
            The default is ``False``.
        material_colors_only : bool, optional
            Display only material colors in the TetView mesh. 
            The default is ``True``.

        """
        self.protocol_log.info(f"store_mesh: call_tetview={call_tetview}")
        self.status_log.info(f"Storing mesh.")
        self.status_log.debug(f"Options used for store_mesh: call_tetview={call_tetview}")
        
        old_lines_count = self.handles['status output'].get_value().count('\r')
        
        if self.handles['call TetView'].get_toggle_state() != call_tetview: # disable TetView call afer mesh is written
            self.handles['call TetView'].toggle()
        if self.handles['material colors only'].get_toggle_state() != material_colors_only:
            self.handles['material colors only'].toggle()
        if self.handles['hide RVE boundary'].get_toggle_state() != hide_RVE_boundary:
            self.handles['hide RVE boundary'].toggle()

        self.handles['write mesh'].click()
        
        return self._wait_for_output('write *.tmpSurf ...(*.node,*.smesh) done', old_lines_count)
        
    def store_ansys(self, introduce_GB_prisms=True, element_types={}, gb_thickness=None):
        """Generate ANSYS scripts with the definition of the mesh for simulations.
        
        ``VoxSM`` automatically generates input files for ``ANSYS`` containing 
        the definition of nodes and elements of the generated mesh, as well as 
        scripts for loading the mesh in preparation for simulations. 
        The following ``ANSYS APDL`` script files will be created:
            
        - ``1_nodes.win`` - contains the node positions of the mesh
        - ``*_GB_prisms.win`` - introduces shell elements at the grain 
          boundaries (can be used to model boundary layer effects)
          
          *Note that grain boundaries elements will only be created if*
          ``introduce_GB_prisms`` *is set to* ``True``.
        - ``*_SHELL_GB_RVE.win`` - defines *components* of elements (those 
          correspond to geometric objects or particles in ``GeoVal``)
        - ``*_CMs_mesh.win`` - fills components with volumetric elements  
        - ``_main.win`` - main scripts contains general definitions of the 
          element types and RVE dimensions, executes the other scripts from 
          above and stores the resulting mesh in a database.
          You can run this file in ``ANSYS APDL`` to generate a database file 
          with the definition of a mesh ready for subsequent simulations.
          
        The generated files will be placed in the same directory where the
        original GeoVal file (``.val``) was located.

        Parameters
        ----------
        introduce_GB_prisms : bool, optional
            Generate prism elements at the grain boundaries (cf. Section 3.3.1
            in this :download:`document <../_static/2013_Thomas_Mueller_Dissertation.pdf>`)
            
            The default is ``True``.

        element_types: dict, optional
            Dictionary for defining the element types in the ``_main.win`` header
            output by VoxSM. What element types you need depends on what type
            of analysis you are running. For elasticity simulations you may
            want to use the type ``solid187`` for the grain tetrahedra.
            For thermal conductivity you can use ``solid70``.
            For a list of the available elements see 
            `here <https://www.mm.bme.hu/~gyebro/files/ans_help_v182/ans_elem/Hlp_E_ElemTOC.html>`_ .
            
            The default elemement types are defined in 
            :py:const:`~MPaut.voxsm_subprocess.VoxSM_Communicator.default_element_types`.
        
        gb_thickness : float, optional
            Value for the grain boundary prism thickness. 
            If not specified a value of ``0.1 * eL_min`` (``eL_min`` = minimum 
            edge length) will be used as suggested in the tooltip of the 
            checkbox.
        """
        self.protocol_log.info(f"store_ansys: introduce_GB_prisms={introduce_GB_prisms}, gb_thickness={gb_thickness}")
        self.status_log.info(f"Storing ansys files.")
        self.status_log.debug(f"options used for store_ansys: introduce_GB_prisms={introduce_GB_prisms}, gb_thickness={gb_thickness}")
        
        # need to get mesh statistics for automatic selection of grain boundary thickness
        fs_stats = self._get_Fs_statistics()
        
        # switch to ANSYS tab
        #self._select_tab(3)
        
        if self.handles['gb_checkbox'].get_toggle_state() != introduce_GB_prisms:
            self.handles['gb_checkbox'].toggle()
        if introduce_GB_prisms:
            # set suggested default value for grain boundary element thickness
            # ~ 1/10 eLmin
            if gb_thickness is None:
                gb_thickness = fs_stats['eL_min'] * 0.1
            self.handles['gb_thickness_edit'].set_text(str(gb_thickness))
        
        # set user-defined element types in ansys header
        header_text = self.handles['ansys_header'].get_value()
        for et_number in range(1,7):        
            rx = re.compile(r"et,{0},(?P<element_type>\S+)".format(et_number))
            # if user does not specify element type for a type id, use the
            # default elemnt type instead
            etype = element_types.get(et_number, VoxSM_Communicator.default_element_types[et_number])
            header_text = re.sub(rx, f'et,{et_number},{etype}', header_text)
        self.handles['ansys_header'].set_text(header_text)
        
        self._select_tab(3)
        self.handles['write ansys'].type_keys('~')
        
        old_lines_count = self.handles['status output'].get_value().count('\r')
        
        dlg = self.toplevel_dlg.child_window(title='Ordner suchen')
        dlg.wait('visible')
        dlg.type_keys('~')

        # wait until file output is complete
        return self._wait_for_output('# (', old_lines_count)    # '# (' indicates that command has finished because time is printed
    
    def print_particles(self):
        """Print information about the particles in the voxel grid to console 
        in VoxSM's VOX tab."""
        self.protocol_log.info("print_particles: ")
        self.status_log.info("Printing particles.")
        self._select_tab(0)   # VOX tab
        # navigate to 'print RTB' + Enter
        self.handles['vox menu strip'].type_keys('p{DOWN}~').type_keys('p~')
        
    def print_materials(self):
        """Print information about the materials in the voxel grid to console 
        in VoxSM's VOX tab."""
        self.protocol_log.info("print_materials: ")
        self.status_log.info("Printing materials.")

        self._select_tab(0)  # VOX tab
        # navigate to 'print RTB' --(1xDOWN)--> Enter
        self.handles['vox menu strip'].type_keys('p{DOWN}~')
        
    def close(self):
        """Close the VoxSM window."""
        self.protocol_log.info("close: ")
        self.status_log.info("Closing VoxSM.")
        self.subprocess.kill()
