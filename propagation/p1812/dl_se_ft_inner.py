

import numpy as np
    
def dl_se_ft_inner(epsr = None,sigma = None,d = None,hte = None,hre = None,adft = None,f = None): 
    #import pdb;pdb.set_trace()
    ##dl_se_ft_inner The inner routine of the first-term spherical diffraction loss
#   This function computes the first-term part of Spherical-Earth diffraction
#   loss exceeded for p# time for antenna heights
#   as defined in Sec. 4.3.3 of the ITU-R P.1812-4, equations (29-36)
    
    #     Input parameters:
#     epsr    -   Relative permittivity
#     sigma   -   Conductivity (S/m)
#     d       -   Great-circle path distance (km)
#     hte     -   Effective height of interfering antenna (m)
#     hre     -   Effective height of interfered-with antenna (m)
#     adft    -   effective Earth radius (km)
#     f       -   frequency (GHz)
    
    #     Output parameters:
#     Ldft   -   The first-term spherical-Earth diffraction loss not exceeded for p# time
#                implementing equations (30-37), Ldft(1) is for horizontal
#                and Ldft(2) for the vertical polarization
    
    #     Example:
#     Ldft = dl_se_ft_inner(epsr, sigma, d, hte, hre, adft, f)
    
    # Normalized factor for surface admittance for horizontal (1) and vertical
# (2) polarizations

    K = np.array([0, 0])
    
    K = K.astype(float)
    
    K[0] = 0.036 * (adft * f) ** (- 1 / 3) * ((epsr - 1) ** 2 + (18 * sigma / f) ** 2) ** (- 1 / 4)
    
    K[1] = K[0] * (epsr ** 2 + (18 * sigma / f) ** 2) ** (1 / 2)
    
    # Earth ground/polarization parameter
    
    beta_dft = (1 + 1.6 * K ** 2 + 0.67 * K ** 4) / (1 + 4.5 * K ** 2 + 1.53 * K ** 4)
    
    # Normalized distance
    
    X = 21.88 * beta_dft * (f / adft ** 2) ** (1 / 3) * d
    
    # Normalized transmitter and receiver heights
    
    Yt = 0.9575 * beta_dft * (f ** 2 / adft) ** (1 / 3) * hte
    
    Yr = 0.9575 * beta_dft * (f ** 2 / adft) ** (1 / 3) * hre
    
    Fx = np.array([0,0])
    Fx = Fx.astype(float)
    GYt = np.array([0,0])
    GYt = GYt.astype(float)
    GYr = np.array([0,0])
    GYr = GYr.astype(float)
    # Calculate the distance term given by:
    
    for ii in range(2):
        if X[ii] >= 1.6:
            Fx[ii] = 11 + 10 * np.log10(X[ii]) - 17.6 * X[ii]
        else:
            Fx[ii] = - 20 * np.log10(X[ii]) - 5.6488 * (X[ii]) ** 1.425
    
    Bt = beta_dft * Yt
    
    Br = beta_dft * Yr
    
    for ii in range(2):
        if Bt[ii] > 2:
            GYt[ii] = 17.6 * (Bt[ii] - 1.1) ** 0.5 - 5 * np.log10(Bt[ii] - 1.1) - 8
        else:
            GYt[ii] = 20 * np.log10(Bt[ii] + 0.1 * Bt[ii] ** 3)
        if Br[ii] > 2:
            GYr[ii] = 17.6 * (Br[ii] - 1.1) ** 0.5 - 5 * np.log10(Br[ii] - 1.1) - 8
        else:
            GYr[ii] = 20 * np.log10(Br[ii] + 0.1 * Br[ii] ** 3)
        if GYr[ii] < 2 + 20 * np.log10(K[ii]):
            GYr[ii] = 2 + 20 * np.log10(K[ii])
        if GYt[ii] < 2 + 20 * np.log10(K[ii]):
            GYt[ii] = 2 + 20 * np.log10(K[ii])
    
    Ldft = - Fx - GYt - GYr
    

    
    return Ldft
   