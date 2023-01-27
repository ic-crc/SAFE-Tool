

import numpy as np
    
def pl_los(d = None,hts = None,hrs = None,f = None,p = None,b0 = None,dlt = None,dlr = None): 
    #import pdb;pdb.set_trace()
    #pl_los Line-of-sight transmission loss according to ITU-R P.1812-6
#     This function computes line-of-sight transmission loss (including short-term effects)
#     as defined in ITU-R P.1812-6.
    
    #     Input parameters:
#     d       -   Great-circle path distance (km)
#     hts     -   Tx antenna height above sea level (masl)
#     hrs     -   Rx antenna height above sea level (masl)
#     f       -   Frequency (GHz)
#     p       -   Required time percentage(s) for which the calculated basic
#                 transmission loss is not exceeded (#)
#     b0      -   Point incidence of anomalous propagation for the path
#                 central location (#)
#     dlt     -   For a transhorizon path, distance from the transmit antenna to
#                 its horizon (km). For a LoS path, each is set to the distance
#                 from the terminal to the profile point identified as the Bullington
#                 point in the diffraction method for 50# time
#     dlr     -   For a transhorizon path, distance from the receive antenna to
#                 its horizon (km). The same note as for dlt applies here.
    
    #     Output parameters:
#     Lbfs   -   Basic transmission loss due to free-space propagation
#     Lb0p    -   Basic transmission loss not exceeded for time percentage, p#, due to LoS propagation
#     Lb0b    -   Basic transmission loss not exceedd for time percentage, b0#, due to LoS propagation
    
    #     Example:
#     [Lbfsg, Lb0p, Lb0b] = pl_los(d, hts, hrs, f, p, b0, dlt, dlr)
    
    # Basic transmission loss due to free-space propagation
    
    #Lbfs = 92.45 + 20.0*log10(f) + 20.0*log10(d);  # (8)
    
    dfs = np.sqrt(d ** 2 + ((hts - hrs) / 1000.0) ** 2)
    
    Lbfs = 92.4 + 20.0 * np.log10(f) + 20.0 * np.log10(dfs)
    
    # Corrections for multipath and focusing effects at p and b0
    Esp = 2.6 * (1 - np.exp(- 0.1 * (dlt + dlr))) * np.log10(p / 50)
    
    Esb = 2.6 * (1 - np.exp(- 0.1 * (dlt + dlr))) * np.log10(b0 / 50)
    
    # Basic transmission loss not exceeded for time percentage p# due to
# LoS propagation
    Lb0p = Lbfs + Esp
    
    # Basic transmission loss not exceeded for time percentage b0# due to
# LoS propagation
    Lb0b = Lbfs + Esb
    
    return Lbfs,Lb0p,Lb0b
    