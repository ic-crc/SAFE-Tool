


import numpy as np
    
def find_intervals(series = None): 
    #find_intervals Find all intervals with consecutive 1's
#     [k1, k2] = find_intervals(series)
#     This function finds all 1's intervals, namely, the indices when the
#     intervals start and where they end
    
    #     For example, for the input indices
#           0 0 1 1 1 1 0 0 0 1 1 0 0
#     this function will give back
#       k1 = 3, 10
#       k2 = 6, 11
    
    #     Input arguments:
#     indices -   vector containing zeros and ones
    
    #     Output arguments:
#     k1      -   vector of start-indices of the found intervals
#     k2      -   vector of end-indices of the found intervals
    
    #     Example:
#     [k1, k2] = find_intervals(indices)
    
    k1 = []
    k2 = []
    if np.amax(series) == 1:
        k1 = np.where(np.diff(np.append(0,series)) == 1)[0]
        k2 = np.where(np.diff(np.append(series,0)) == - 1)[0]
    
    return k1,k2