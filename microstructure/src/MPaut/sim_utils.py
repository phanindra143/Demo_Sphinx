# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 14:46:54 2021

@author: pirkelma
"""
import numpy as np


def compute_stiffness_matrix_svd(epsilon_d, sigma_d):
    """Compute the stiffness matrix for the given stress and strain measurements.
    
    This implements the same algorithm as used in the program Crystal 
    (originally developed in Delphi by F. Raether).
    
    The algorithm works as follows: We are given measurements of strain 
    tensors ``epsilon_i`` and corresponding stresses ``sigma_i``, where each 
    tensor includes the following:
        ``sigma_i   = [sxx syy szz syz sxz sxy]``
        ``epsilon_i = [exx eyy ezz eyz exz exy]``
        
    We want to compute the stiffness tensor ``C`` which best maps the strains 
    to the stresses, i.e.
       ``sigma_i = C * epsilon_i    for all i``
       
    The problem is solved by writing ``C`` as a vector ``c`` and creating the 
    linear system 
      ``s = E * c``
    where ``E`` is a matrix formed from the strain tensors, ``s`` is a vector 
    formed of the strain tensors and ``c`` is the unknown vector with the 
    components of the stiffness matrix (for details look at the code).    
    
    The system is solved by computing the singular value decomposition
        ``E = U * S * V^T``
    and using it to solve the system for ``c``, i.e.:
        ``c = V * S^-1 * U^T * s``
        
    Parameters
    ----------
    epsilon_d : list
        List of ``n`` (usually six) measurements of the strains. Each entry
        of the list need to be a dict which contains the six independend 
        components of the strain tensor epsilon_i in the following format:
        ``epsilon_d = [{'xx': -0.02, 'yy': -0.02, 'zz': 0.14, 'xy': -0.005, 'yz': -0.005, 'xz': -0.008}, 
        {'xx': -0.02, 'yy': 0.14, 'zz': -0.02, 'xy': -0.01, 'yz': -0.003, 'xz': -0.002},
        ... ]``
    sigma_d : list
        List of ``n`` (usually six) measurements of the stresses. Each entry
        of the list need to be a dict which contains the six independend 
        components of the stress tensor sigma_i in the following format:
        ``sigma_d = [{'xx': 7.31, 'yy': 7.31, 'zz': 38.66, 'xy': -0.67, 'yz': -0.57, 'xz': -0.94},
        {'xx': 6.97, 'yy': 40.0, 'zz': 7.08, 'xy': -1.08, 'yz': -0.30, 'xz': -0.23}, 
         ... ]``

        
    Returns
    -------
    C : numpy.array
        Resulting stiffness tensor ``C``.
    svd_ratio : float
        Ratio of the minimum and maximum singular values from the singular
        value decomposition of the matrix ``E``.
    """
    order = ['xx', 'yy', 'zz', 'yz', 'xz', 'xy']

    # create vector s
    vec = []
    for d in sigma_d:
        # the vector sigma just contains the independent components of the
        # stress tensors sigma_i stacked together, i.e.
        # sigma = [sigma_0, sigma_1, ..., sigma_n]
        # this gives a vector of dimension (6 * n) x 1
        # where n is the number of stress tensors
        vec.append([d[o] for o in order])
    sig = np.hstack(vec)

    # create matrix E
    mat = []
    for d in epsilon_d:
        # create blocks from strain tensor (exx eyy ezz eyz exz exy) 
        #for each load step (1 - 6) a block contains the following data
        # exx eyy ezz eyz exz exy   0 ...                                                       0
        #   0 exx   0   0   0   0 eyy ezz eyz exz exy   0 ...                                   0
        #   0   0 exx   0   0   0   0 eyy   0   0   0 ezz eyz exz exy   0 ...                   0
        #   ...
        #   0                   0 exx   0   0   0   0 eyy   0   0   0 ezz   0   0 eyz   0 exz exy
        block = np.zeros((6,21))
        for row in range(6):
            offsets = [row] + list(range(4, 4-row, -1)) + [0] * (4 - row + 1)
            for j in range(6):
                col = sum(offsets[:j+1]) + j
                block[row, col] = d[order[j]]
        mat.append(block)

    # stack blocks to create matrix for linear system
    #  s = E * c
    # we want to find the vector c that best satisfies the system
    # this vector will correspond to the entries of the stiffness matrix C
    E = np.vstack(mat)

    # compute svd:  E = U * S * V^T
    U, S, Vh = np.linalg.svd(E)
    
    svd_ratio = S.min() / S.max()

    # compute entries of the stiffness matrix:  c = V * S^-1 * U^T * sig
    # here we only need to consider the first 21 entries of the vector 
    # v = U^T * sig
    c_vals = Vh.T @ np.linalg.inv(np.diag(S)) @ (U.T @ sig)[:21]
    
    # fill values in the matrix
    C = np.zeros((6,6))
    C[np.triu_indices(6)] = c_vals  # fill diagonal and upper triangular matrix with values
    C += np.triu(C, 1).T            # add transposed of upper triangular to get full matrix

    return C, svd_ratio

def compute_stiffness_matrix_simple(eps_d, sig_d, mandel_scaling=False):
    order = ['xx', 'yy', 'zz', 'yz', 'xz', 'xy']

    # create matrix of stress tensor values
    sig = []
    for i, d in sig_d.items():
        # the vector sigma just contains the independent components of the
        # stress tensors sigma_i stacked next to each other, i.e.
        # sigma = [sigma_0  sigma_1 ... sigma_n]
        # where n is the number of stress tensors
        sig.append([d[o] for o in order])
    sig = np.vstack(sig).T
    
    # create matrix of strain tensor values
    eps = []
    for i, d in eps_d.items():
        # the vector sigma just contains the independent components of the
        # stress tensors sigma_i stacked next to each other, i.e.
        # sigma = [sigma_0  sigma_1 ... sigma_n]
        # where n is the number of stress tensors
        eps.append([d[o] for o in order])
    eps = np.vstack(eps).T
    
    if mandel_scaling:
        sig[3:,:] = sig[3:,:] * np.sqrt(2)
        eps[3:,:] = eps[3:,:] * np.sqrt(2)
    
    # compute svd
    #  eps = U * S * V^T
    U, S, Vh = np.linalg.svd(eps)
    
    # compute stiffness matrix 
    #  C = sigma * V * S^-1 * U^T
    C = sig @ Vh.T @ np.linalg.inv(np.diag(S)) @ U.T
    
    if mandel_scaling:
        # reverse scaling from Mandel notation to get correct entries of the stiffness
        # tensor
        C[3:,:] = C[3:,:] / np.sqrt(2)
        C[:,3:] = C[:,3:] / np.sqrt(2)
    
    C = (C + C.T) / 2
    
    return C

def compute_thermal_conductivity_matrix(q_d, dt_d):
    order = ['x', 'y', 'z']

    # create matrix q
    Q = np.vstack([np.array([q[o] for o in order]) for q in q_d]).T
    
    # create matrix dt
    Dt = np.vstack([np.array([dt[o] for o in order]) for dt in dt_d]).T
    
    # compute svd
    #  dts = U * S * V^T
    U, S, Vh = np.linalg.svd(Dt)
    
    # compute stiffness matrix 
    #  C = sigma * V * S^-1 * U^T
    K = - Q @ Vh.T @ np.linalg.inv(np.diag(S)) @ U.T
    
    return K
    
    
    
def voigt_average(C):
    """Compute Voigt average approximation of the elastic constants.
    

    Parameters
    ----------
    C : numpy.array
        Stiffness tensor as a 6x6 matrix.

    Returns
    -------
    dict :
        Dictionary with keys ``'E', 'nu', 'K', 'G'`` representing the 
        elastic modulus, poisson ratio, bulk  modulus and shear modulus.

    """
    av = (C[0,0]+C[1,1]+C[2,2])/3
    bv = (C[0,1]+C[1,2]+C[2,0])/3
    cv = (C[3,3]+C[4,4]+C[5,5])/3
    
    ev = (av-bv+3*cv)*(av+2*bv)/(2*av+3*bv+cv)
    gv = (av-bv+3*cv)/5
    kv = (av+2*bv)/3
    pv = ev/2/gv-1
    
    res = {k: v for (k,v) in zip(('E', 'nu', 'K', 'G'), (ev, pv, kv, gv))}
    
    return res

def reuss_average(C):
    """Compute Reuss average approximation of the elastic constants.
    

    Parameters
    ----------
    C : numpy.array
        Stiffness tensor as a 6x6 matrix.

    Returns
    -------
    dict :
        Dictionary with keys ``'E', 'nu', 'K', 'G'`` representing the 
        elastic modulus, poisson ratio, bulk  modulus and shear modulus.

    """
    a = np.linalg.inv(C)
    
    xr = (a[0,0]+a[1,1]+a[2,2])/3
    yr = (a[0,1]+a[1,2]+a[2,0])/3
    zr = (a[3,3]+a[4,4]+a[5,5])/3
    
    er = 5/(3*xr+2*yr+zr)
    gr = 5/(4*xr-4*yr+3*zr)
    kr = 1/(xr+2*yr)/3
    pr = er/2/gr-1
    
    res = {k: v for (k,v) in zip(('E', 'nu', 'K', 'G'), (er, pr, kr, gr))}
    
    return res

def hill_average(C):
    """Compute hill average approximation for the elastic constants.
    

    Parameters
    ----------
    C : numpy.array
        Stiffness tensor as a 6x6 matrix.

    Returns
    -------
    dict :
        Dictionary with keys ``'E', 'nu', 'K', 'G'`` representing the 
        elastic modulus, poisson ratio, bulk  modulus and shear modulus.

    """
    voigt = voigt_average(C)
    reuss = reuss_average(C)
    
    hill = {k: (voigt[k] + reuss[k])/2.0 for k in ('E', 'nu', 'K', 'G')}
    
    return hill

if __name__ == "__main__":
    """
    For each load step (1 - 6) fx contains the following:
        fx fy fz fxy fxz fyz
    where f<comp> is the cumulative component stress of the RVE as computed by the
    APDL 'ETABLE, S, <comp>' and 'SSUM'
    """
    # fx # fxx            fyy            fzz            fxy            fxz            fyz     
    # -> 11 22 33 12 13 23
    #     0  1  2  3  4  5
    
    def create_dict(nparr):
        res = {}
        for i in range(6):
            res[i] = {k: v for k,v in zip(['xx', 'yy', 'zz', 'xy', 'xz', 'yz'], nparr[i,:])}
        return res
    
    # create stress tensor (in matrix form)
    sig_ = np.array([[0.00717,  0.00624, 23.27492, -0.04908, -0.17675,  0.48564],
                     [0.00668, 23.22473,  0.00764,  0.32940, -0.06258,  0.44176],
                     [23.13187,  0.00645,  0.00733,  0.31892, -0.02467, -0.01265],
                     [0.07375,  0.13280, -0.02431,  6.15113,  0.26355, -0.12914],
                     [-0.16429, -0.05409, -0.11170,  0.23956,  6.20875,  0.20275],
                     [0.09944,  0.46823,  0.50660, -0.14505,  0.23742,  5.97150]])
           
    """
    For each load step (1 - 6) ex contains the following:
        exx eyy ezz exy exz eyz
    where e<comp> is the cumulative component elastic strain of the RVE as computed by the
    APDL 'ETABLE, EPEL, <comp>' and 'SSUM'
    """
    # ex # exx            eyy            ezz            exy            exz            eyz     
    # -> 1,1 2,2 3,3 1,2 1,3 2,3
    #        
    eps_ = np.array([[-0.02700, -0.02661,  0.15000,  0.00226, -0.00545, -0.00197],
                     [-0.02772,  0.15000, -0.02655, -0.00024,  0.00064, -0.00380],
                     [0.15000, -0.02761, -0.02683, -0.00027, -0.00463, -0.00014],
                     [-0.00060,  0.00020,  0.00000,  0.10000,  0.00036, -0.00311],
                     [-0.00410,  0.00000, -0.00075,  0.00192,  0.10000,  0.00141],
                     [-0.00000, -0.00138, -0.00152, -0.00390,  0.00218,  0.10000]])

    # delphi way
    eps_d = create_dict(eps_)
    sig_d = create_dict(sig_)
    C, svd_ratio = compute_stiffness_matrix_svd(eps_d, sig_d)
    print("svd_ratio = ", svd_ratio)
    
    print("voigt av: ", voigt_average(C))
    print("reuss av: ", reuss_average(C))
    print("hill av: ", hill_average(C))
    
    C_simple = compute_stiffness_matrix_simple(eps_d, sig_d, mandel_scaling=False)
    
    print("voigt av: ", voigt_average(C_simple))
    print("reuss av: ", reuss_average(C_simple))
    print("hill av: ", hill_average(C_simple))
    
    #np.savetxt("C.txt", C, fmt='%8.3f')
    #np.savetxt("C_simple.txt", C_simple, fmt='%8.3f')



