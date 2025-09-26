import numpy as np
import ast
import matplotlib.pyplot as plt

'''
Plots Youngs modulus, Shear modulus, Bulk modulus, Poissons ratio for 
Hill Average, Reuss average, Voigt average methods

Input Parameter : 'results_elasticity.txt' file in the current folder

'''


f = open('results_elasticity.txt') 
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
    # Pores.append(d['Pores'])

# Converting volumefraction from string to list of float values
ZrO2 = list(map(float, ZrO2))
Al2O3 = list(map(float, Al2O3))
Pores = list(map(float, Pores))

print('List of Voigt Elastic Modulus for different volume fraction',Youngs_modulus_voigt)
print('List of Voigt Shear Modulus for different volume fraction',Shear_modulus_voigt)
print('List of Voigt Bulk Modulus for different volume fraction',Bulk_modulus_voigt)
print('List of Voigt Poissons ratio for different volume fraction',Poissons_ratio_voigt)
print('List  of names of all componenets',components)
print('List of volume fractions of Zirconium Oxide',ZrO2)
print('List of volume fractions of Alluminium Oxide',Al2O3)
print('List of volume fractions of Pores',Pores)

# Plotting of Properties

plt.subplot(4, 1, 1)
plt.scatter(ZrO2, Youngs_modulus_Hill)
plt.scatter(ZrO2, Youngs_modulus_Reuss)
plt.scatter(ZrO2, Youngs_modulus_voigt)

# plt.title('Elastic properties')
plt.xlabel('Volume fraction of ZrO2 in %')
plt.ylabel('Modulus of Elasticity in Gpa')
plt.legend(["Hill_Avg", "reuss_avg", "voigt_avg"])

plt.subplot(4, 1, 2)
plt.scatter(ZrO2, Shear_modulus_Hill)
plt.scatter(ZrO2, Shear_modulus_Reuss)
plt.scatter(ZrO2, Shear_modulus_voigt)

# plt.title('Elastic properties')
plt.xlabel('Volume fraction of ZrO2 in %')
plt.ylabel('Shear Modulus in Gpa')
plt.legend(["Hill_Avg", "reuss_avg", "voigt_avg"])

plt.subplot(4, 1, 3)
plt.scatter(ZrO2, Bulk_modulus_Hill)
plt.scatter(ZrO2, Bulk_modulus_Reuss)
plt.scatter(ZrO2, Bulk_modulus_voigt)

# plt.title('Elastic properties')
plt.xlabel('Volume fraction of ZrO2 in %')
plt.ylabel('Bulk Modulus in Gpa')
plt.legend(["Hill_Avg", "reuss_avg", "voigt_avg"])


plt.subplot(4, 1, 4)
plt.scatter(ZrO2, Poissons_ratio_Hill)
plt.scatter(ZrO2, Poissons_ratio_Reuss)
plt.scatter(ZrO2, Poissons_ratio_voigt)

# plt.title('Poissons ratio')
plt.xlabel('Volume fraction of ZrO2 in %')
plt.ylabel('Poissons ratio')
plt.legend(["Hill_Avg", "reuss_avg", "voigt_avg"])

plt.show()


######################################################################################
### Curve fitting


def func(x,a,b,c): 
    return a*x+b*x+c
#### Gradient Descent is an algorithm to minimize the function by optimizing the parameters
#### our function is of the form y =a*x**2+b*x+c

def hypothisis(x,a,b,c): # This is the function that we assume that fits to the our data
    return a + b*x + c*x**0.3

## cost function we are taking here for finding parametrs of a,b,c is MSE
def cost_fun(x,a,b,c):  # This is the function that we want to minimize
    MSE = np.average(y-hypothisis(x,a,b,c))**2
    #return MSE

def derivat_cost(x,a,b,c,y):
    df_cost_da = np.average(2*(hypothisis(x,a,b,c) - y)*1)
    df_cost_db = np.average(2*(hypothisis(x,a,b,c) - y)*x)
    df_cost_dc = np.average(2*(hypothisis(x,a,b,c) - y)*x*0.3)
    return df_cost_da , df_cost_db, df_cost_dc

### Parameter optimization or update logic using gradient descent method
def gradient_descent_step(x , a_old, b_old , c_old ,learning_rate, y):
    df_cost_da ,df_cost_db ,df_cost_dc = derivat_cost(x, a_old, b_old , c_old, y)
    # formulae is new_value = old+value - learning_rate * slope
    a_new = a_old - learning_rate*df_cost_da
    b_new = b_old - learning_rate*df_cost_db
    c_new = c_old - learning_rate*df_cost_dc
    return a_new , b_new , c_new

def optimum_parameters(x_training, y_training, y_testing, method):
        ### Finding the best values of parameters in the function y =a*x**2+b*x+c
        learning_rate = 0.1
        N = 10000  # Maximum Number of iterations to check
        precission =  1e-6
        coeficients = [[0, 0.0, 0.0]] # innitialising start values for the coefficients a ,b ,c
        for j in range(N-1):
            old_a ,old_b ,old_c = coeficients[-1]
            a_new , b_new, c_new = gradient_descent_step(x_training , old_a , old_b , old_c , learning_rate, y_training)
            #print('updated parameters for the function are ', 'a value',  a_new ,'b value' , b_new , 'c value ', c_new )
            coeficients.append([a_new , b_new , c_new])
            #js.append(cost_fun(new_k))
            if (abs(a_new - old_a)<precission).any() and (abs(b_new - old_b)< precission).any() and (abs(c_new - old_c)< precission).any() :
            # if abs(a_new - old_a)<precission and abs(b_new - old_b)< precission and abs(c_new - old_c)< precission:  
                print('iteration finished in total {} iterations '.format(j))
                total_iteration = j+1
                break
        
        a_f , b_f ,c_f = coeficients[-1]
        print("These are the optimized final parameters ",a_f , b_f , c_f)
        y_learned = hypothisis(x_training , a_f , b_f ,c_f)
        
        fig , ax = plt.subplots()
        ax.plot(x_training , y_training, 'o', color = 'red', label = 'training data')
        ax.plot(x_testing , y_testing , 'o', color = 'blue', label = 'test_data')
        ax.plot(x_training , y_learned,  color = 'green', label = 'learned data')
        ax.legend()
        plt.title(label = method)
        plt.show()

        return y_learned

### Splitting the total number of data points into 60% training and 40% testing data
number_total_data = len(ZrO2) # ZrO2 is replaced with Al2O3 if we want depenedence of properties on percentage of Al2O3 
                              # ZrO2 is replaced with Pores if we want depenedence of properties on percentage of Pores
split = 0.6
num_training_data = int(split*number_total_data)
print(num_training_data)
num_testing_data = number_total_data - num_training_data
print(num_testing_data)

### seperation of the training and testing data into two lists
### we took an mask array inorder to do this task
mask = np.zeros(number_total_data , dtype=bool)
print(mask)
mask[:num_training_data] = True
np.random.seed(10)
np.random.shuffle(mask)
print(mask)

###Converting list to array
# arr = np.array(lst)
ZrO2 = np.array(ZrO2)
Al2O3 = np.array(Al2O3)
Pores = np.array(Pores)

Youngs_modulus_Hill = np.array(Youngs_modulus_Hill)
Shear_modulus_Hill = np.array(Shear_modulus_Hill)
Bulk_modulus_Hill = np.array(Bulk_modulus_Hill)
Poissons_ratio_Hill = np.array(Poissons_ratio_Hill)

Youngs_modulus_Reuss = np.array(Youngs_modulus_Reuss)
Shear_modulus_Reuss = np.array(Shear_modulus_Reuss)
Bulk_modulus_Reuss = np.array(Bulk_modulus_Reuss)
Poissons_ratio_Reuss = np.array(Poissons_ratio_Reuss)

Youngs_modulus_voigt = np.array(Youngs_modulus_voigt)
Shear_modulus_voigt = np.array(Shear_modulus_voigt)
Bulk_modulus_voigt = np.array(Bulk_modulus_voigt)
Poissons_ratio_voigt = np.array(Poissons_ratio_voigt)

###getting training data points into x_training and y_training list
x_training = ZrO2[mask] # ZrO2 is replaced with Al2O3 if we want depenedence of properties on percentage of Al2O3 
                        # ZrO2 is replaced with Pores if we want depenedence of properties on percentage of Pores
y_training_Hill = [Youngs_modulus_Hill[mask], Shear_modulus_Hill[mask],  Bulk_modulus_Hill[mask],  Poissons_ratio_Hill[mask]]
y_training_Reuss = [Youngs_modulus_Reuss[mask], Shear_modulus_Reuss[mask],  Bulk_modulus_Reuss[mask],  Poissons_ratio_Reuss[mask]]
y_training_voigt = [Youngs_modulus_voigt[mask], Shear_modulus_voigt[mask],  Bulk_modulus_voigt[mask],  Poissons_ratio_voigt[mask]]


###getting testing data points into x_testing  and y_testing list
x_testing = ZrO2[~mask] # ZrO2 is replaced with Al2O3 if we want depenedence of properties on percentage of Al2O3 
                        # ZrO2 is replaced with Pores if we want depenedence of properties on percentage of Pores
y_testing_Hill = [Youngs_modulus_Hill[~mask], Shear_modulus_Hill[~mask],  Bulk_modulus_Hill[~mask],  Poissons_ratio_Hill[~mask]]
y_testing_Reuss = [Youngs_modulus_Reuss[~mask], Shear_modulus_Reuss[~mask],  Bulk_modulus_Reuss[~mask],  Poissons_ratio_Reuss[~mask]]
y_testing_voigt = [Youngs_modulus_voigt[~mask], Shear_modulus_voigt[~mask],  Bulk_modulus_voigt[~mask],  Poissons_ratio_voigt[~mask]]


for i in range(len(y_training_Hill)):
    y_learned = optimum_parameters(x_training, y_training_Hill[i], y_testing_Hill[i], 'Hill_Avg')

for i in range(len(y_training_Reuss)):
    y_learned = optimum_parameters(x_training, y_training_Reuss[i], y_testing_Reuss[i], 'Reuss_Avg')
    
for i in range(len(y_training_voigt)):
    y_learned = optimum_parameters(x_training, y_training_voigt[i], y_testing_voigt[i], 'voigt_Avg')    
    
    
###############################################################################
# Curve fitting using scikit library    
from sklearn.linear_model import LinearRegression
regressor = LinearRegression()

for i in range(len(y_training_Hill)): # If want to fit curve for other averaging methods
                                      # give the name of respective method to arguments
    regressor.fit(x_training.reshape(-1, 1), y_training_Hill[i].reshape(-1, 1))
    y_predicted = regressor.predict(x_training.reshape(-1, 1))
    
    r2_score = regressor.score(x_testing.reshape(-1, 1),y_testing_Hill[i].reshape(-1, 1))
    print(r2_score*100,'%') 
    
    plt.scatter(x_testing, y_testing_Hill[i],  color='black',label = 'testing data')
    plt.scatter(x_training, y_training_Hill[i],  color='red', label = 'training data')
    plt.plot(x_training, y_predicted, color='blue', linewidth=1, label = 'learned data')

    plt.legend()
    plt.show()
    
###############################################################################   