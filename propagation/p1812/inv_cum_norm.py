

import numpy as np
    
def inv_cum_norm(x = None): 
    #inv_cum_norm approximation to the inverse cummulative normal distribution
#   I = inv_cum_norm( x )
#   This function implements an approximation to the inverse cummulative
#   normal distribution function for 0<x<1 as defined in Attachment 2 to
#   Annex 1 of the ITU-R P.1812-5
    
    if x < 1e-06:
        x = 1e-06
    
    if x > 0.999999:
        x = 0.999999
    
    if x <= 0.5:
        I = T(x) - C(x)
    else:
        I = - (T(1 - x) - C(1 - x))
    
    return I
    
def T(y = None): 
    outT = np.sqrt(- 2 * np.log(y))
    
    return outT
    
def C(z = None): 
    C0 = 2.515516698
    C1 = 0.802853
    C2 = 0.010328
    D1 = 1.432788
    D2 = 0.189269
    D3 = 0.001308
    outC = (((C2 * T(z) + C1) * T(z)) + C0) / (((D3 * T(z) + D2) * T(z) + D1) * T(z) + 1)
    
    return outC
  