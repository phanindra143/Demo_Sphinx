import numpy as np
import matplotlib.pyplot as plt

# def func(x,a,b,c): 
#     return a*x+b*x+c
# #### Gradient Descent is an algorithm to minimize the function by optimizing the parameters
# #### our function is of the form y =a*x**2+b*x+c

def hypothisis(x,a,b,c): # This is the function that we assume that fits to the our data
    return a + b*x + c*x

## cost function we are taking here for finding parametrs of a,b,c is MSE
def cost_fun(x,a,b,c):  # This is the function that we want to minimize
    MSE = np.average(y-hypothisis(x,a,b,c)**2)
    #return MSE

def derivat_cost(x,a,b,c,y):
    df_cost_da = np.average(2*(hypothisis(x,a,b,c) - y)*1)
    df_cost_db = np.average(2*(hypothisis(x,a,b,c) - y)*x)
    df_cost_dc = np.average(2*(hypothisis(x,a,b,c) - y)*x**2)
    return df_cost_da , df_cost_db, df_cost_dc

### Parameter optimization or update logic using gradient descent method
def gradient_descent_step(x , a_old, b_old , c_old ,learning_rate, y):
    df_cost_da ,df_cost_db ,df_cost_dc = derivat_cost(x, a_old, b_old , c_old, y)
    # formulae is new_value = old+value - learning_rate * slope
    a_new = a_old - learning_rate*df_cost_da
    b_new = b_old - learning_rate*df_cost_db
    c_new = c_old - learning_rate*df_cost_dc
    return a_new , b_new , c_new

'''
number_total_data = 50    
x = np.linspace(-1 , 3 , number_total_data)
print('these are total initial range of values along x', x)
func_true = func(x , 0.3, 0.5, -1)

### The below step is to creat noisy data around the true function along the range of x
np.random.seed(1)
y_observed = func_true + np.random.normal(scale=0.6 , size=x.shape)  
#y_observed = func_true +  np.random.choice(range(x.size), size = 50,   replace=True) # This is Functions for sequences
#y_observed = func_true +  np.random.choice(x,replace= False)
#y_observed =  func_true + np.random.random()
#y_observed = func_true +  np.random.randint(-1,4,50)
'''

### Splitting the total number of data points into 60% training and 40% testing data
number_total_data = len(ZrO2)
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
np.random.seed(2)
np.random.shuffle(mask)
print(mask)

###getting training data points into x_training and y_training list
# arr = np.array(lst)
ZrO2 = np.array(ZrO2)
ZrO2_training = ZrO2[mask]
Youngs_modulus_Hill = np.array(Youngs_modulus_Hill)
Youngs_modulus_Hill_training = Youngs_modulus_Hill[mask]
# print('this is list of the training points co-ordinates list in x axis',ZrO2_training)
# print('this is list of the training points co-ordinates list in y axis',Youngs_modulus_Hill_training)

###getting testing data points into x_testing  and y_testing list
ZrO2_testing = ZrO2[~mask]
Youngs_modulus_Hill_testing = Youngs_modulus_Hill[~mask]
# print('this is list of the testing points co-ordinates list in x axis',ZrO2_testing)
# print('this is list of the testing points co-ordinates list in y axis',Youngs_modulus_Hill_testing)

### Finding the best values of parameters in the function y =a*x**2+b*x+c
learning_rate = 0.01
N = 1000  # Maximum Number of iterations to check
precission =  1e-4
coeficints = [[0, 0.1, 0.1]] # innitialising start values for the coefficients a ,b ,c
for j in range(N-1):
    old_a ,old_b ,old_c = coeficints[-1]
    a_new , b_new, c_new = gradient_descent_step(ZrO2_training , old_a , old_b , old_c , learning_rate, Youngs_modulus_Hill_training)
    #print('updated parameters for the function are ', 'a value',  a_new ,'b value' , b_new , 'c value ', c_new )
    coeficints.append([a_new , b_new , c_new])
    #js.append(cost_fun(new_k))
    if (abs(a_new - old_a)<precission).any() and (abs(b_new - old_b)< precission).any() and (abs(c_new - old_c)< precission).any() :
        print('iteration finished in total {} iterations '.format(j))
        total_iteration = j+1
        break

a_f , b_f ,c_f = coeficints[-1]
print("These are the optimized final parameters ",a_f , b_f , c_f)
y_learned = hypothisis(ZrO2_training , a_f , b_f ,c_f)


fig , ax = plt.subplots()
# ax.plot(x,func_true, '--', color = 'blue', label = 'true_function')
# ax.plot(x,y_observed, 'o', color = 'green', label = 'true_data incl noise')
ax.plot(ZrO2_training , Youngs_modulus_Hill_training, 'o', color = 'red', label = 'training data')
# ax.plot(x_testing , y_testing, 'o', color = 'yellow', label = 'test_data')
ax.plot(ZrO2_training , y_learned, 'o', color = 'black', label = 'learned data')
ax.legend()
plt.show()
