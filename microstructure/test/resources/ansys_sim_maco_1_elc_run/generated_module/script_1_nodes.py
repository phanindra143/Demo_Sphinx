from .utils import wait_for_checkpoint_file

def run(mapdl):
    mapdl.run("/input,'mymodule/nodes/1_nodes_0','win',")
    wait_for_checkpoint_file(mapdl, 'done_1_nodes_0.out')
