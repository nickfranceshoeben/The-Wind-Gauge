import numpy as np



def R_w_s(angle):
    #Create rotation matrix from world to ship coordinates. Angle given in degrees.
    
    mat = np.array([[np.cos(angle),np.sin(angle)],
                    [-np.sin(angle),np.cos(angle)]])
    
    return mat

def R_s_w(angle):
    #Create rotation matrix from ship to world coordinates. Angle given in degrees.
    
    mat = np.array([[np.cos(angle),-np.sin(angle)],
                    [np.sin(angle),np.cos(angle)]])
    
    return mat
    
    