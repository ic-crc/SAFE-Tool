
import numpy as np
    
def dl_bull(d = None,g = None,hts = None,hrs = None,ap = None,f = None): 
    #import pdb;pdb.set_trace()
    #dl_bull Bullington part of the diffraction loss according to P.1812-4
#   This function computes the Bullington part of the diffraction loss
#   as defined in ITU-R P.1812-4 in 4.3.1
    
    #     Input parameters:
#     d       -   vector of distances di of the i-th profile point (km)
#     g       -   vector of heights hi of the i-th profile point (meters
#                 above mean sea level) + representative clutter height
#                 Both vectors d and g contain n+1 profile points
#     hts     -   transmitter antenna height in meters above sea level (i=0)
#     hrs     -   receiver antenna height in meters above sea level (i=n)
#     ap      -   the effective earth radius in kilometers
#     f       -   frequency expressed in GHz
    
    #     Output parameters:
#     Lbull   -   Bullington diffraction loss for a given path
    
    #     Example:
#     Lbull = dl_bull(d, g, hts, hrs, ap, f)
    
    ## Body of function
    
    # Effective Earth curvature Ce (km^-1)
    
    Ce = 1 / ap
    # Wavelength in meters
# speed of light as per ITU.R P.2001
    lambda_ = 0.2998 / f
    # Complete path length
    
    dtot = d[-1] - d[0]
    # Find the intermediate profile point with the highest slope of the line
# from the transmitter to the point
    
    di = d[1:len(d)-1]
    gi = g[1:len(d)-1]
    Stim = max((gi + 500 * Ce * di * (dtot - di) - hts) / di)
    
    # Calculate the slope of the line from transmitter to receiver assuming a
# LoS path
    
    Str = (hrs - hts) / dtot
    
    if Stim < Str:
        # Find the intermediate profile point with the highest diffraction
# parameter nu:
        numax = max((gi + 500 * Ce * di * (dtot - di) - (hts * (dtot - di) + hrs * di) / dtot) * np.sqrt(0.002 * dtot / (lambda_ * di * (dtot - di))))
        Luc = 0
        if numax > - 0.78:
            Luc = 6.9 + 20 * np.log10(np.sqrt((numax - 0.1) ** 2 + 1) + numax - 0.1)
    else:
        # Path is transhorizon
        # Find the intermediate profile point with the highest slope of the
# line from the receiver to the point
        Srim = max((gi + 500 * Ce * di * (dtot - di) - hrs) / (dtot - di))
        # Calculate the distance of the Bullington point from the transmitter:
        dbp = (hrs - hts + Srim * dtot) / (Stim + Srim)
        # Calculate the diffraction parameter, nub, for the Bullington point
        nub = (hts + Stim * dbp - (hts * (dtot - dbp) + hrs * dbp) / dtot) * np.sqrt(0.002 * dtot / (lambda_ * dbp * (dtot - dbp)))
        # The knife-edge loss for the Bullington point is given by
        Luc = 0
        if nub > - 0.78:
            Luc = 6.9 + 20 * np.log10(np.sqrt((nub - 0.1) ** 2 + 1) + nub - 0.1)
    
    # For Luc calculated using either (16) or (20), Bullington diffraction loss
# for the path is given by
    
    Lbull = Luc + (1 - np.exp(- Luc / 6.0)) * (10 + 0.02 * dtot)
    
    return Lbull
   