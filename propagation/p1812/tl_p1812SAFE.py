

import numpy as np

from propagation.p1812.check_limit import check_limit
from propagation.p1812.check_value import check_value
from propagation.p1812.great_circle_path import great_circle_path
from propagation.p1812.longest_cont_dist import longest_cont_dist
from propagation.p1812.beta0 import beta0
from propagation.p1812.earth_rad_eff import earth_rad_eff
from propagation.p1812.path_fraction import path_fraction
from propagation.p1812.smooth_earth_heights import smooth_earth_heights
from propagation.p1812.pl_los import pl_los
from propagation.p1812.dl_p import dl_p
from propagation.p1812.inv_cum_norm import inv_cum_norm
from propagation.p1812.tl_anomalous import tl_anomalous
from propagation.p1812.tl_tropo import tl_tropo

    
def tl_p1812SAFE(f = None,p = None,d = None,h = None,R = None,Ct = None,zone = None,htg = None,hrg = None,pol = None, phi_t = None, phi_r = None, lam_t = None, lam_r = None, pL = None, sigmaL = None, DN = None, N0 = None): 
    #import pdb;pdb.set_trace()
    #tl_p1812 basic transmission loss according to P.1812-6
#   [Lb Ep] = tl_p1812(f, p, d, h, R, Ct, zone, htg, hrg, pol, varargin)
    
    #   This is the MAIN function that computes the basic transmission loss not exceeded for p% time
#   and pL% locations, including additional losses due to terminal surroundings
#   and the field strength exceeded for p% time and pL% locations
#   as defined in ITU-R P.1812-6.
#   This function:
#   does not include the building entry loss (only outdoor scenarios implemented)
    
    #   Other functions called from this function are in ./private/ subfolder.
    
    #     Input parameters:
#     f       -   Frequency (GHz)
#     p       -   Required time percentage for which the calculated basic
#                 transmission loss is not exceeded
#     d       -   vector of distances di of the i-th profile point (km)
#     h       -   vector of heights hi of the i-th profile point (meters
#                 above mean sea level.
#     R       -   vector of representative clutter height Ri of the i-th profile point (m)
#     Ct      -   vector of representative clutter type Cti of the i-th profile point
#                 Water/sea (1), Open/rural (2), Suburban (3),
#                 Urban/trees/forest (4), Dense urban (5)
#                 if empty or all zeros, the default clutter used is Open/rural
#     zone    -   vector of radio-climatic zone types: Inland (4), Coastal land (3), or Sea (1)
#     htg     -   Tx Antenna center heigth above ground level (m)
#     hrg     -   Rx Antenna center heigth above ground level (m)
#     pol     -   polarization of the signal (1) horizontal, (2) vertical
    
    #    Input parameters related to path centre:
#    EITHER the following are required:
    
    #     phi_t    - latitude of Tx station (degrees)
#     phi_r    - latitude of Rx station (degrees)
#     lam_t    - longitude of Tx station (degrees)
#     lam_r    - longitude of Rx station (degrees)
    
    #    OR the following are required:
    
    #     phi_path - latitude of the path centre (degrees)
    
    #   Examples of both cases are provided below.
    
    #   Output parameters:
#     Lb   - basic transmission loss according to P.1812-6
#     Ep   - the field strength relative to Ptx
    
    
    # Examples:
    
    # 1) Call with required input parameters, and latitude/longitude of Tx/Rx:
# [Lb,Ep] = tl_p1812(f,p,d,h,R,Ct,zone,htg,hrg,pol,...
#     'phi_t',phi_t,'phi_r',phi_r,'lam_t',lam_t,'lam_r',lam_r)
    
    # 2) Call with required input parameters, and latitude of path centre:
# [Lb,Ep] = tl_p1812(f,p,d,h,R,Ct,zone,htg,hrg,pol,'phi_path',phi_path);
    
    # 3) Call with Name-Value Pair Arguments. Name is the argument name and Value is the
# corresponding value. Name must appear inside quotes.
# [Lb,Ep] = tl_p1812(___,Name,Value)
# Example: tl_p1812(f,p,d,h,R,Ct,zone,htg,hrg,pol,'phi_path',phi_path,'DN',DN,'N0',N0)
# Below are the valid Name-Value Pair Arguments:
#     pL      -   Required time percentage for which the calculated basic
#                 transmission loss is not exceeded (1# - 99#)
#     sigmaL  -   location variability standard deviations computed using
#                 stdDev.m according to §4.8 and §4.10
#                 the value of 5.5 dB used for planning Broadcasting DTT
#     Ptx     -   Transmitter power (kW), default value 1 kW
#     DN      -   The average radio-refractive index lapse-rate through the
#                 lowest 1 km of the atmosphere (it is a positive quantity in this
#                 procedure) (N-units/km)
#     N0      -   The sea-level surface refractivity, is used only by the
#                 troposcatter model as a measure of location variability of the
#                 troposcatter mechanism. The correct values of DN and N0 are given by
#                 the path-centre values as derived from the appropriate
#                 maps (N-units)
#     dct     -   Distance over land from the transmit and receive
#     dcr         antennas to the coast along the great-circle interference path (km).
#                 default values dct = 500 km, dcr = 500 km, or
#                 set to zero for a terminal on a ship or sea platform
#     flag4   -   Set to 1 if the alternative method is used to calculate Lbulls
#                 without using terrain profile analysis (Attachment 4 to Annex 1)
#     debug   -   Set to 1 if the log files are to be written,
#                 otherwise set to default 0
#     fid_log  -   if debug == 1, a file identifier of the log file can be
#                 provided, if not, the default file with a file
#                 containing a timestamp will be created
  
    # This function calls other functions that are placed in the ./private folder
    
    # Set other optional inputs
    dcr = 500
    dct = 500
    flag4 = 0
    
    #verify input argument values and limits
    check_limit(f, 0.03, 6.0, 'f [GHz]');
    check_limit(p, 1, 50, 'p [%]');
    check_limit(htg, 1, 3000, 'htg [m]');
    check_limit(hrg, 1, 3000, 'hrg [m]');
    check_limit(pL, 1, 99, 'pL[%]');
    check_value(np.array([pol]), np.array([1, 2]), 'Polarization (pol)');
    check_value(Ct, [1, 2, 3, 4, 5], 'Clutter coverage (Ct)');
    check_value(zone, [1, 3, 4], 'Radio-climatic zone (zone)');
    
    
    if zone[0] == 1: # Tx at sea 
        dct = 0
    
    if zone[-1] == 1: # Rx at sea
        dcr = 0
    
    # Compute the path profile parameters
    
    # Path center latitude
    # Compute phi_path
    Re = 6371
    dpnt = 0.5 * (d[-1] - d[0])
    phi_path = great_circle_path(lam_r,lam_t,phi_r,phi_t,Re,dpnt)[1]
    
    # Compute  dtm     -   the longest continuous land (inland + coastal =34) section of the great-circle path (km)
    zone_r = 34
    dtm = longest_cont_dist(d,zone,zone_r)
    
    # Compute  dlm     -   the longest continuous inland section (4) of the great-circle path (km)
    zone_r = 4
    dlm = longest_cont_dist(d,zone,zone_r)
    
    # Compute b0
    b0 = beta0(phi_path,dtm,dlm)
    ae,ab = earth_rad_eff(DN)
    
    # Compute the path fraction over sea Eq (1)
    
    omega = path_fraction(d,zone,1)
    
    # Derive parameters for the path profile analysis
    
    hst_n,hsr_n,hst,hsr,hstd,hsrd,hte,hre,hm,dlt,dlr,theta_t,theta_r,theta,pathtype = smooth_earth_heights(d,h,R,htg,hrg,ae,f)
    dtot = d[-1] - d[0]
    
    #Tx and Rx antenna heights above mean sea level amsl (m)
    hts = h[0] + htg
    hrs = h[-1] + hrg
    
    # Modify the path by adding representative clutter, according to Section 3.2
    # excluding the first and the last point
    g = h + R
    g[0] = h[0]
    g[-1] = h[-1]
    
    #Compute htc and hrc as defined in Table 5 (P.1812-6)
    # htc = max(hts,g(1));
    # hrc = max(hrs,g(end));
    htc = hts
    hrc = hrs
    
    # Calculate an interpolation factor Fj to take account of the path angular
    # distance Eq (57)
    THETA = 0.3
    KSI = 0.8
    Fj = 1.0 - 0.5 * (1.0 + np.tanh(3.0 * KSI * (theta - THETA) / THETA))
    
    # Calculate an interpolation factor, Fk, to take account of the great
    # circle path distance:
    dsw = 20
    kappa = 0.5
    Fk = 1.0 - 0.5 * (1.0 + np.tanh(3.0 * kappa * (dtot - dsw) / dsw)) # eq (58)
    
    #[Lbfs, Lb0p, Lb0b] = pl_los(dtot, f, p, b0, dlt, dlr);
    Lbfs,Lb0p,Lb0b = pl_los(dtot,hts,hrs,f,p,b0,dlt,dlr)
    Ldp,Ldb,Ld50,Lbulla50,Lbulls50,Ldsph50 = dl_p(d,g,htc,hrc,hstd,hsrd,f,omega,p,b0,DN,flag4)
    
    # The median basic transmission loss associated with diffraction Eq (42)
    Lbd50 = Lbfs + Ld50
    
    # The basic tranmission loss associated with diffraction not exceeded for
    # p% time Eq (43)
    Lbd = Lb0p + Ldp
    
    # A notional minimum basic transmission loss associated with LoS
    # propagation and over-sea sub-path diffraction
    Lminb0p = Lb0p + (1 - omega) * Ldp
    
    # eq (40a)
    Fi = 1
    if p >= b0:
        Fi = inv_cum_norm(p / 100) / inv_cum_norm(b0 / 100)
        Lminb0p = Lbd50 + (Lb0b + (1 - omega) * Ldp - Lbd50) * Fi # eq (59)
    
    # Calculate a notional minimum basic transmission loss associated with LoS
    # and transhorizon signal enhancements
    eta = 2.5
    Lba = tl_anomalous(dtot,dlt,dlr,dct,dcr,dlm,hts,hrs,hte,hre,hm,theta_t,theta_r,f,p,omega,ae,b0)
    Lminbap = eta * np.log(np.exp(Lba / eta) + np.exp(Lb0p / eta))  # eq (60)
    
    # Calculate a notional basic transmission loss associated with diffraction
    # and LoS or ducting/layer reflection enhancements
    Lbda = Lbd
    if Lminbap <= Lbd[0] and Lminbap <= Lbd[1]:
        Lbda = Lminbap + (Lbd - Lminbap) * Fk # eq (61)
    
    # Calculate a modified basic transmission loss, which takes diffraction and
    # LoS or ducting/layer-reflection enhancements into account
    Lbam = Lbda + (Lminb0p - Lbda) * Fj # eq (62)
    
    # Calculate the basic transmission loss due to troposcatter not exceeded
    # for any time percantage p
    
    Lbs = tl_tropo(dtot,theta,f,p,N0)
    
    # Calculate the final transmission loss not exceeded for p% time
    # ignoring the effects of terminal clutter
    Lbc_pol = - 5 * np.log10(10.0 ** (- 0.2 * Lbs) + 10.0 ** (- 0.2 * Lbam)) # eq (63)
    
    # choose the right polarization
    Lbc = Lbc_pol[pol-1]
    
    # # The additional clutter losses from are removed in P.1812-6
# # additional losses due to terminal surroundings (Section 4.7)
    
    # # Parameter ws relates to the width of the street. It is set to 27 unless
# # there is specific local information available
    
    # ws = 27;
    
    # # Transmitter side
    
    # Aht = cl_loss(htg, R(1), Ct(1), f, ws);
    
    # # Receiver side
    
    # Ahr = cl_loss(hrg, R(end), Ct(end), f, ws);
    
    # # Basic transmission loss not exceeded for p% time and 50% locations,
# # including the effects of terminal clutter losses
    
    #Lbc = Lbu + Aht + Ahr;
    
    Lloc = 0.0 # outdoors only (67a)
    
    # Location variability of losses (Section 4.8)
    if zone[-1] != 1: # Rx at sea
        Lloc = - inv_cum_norm(pL / 100) * sigmaL
    
    # Basic transmission loss not exceeded for p% time and pL% locations
    # (Sections 4.8 and 4.9) not implemented
    
    Lb = max(Lb0p,Lbc + Lloc) # eq (69)
    
    return Lb
