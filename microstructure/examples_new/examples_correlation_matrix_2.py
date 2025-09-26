import numpy as np
import ast
import matplotlib.pyplot as plt
import os
import fnmatch
import pandas as pd
import seaborn as sn

interface_fractions_Pore_ZrO2 = []
interface_fractions_Pore_Al2O3 = []
interface_fractions_ZrO2_ZrO2 = []
interface_fractions_ZrO2_Al2O3 = []
interface_fractions_Al2O3_Al2O3 = []

mean_chord_length_Porosity = []
mean_chord_length_ZrO2 = []
mean_chord_length_Al2O3 = []

variance_Porosity = []
variance_ZrO2 = []
variance_Al2O3 = []

volume_fraction = []

#-----------------------------------------------------------------------------

path_for_results = 'U:/01_Ravi_Phanindra/mpaut/examples_new/Airfox_Output'

#-----------------------------------------------------------------------------

'''
This function creates list of data for 
'interface_fractions', 
'mean_chord_length', 
'variance', 
'volume_fraction'
from the 'info.txt' file generated while creating 'GeoVal' structure.
 
This list of data is used for creating
 Correlation martrix with the 'Elastic Properties'
of microstructure.

'''

def data_function(path):
    # if os.path.isfile('path'):
        f = open(path) 
        data = f.read()
        dic1 = ast.literal_eval(data.replace('array', ''))
        keys1 = dic1.keys()
        print('Keys in the Dictionary of info.txt file is :',keys1)
        print("-------------------------------------------------------")
        
        val1 =  dic1['chord_length_analysis']
        print('Dictionary of chord_length_analysis is :',val1)
        print("-------------------------------------------------------")
        
        
        val2 =  val1['interface_fractions']
        print('Dictionary of interface_fractions :',val2)
        print("-------------------------------------------------------")
        
        
        print('Different phases at interface fractions are : ',val2.keys())
        print("-------------------------------------------------------")
        
        print('Volume Percentage of different phases at interface fractions are :',val2.values())
        print("-------------------------------------------------------")
        
        
        val3 = val1['phase_chord_lengths']
        print('Dictionary of phase_chord_lengths :',val3)
        print("-------------------------------------------------------")  
        
        phase0 = val3[0]
        print('Dictionary of phase 0 i.e POROSITY:',phase0)
        print("-------------------------------------------------------") 
        
        phase4 = val3[4]
        print('Dictionary of phase 4 i.e ZrO2:',phase4)
        print("-------------------------------------------------------") 
        
        phase10 = val3[10]
        print('Dictionary of phase 10 i.e Al2O3:',phase10)
        print("-------------------------------------------------------") 
        
        ###-------------------------------------------------------------------
        key_to_lookup0 = (0, 4)
        if key_to_lookup0 in val2:
            IFC_Pore_ZrO2 = val2[(0, 4)]
        else :
            IFC_Pore_ZrO2 = 0
           
        key_to_lookup5 = (0, 10)
        if key_to_lookup5 in val2:
            IFC_Pore_Al2O3 = val2[(0, 10)]
        else :
            IFC_Pore_Al2O3 = 0
        
        key_to_lookup1 = (4, 4)
        if key_to_lookup1 in val2:
              print("Key exists")
              IFC_ZrO2_ZrO2 = val2[(4, 4)]
        else:
              print("Key does not exist")
              IFC_ZrO2_ZrO2 = 0
        
        key_to_lookup4 = (4, 10)
        if key_to_lookup4 in val2:
            IFC_ZrO2_Al2O3 = val2[(4, 10)]
        else :
             IFC_ZrO2_Al2O3 = 0
             
        key_to_lookup2 = (10, 10)
        if key_to_lookup2 in val2:
            IFC_Al2O3_Al2O3 = val2[(10, 10)]
        else :
            IFC_Al2O3_Al2O3 = 0
        ###-------------------------------------------------------------------    
        
        print('Interface fraction of Pores with ZrO2:',IFC_Pore_ZrO2)
        print("-------------------------------------------------------") 
        
        MCL_Porosity = phase0['mean_chord_length']
        var_Porosity = phase0['variance']
        print('Mean chord length of Porosity phase:',MCL_Porosity)
        print('Variance of Porosity phase:',var_Porosity)
        print("-------------------------------------------------------")
        MCL_ZrO2 = phase4['mean_chord_length']
        var_ZrO2 = phase4['variance']
        print('Mean chord length of ZrO2 phase:',MCL_ZrO2)
        print('Variance of ZrO2 phase:',var_ZrO2)
        print("-------------------------------------------------------")
        MCL_Al2O3 = phase10['mean_chord_length']
        var_Al2O3 = phase10['variance']
        print('Mean chord length of Al2O3 phase:',MCL_Al2O3)
        print('Variance of Porosity Al2O3:',var_Al2O3)
        print("-------------------------------------------------------")
        
        
        interface_fractions_Pore_ZrO2.append(IFC_Pore_ZrO2)
        interface_fractions_Pore_Al2O3.append(IFC_Pore_Al2O3)
        interface_fractions_ZrO2_ZrO2.append(IFC_ZrO2_ZrO2)
        interface_fractions_ZrO2_Al2O3.append(IFC_ZrO2_Al2O3)
        interface_fractions_Al2O3_Al2O3.append(IFC_Al2O3_Al2O3)
        
        mean_chord_length_Porosity.append(MCL_Porosity)
        mean_chord_length_ZrO2.append(MCL_ZrO2)
        mean_chord_length_Al2O3.append(MCL_Al2O3)
        
        variance_Porosity.append(var_Porosity)
        variance_ZrO2.append(var_ZrO2)
        variance_Al2O3.append(var_Al2O3)
        
        return interface_fractions_Pore_ZrO2, interface_fractions_Pore_Al2O3, interface_fractions_ZrO2_ZrO2,\
               interface_fractions_ZrO2_Al2O3, interface_fractions_Al2O3_Al2O3, mean_chord_length_Porosity, \
               mean_chord_length_ZrO2, mean_chord_length_Al2O3, variance_Porosity, variance_ZrO2, variance_Al2O3

################################################################################                             
  
ZrO2 = []
Al2O3 = []
Pores = []
components = []


Youngs_modulus_Hill = []
Shear_modulus_Hill  = []
Bulk_modulus_Hill   = []
Poissons_ratio_Hill = []

Youngs_modulus_Reuss = []
Shear_modulus_Reuss  = []
Bulk_modulus_Reuss   = []
Poissons_ratio_Reuss = []

Youngs_modulus_voigt  = []
Shear_modulus_voigt   = []
Bulk_modulus_voigt    = []
Poissons_ratio_voigt  = []


def results(path):
        f = open(path) 
        data = f.read()
        dic1 = ast.literal_eval(data.replace('array', ''))
        for key in dic1 :   
            key1 = dic1.keys()
            print('^^^^^^^^^^^^^^^^^^^^^^^START^^^^^^^^^^^^^^^^^^^^^^^^^')
            print('All components and their Volume fractions as keys :',key1)
            print("-------------------------------------------------------")
            val1 =  dic1[key]
            print('Elasticity results for particular volume fraction :',val1)
            print("-------------------------------------------------------")
            
            print('')
            folder_path = val1['data_folder']
            print('PATH OF THE FOLDER is :', folder_path)
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            print('')
            
            #------------------------------------------------------------------
            # Giving path for getting acess to info.txt file saved in different folders
            #------------------------------------------------------------------
            
            replace_path3 = folder_path.replace("\\", "/")
            replace_path2 = replace_path3.replace("Airfox_Output_completed", "Airfox_Output")
            replace_path = replace_path2.replace("Airfox_list_Output_completed", "Airfox_Output")    
            print('Replaced path ',replace_path)
            basic_path = 'U:/01_Ravi_Phanindra/mpaut/examples_new'
            path_for_info_file = basic_path+'/'+replace_path+'/'+'info.txt'
            data_function(path_for_info_file) # calling of the data_function
            #------------------------------------------------------------------
            
            key2 = val1.keys()
            print('Properties as keys for particular volume fraction :',key2)
            print("-------------------------------------------------------")
            
            val2 = val1['hill_avg']
            Youngs_modulus_Hill.append(val2['E'])
            Shear_modulus_Hill.append(val2['G'])
            Bulk_modulus_Hill.append(val2['K'])
            Poissons_ratio_Hill.append(val2['nu'])
            print('Dictionary of different Modulus and Poissons ratio for Hill_Avg :',val2)
            print("-------------------------------------------------------")
            
            val2_Reuss = val1['reuss_avg']
            Youngs_modulus_Reuss.append(val2_Reuss['E'])
            Shear_modulus_Reuss.append(val2_Reuss['G'])
            Bulk_modulus_Reuss.append(val2_Reuss['K'])
            Poissons_ratio_Reuss.append(val2_Reuss['nu'])
            print('Dictionary of different Modulus and Poissons ratio for Reuss_Avg :',val2_Reuss)
            print("-------------------------------------------------------")
            
            val2_voigt = val1['voigt_avg']
            Youngs_modulus_voigt.append(val2_voigt['E'])
            Shear_modulus_voigt.append(val2_voigt['G'])
            Bulk_modulus_voigt.append(val2_voigt['K'])
            Poissons_ratio_voigt.append(val2_voigt['nu'])
            print('Dictionary of different Modulus and Poissons ratio for Voigt_Avg :',val2_voigt)
            print("-------------------------------------------------------")
                  
            # Extracting the volume fraction of all components  
            dic2 = str(key)
            print(key)
            print(dic2)
            d = dict(x.split(":") for x in dic2.split(", "))
            print('dictionary of volume fraction of each components is',d)
            
            components = list(d.keys())
            ZrO2.append(d['ZrO2'])
            Al2O3.append(d['Al2O3'])
            Pores.append(d['Pores'])
            print('%%%%%%%%%%%%%%%%%   END    %%%%%%%%%%%%%%%%%%%')
      
        
        return Youngs_modulus_Hill, Shear_modulus_Hill, Bulk_modulus_Hill, Poissons_ratio_Hill, \
           Youngs_modulus_Reuss, Shear_modulus_Reuss, Bulk_modulus_Reuss, Poissons_ratio_Reuss, \
           Youngs_modulus_voigt, Shear_modulus_voigt, Bulk_modulus_voigt, Poissons_ratio_voigt, \
           ZrO2, Al2O3, Pores, components
            

#-----------------------------------------------------------------------------
###############################################################################
''' This is the function that 
  iterates over all the folders in the given path '''

def scan_folder(parent):
    # iterate over all the files in directory 'parent'
    for file_name in os.listdir(parent):
        if file_name.endswith(".txt"):
            # if it's a txt file, print its name (or do whatever you want)
            if file_name == 'results.txt':    
                    current_path2 = "".join((parent, "/", file_name))
                    results(current_path2)
                    
        current_path = "".join((parent, "/", file_name))
        if os.path.isdir(current_path):
                # if we're checking a sub-directory, recursively call this method
                scan_folder(current_path)
                
############################################################################### 

#------------------------------------------------------------------------------
# # Calling of the function 
scan_folder(path_for_results)
#------------------------------------------------------------------------------

# Converting volumefraction from string to list of float values
ZrO2 = list(map(float, ZrO2))
Al2O3 = list(map(float, Al2O3))
Pores = list(map(float, Pores))

#------------------------------------------------------------------------------
#########################    END OF DATA HANDLING    ##########################


#------------------------------------------------------------------------------
#-------------------------------PLOTTINGS--------------------------------------
#------------------------------------------------------------------------------
''' Plotting of correlation matrices '''  
#------------------------------------------------------------------------------

data1 = {'Pore_ZrO2': interface_fractions_Pore_ZrO2,
        'Pore_Al2O3': interface_fractions_Pore_Al2O3,
        'ZrO2_ZrO2': interface_fractions_ZrO2_ZrO2,
        'ZrO2_Al2O3' : interface_fractions_ZrO2_Al2O3,
        'Al2O3_Al2O3' : interface_fractions_Al2O3_Al2O3,
        'Youngs_modulus_Hill' : Youngs_modulus_Hill,
        'Shear_modulus_Hill' : Shear_modulus_Hill,
        'Bulk_modulus_Hill' : Bulk_modulus_Hill,
        'Poissons_ratio_Hill' :  Poissons_ratio_Hill
        }

df = pd.DataFrame(data1,columns=['Pore_ZrO2','Pore_Al2O3','ZrO2_ZrO2','ZrO2_Al2O3', 'Al2O3_Al2O3',   
                        'Youngs_modulus_Hill', 'Shear_modulus_Hill', 'Bulk_modulus_Hill','Poissons_ratio_Hill'])

corrMatrix = df.corr()
sn.heatmap(corrMatrix, annot=True).set_title('Correlation matrix of Properties with Interface fractions of constituents')
plt.show()

data2 = {
        'MCL_Porosity': mean_chord_length_Porosity,
        'MCL_ZrO2': mean_chord_length_ZrO2,
        'MCL_Al2O3': mean_chord_length_Al2O3,
        'Youngs_modulus_Hill' : Youngs_modulus_Hill,
        'Shear_modulus_Hill' : Shear_modulus_Hill,
        'Bulk_modulus_Hill' : Bulk_modulus_Hill,
        'Poissons_ratio_Hill' :  Poissons_ratio_Hill
        }

df = pd.DataFrame(data2,columns=[ 'MCL_Porosity', 'MCL_ZrO2', 'MCL_Al2O3',
                        'Youngs_modulus_Hill', 'Shear_modulus_Hill', 'Bulk_modulus_Hill','Poissons_ratio_Hill'])

corrMatrix = df.corr()
sn.heatmap(corrMatrix, annot=True).set_title('Correlation matrix of Properties with Mean Chord Length of constituents')
plt.show()

data3 = {
        'Var_Porosity' : variance_Porosity,
        'Var_ZrO2' : variance_ZrO2,
        'Var_Al2O3' : variance_Al2O3, 
        'Youngs_modulus_Hill' : Youngs_modulus_Hill,
        'Shear_modulus_Hill' : Shear_modulus_Hill,
        'Bulk_modulus_Hill' : Bulk_modulus_Hill,
        'Poissons_ratio_Hill' :  Poissons_ratio_Hill
        }

df = pd.DataFrame(data3,columns=[ 'Var_Porosity', 'Var_ZrO2', 'Var_Al2O3',
                        'Youngs_modulus_Hill', 'Shear_modulus_Hill', 'Bulk_modulus_Hill','Poissons_ratio_Hill'])

corrMatrix = df.corr()
sn.heatmap(corrMatrix, annot=True).set_title('Correlation matrix of Properties with Variance of constituents')
plt.show()

#------------------------------------------------------------------------------
data_VF3 = {
        'Vol_Frac_of_ZrO2' : ZrO2,
        'Vol_Frac_of_Al2O3' : Al2O3,
        'Vol_Frac_of_Pores' : Pores, 
        'Youngs_modulus_Hill' : Youngs_modulus_Hill,
        'Shear_modulus_Hill' : Shear_modulus_Hill,
        'Bulk_modulus_Hill' : Bulk_modulus_Hill,
        'Poissons_ratio_Hill' :  Poissons_ratio_Hill
        }

df = pd.DataFrame(data_VF3,columns=['Vol_Frac_of_ZrO2', 'Vol_Frac_of_Al2O3', 'Vol_Frac_of_Pores',
                        'Youngs_modulus_Hill', 'Shear_modulus_Hill', 'Bulk_modulus_Hill','Poissons_ratio_Hill'])

corrMatrix = df.corr()
sn.heatmap(corrMatrix, annot=True).set_title('Correlation matrix of Hill Properties with Volume Fractions of constituents')
plt.show()

##------------------------------------------------------------------------------