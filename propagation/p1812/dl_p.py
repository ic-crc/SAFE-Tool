

from propagation.p1812.earth_rad_eff import earth_rad_eff
from propagation.p1812.dl_delta_bull import dl_delta_bull
from propagation.p1812.inv_cum_norm import inv_cum_norm

def dl_p(d = None,g = None,hts = None,hrs = None,hstd = None,hsrd = None,f = None,omega = None,p = None,b0 = None,DN = None,flag4 = None): 
    #import pdb;pdb.set_trace()
    #dl_p Diffraction loss model not exceeded for p# of time according to P.1812-4
#   function [Ldp, Ld50, Lbulla50, Lbulls50, Ldsph50] = dl_p( d, h, hts, hrs, hstd, hsrd, ap, f, omega, p, b0, DN, flag4 )
    
    #   This function computes the diffraction loss not exceeded for p# of time
#   as defined in ITU-R P.1812-5 (Section 4.3-5) and Attachment 4 to Annex 1
    
    #     Input parameters:
#     d       -   vector of distances di of the i-th profile point (km)
#     g       -   vector gi of heights of the i-th profile point (meters
#                 above mean sea level) + Representative clutter height.
#                 Both vectors g and d contain n+1 profile points
#     hts     -   transmitter antenna height in meters above sea level (i=0)
#     hrs     -   receiver antenna height in meters above sea level (i=n)
#     hstd    -   Effective height of interfering antenna (m amsl) c.f. 5.6.2
#     hsrd    -   Effective height of interfered-with antenna (m amsl) c.f. 5.6.2
#     f       -   frequency expressed in GHz
#     omega   -   the fraction of the path over sea
#     p       -   percentage of time
#     b0      -   the time percentage that the refractivity gradient (DELTA-N) exceeds 100 N-units/km in the first 100m of the lower atmosphere
#     DN      -   the average radio-refractive index lapse-rate through the
#                 lowest 1 km of the atmosphere. Note that DN is positive
#                 quantity in this procedure
#     flag4   -   Set to 1 if the alternative method is used to calculate Lbulls
#                 without using terrain profile analysis (Attachment 4 to Annex 1)
    
    
    #     Output parameters:
#     Ldp    -   diffraction loss for the general path not exceeded for p # of the time
#                according to Section 4.3.4 of ITU-R P.1812-4.
#                Ldp(1) is for the horizontal polarization
#                Ldp(2) is for the vertical polarization
#     Ldb    -   diffraction loss for p = beta_0#
#     Ld50   -   diffraction loss for p = 50#
#     Lbulla50 -   Bullington diffraction (4.3.1) for actual terrain profile g and antenna heights
#     Lbulls50 -   Bullington diffraction (4.3.1) with all profile heights g set to zero and modified antenna heights
#     Ldshp50  -   Spherical diffraction (4.3.2) for the actual path d and modified antenna heights
    
    
    #     Example:
#     [Ldp, Ldb, Ld50, Lbulla50, Lbulls50, Ldsph50] = dl_p( d, g, hts, hrs, hstd, hsrd, ap, f, omega, p, b0, DN )
    
    
    # Use the method in 4.3.4 to calculate diffraction loss Ld for median effective
# Earth radius ap = ae as given by equation (7a). Set median diffraction
# loss to Ldp50
    
    ae,ab = earth_rad_eff(DN)
    ap = ae
    Ld50,Lbulla50,Lbulls50,Ldsph50 = dl_delta_bull(d,g,hts,hrs,hstd,hsrd,ap,f,omega,flag4)
    if p == 50:
        Ldp = Ld50
        ap = ab
        Ldb = dl_delta_bull(d,g,hts,hrs,hstd,hsrd,ap,f,omega,flag4)
        return Ldp,Ldb,Ld50,Lbulla50,Lbulls50,Ldsph50
    
    if p < 50:
        # Use the method in 4.3.4 to calculate diffraction loss Ld for effective
# Earth radius ap = abeta, as given in equation (7b). Set diffraction loss
# not exceeded for beta0# time Ldb = Ld
        ap = ab
        Ldb = dl_delta_bull(d,g,hts,hrs,hstd,hsrd,ap,f,omega,flag4)[0]
        # Compute the interpolation factor Fi
        if p > b0:
            Fi = inv_cum_norm(p / 100) / inv_cum_norm(b0 / 100)
        else:
            Fi = 1
        # The diffraction loss Ldp not exceeded for p# of time is now given by
        Ldp = Ld50 + Fi * (Ldb - Ld50)
    
    return Ldp,Ldb,Ld50,Lbulla50,Lbulls50,Ldsph50
