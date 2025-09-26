import random
import numpy as np

class MockMAPDL:
    def __init__(self):
        self.mapdl = None
        class Object(object):
            def __init__(self):
                pass            
        self.mesh = Object()
        self.mesh.nodes = np.array([[0, 0, 0], [1,1,1]])
        
    def run(self, *args, **kwargs):
        if args[0].lower().startswith("*get,"):
            # pretend get command works and puts value in parameter dict
            k = args[0].split(",")[1]
            self.parameters._parm[k] = 1
        print("run", "args=", args, "kwargs=", kwargs)
        
    def get(self, *args, **kwargs):
        print("get", "args=", args, "kwargs=", kwargs)
        return random.random()
    
# -*- coding: utf-8 -*-
def get_MockMAPDL():
    
    mapdl = MockMAPDL()
    # create dummy member functions that simulate Ansys commands by just
    # printing the command and arguments to console
    def new_member_creator(func_name):
        def new_member(s, *args, **kwargs):
            print(func_name, "args=", args, "kwargs=", kwargs)
            return ''
        return new_member
    for func_name in ['finish', 'clear', 'mp', 'resume', 'allsel',
                      'tunif', 'tref', 'nsel', 'd', 'cp', 'nsubst',
                      'eqslv', 'solve', 'exit', 'etable', 'esel',
                      'lsclear', 'mpamod', 'ssum', 'nsort', 'save',
                      'nsle', 'smult', 'pretab', 'fsum', 'plnsol',
                      'prep7', 'et', 'real', 'mopt', 'shpp', 'mshmid',
                      'upload', 'nread', 'eread', 'cm', 'type', 'cmsel', 
                      'fvmesh', 'mat', 'edele', 'emid', 'list_files',
                      'etdele', 'post1']:
        setattr(MockMAPDL, func_name, new_member_creator(func_name))
        
    return mapdl
        
        