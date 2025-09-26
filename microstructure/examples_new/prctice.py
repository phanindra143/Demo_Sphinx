import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import ast


'''
Plots Youngs modulus, Shear modulus, Bulk modulus, Poissons ratio for 
Hill Average, Reuss average, Voigt average methods

Input Parameter : 'results_elasticity.txt' file in the current folder

'''


f = open('results_elasticity1.txt') 
data = f.read()
dic1 = ast.literal_eval(data.replace('array', ''))

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


for key in dic1 :   
    key1 = dic1.keys()
    print('All components and their Volume fractions as keys :',key1)
    print("-------------------------------------------------------")
    val1 =  dic1[key]
    print('Elasticity results for particular volume fraction :',val1)
    print("-------------------------------------------------------")
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
    
    components = list(d.keys())
    ZrO2.append(d['ZrO2'])
    Al2O3.append(d['Al2O3'])
    Pores.append(d['Pores'])

# Converting volumefraction from string to list of float values
ZrO2 = list(map(float, ZrO2))
Al2O3 = list(map(float, Al2O3))
Pores = list(map(float, Pores))


def func(x, a, b, c):
    # return a * np.exp(-b * x) + c
    return a*x + b*x + c

# # Define the data to be fit with some noise:


# xdata = np.linspace(0, 4, 50)
# y = func(xdata, 2.5, 1.3, 0.5)
# np.random.seed(1729)
# # y_noise = 0.2 * np.random.normal(size=xdata.size)
# ydata = y + y_noise
# plt.plot(xdata, ydata, 'b-', label='data')

# Fit for the parameters a, b, c of the function func:


popt, pcov = curve_fit(func,ZrO2, Youngs_modulus_Hill)
popt

plt.plot(ZrO2, func(ZrO2, *popt), 'r-',
         label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))

# Constrain the optimization to the region of 0 <= a <= 3, 0 <= b <= 1 and 0 <= c <= 0.5:


popt, pcov = curve_fit(func, ZrO2,  Youngs_modulus_Hill, bounds=(0, [3., 1., 0.5]))
popt

plt.plot( ZrO2, func( ZrO2, *popt), 'g--',
         label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))



plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.show()

