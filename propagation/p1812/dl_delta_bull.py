

from propagation.p1812.dl_bull import dl_bull

from propagation.p1812.dl_se import dl_se

import numpy as np
    
def dl_delta_bull(d = None,g = None,hts = None,hrs = None,hstd = None,hsrd = None,ap = None,f = None,omega = None,flag4 = None): 
    #import pdb;pdb.set_trace()
    #dl_delta_bull Complete 'delta-Bullington' diffraction loss model P.1812-4
#   function Ld = dl_delta_bull( d, h, hts, hrs, hstd, hsrd, ap, f, omega, flag4 )
    
    #   This function computes the complete 'delta-Bullington' diffraction loss
#   as defined in ITU-R P.1812-4 (Section 4.3.4)
    
    #     Input parameters:
#     d       -   vector of distances di of the i-th profile point (km)
#     g       -   vector of heights hi of the i-th profile point (meters
#                 above mean sea level) + Representative clutter height.
#                 Both vectors d, g contain n+1 profile points
#     hts     -   transmitter antenna height in meters above sea level (i=0)
#     hrs     -   receiver antenna height in meters above sea level (i=n)
#     hstd    -   Effective height of interfering antenna (m amsl) c.f. 5.1.6.3
#     hsrd    -   Effective height of interfered-with antenna (m amsl) c.f. 5.1.6.3
#     ap      -   the effective Earth radius in kilometers
#     f       -   frequency expressed in GHz
#     omega   -   the fraction of the path over sea
    
    #     Output parameters:
#     Ld     -   diffraction loss for the general path according to
#                Section 4.3.3 of ITU-R P.1812-4.
#                Ld(1) is for the horizontal polarization
#                Ld(2) is for the vertical polarization
#     Lbulla -   Bullington diffraction (4.3.1) for actual terrain profile g and antenna heights
#     Lbulls -   Bullington diffraction (4.3.1) with all profile heights g set to zero and modified antenna heights
#     Ldshp  -   Spherical diffraction (4.3.2) for the actual path d and modified antenna heights
#     flag4  -   Set to 1 if the alternative method is used to calculate Lbulls
#                without using terrain profile analysis (Attachment 4 to Annex 1)
    
    #     Example:
#     [Ld, Lbulla, Lbulls, Ldsph] = dl_delta_bull( d, g, hts, hrs, hstd, hsrd, ap, f, omega, flag4)
    
    
    # Use the method in 4.3.1 for the actual terrain profile and antenna
# heights. Set the resulting Bullington diffraction loss for the actual
# path to Lbulla
    
    Lbulla = dl_bull(d,g,hts,hrs,ap,f)
    # Use the method in 4.3.1 for a second time, with all profile heights gi
# set to zero and modified antenna heights given by
    
    hts1 = hts - hstd
    
    hrs1 = hrs - hsrd
    
    h1 = np.zeros(len(g))
    dtot = d[-1] - d[0]
    # where hstd and hsrd are given in 5.6.2 of Attachment 1.
    
    # Set the resulting Bullington diffraction loss for this smooth path to Lbulls
    if (flag4 == 1):
        # compute the spherical earth diffraction Lbuls using an
# alternative method w/o terrain profile analysis
# as defined in Attachment 4 to Annex 1 of ITU-R P.1812-5
        Lbulls = dl_bull_att4(dtot,hts1,hrs1,ap,f)
    else:
        # Compute Lbuls using §4.3.1
        Lbulls = dl_bull(d,h1,hts1,hrs1,ap,f)
    
    # Use the method in 4.3.2 to calculate the spherical-Earth diffraction loss
# for the actual path length (dtot) with
    
    hte = hts1
    
    hre = hrs1
    
    Ldsph = dl_se(dtot,hte,hre,ap,f,omega)
    # Diffraction loss for the general paht is now given by
    
    Ld = np.array([0, 0])
    Ld = Ld.astype(float)
    
    Ld[0] = Lbulla + max(Ldsph[0] - Lbulls,0)
    
    Ld[1] = Lbulla + max(Ldsph[1] - Lbulls,0)
    
    return Ld,Lbulla,Lbulls,Ldsph
