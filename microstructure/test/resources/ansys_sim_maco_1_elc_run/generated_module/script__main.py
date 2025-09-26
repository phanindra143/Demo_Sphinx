from . import script_1_nodes
from . import script_2_shell_gb_rve
from . import script_3_cms_mesh
from .utils import wait_for_checkpoint_file

def run(mapdl):
    # created by  VoxSM [ISC,ml,2010]
    # gMesh (base): U:\ablagen\ME-Sim-MaVo\WC_50spheres_0605_00ovlp
    # ---------- header ----------
    mapdl.finish()
    mapdl.run("/clear")
    mapdl.run("/Filname, mesh")
    mapdl.run("/prep7")
    # ETs  (keep type-numbers)
    mapdl.et(1, "solid187")  #3D tet (4-10 nodes)
    mapdl.et(2, "SHELL157")  #GB-shell
    mapdl.et(3, "SHELL157")  #RVE-shell (seperate delete)
    # et,4,Targe170     Targe
    # et,5,Conta174, 6 Conta (keyopt1=6: DOF=VOLT)
    # et,6,solid231     solid GB prisms
    mapdl.real(1)  #Real(1)= Shell thickness (GB)
    mapdl.mopt("TetExpnd", 2)  #< 3( )
    mapdl.shpp("silent", "on")
    mapdl.mshmid(2)  #no Midnodes, prevent meshing-errors.  -> add later( )
    # MPs: (MatNr.)
    # '0' -> '10 000',	         = pores
    # Shell/Plane -> '20 000'   = GBs in-plane conductivity
    # CT: real-constant 'ecc'   = GBs through-plane conductance
    # solid-GB = 100*PartMat    = GB lossy-Dielectric
    # ---------- input ----------
    mapdl.run("structFileName = 'WC_50spheres_0605_00ovlp'")
    mapdl.run("L = 0.000192  ")  # L-Box
    # 23182 nodes:
    script_1_nodes.run(mapdl)
    # 98836 GB + RVE Surf elements (triangles)
    script_2_shell_gb_rve.run(mapdl)
    # 86 Vmesh CMs (particles)
    mapdl.run("keepShells = 0   ")  # keep(1)/delete(0) Shells in FVmesh,
    script_3_cms_mesh.run(mapdl)
    # 2 Materials:
    # 1
    # 2
    # ---------- end ----------
    mapdl.esel("s", "type", "", 3)  #RVE-Boundary-Elements
    mapdl.esel("a", "type", "", 2)  #GB-Shells
    mapdl.edele("all")  #delete selected Elements
    mapdl.esel("s", "type", "", 1)  #all
    mapdl.emid("add")  #add Midnodes to all (sel.) Elements
    mapdl.etdele(2, 6)  #needed DOFs only( ), delete '2-6'
    mapdl.allsel()
    mapdl.save("structFileName", "db", "model")
