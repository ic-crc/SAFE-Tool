
import numpy as np
    
def smooth_earth_heights(d = None,h = None,R = None,htg = None,hrg = None,ae = None,f = None): 
    #import pdb;pdb.set_trace()
    #smooth_earth_heights smooth-Earth effective antenna heights according to ITU-R P.1812-4
# [hst_n, hsr_n, hst, hsr, hstd, hsrd, hte, hre, hm, dlt, dlr, theta_t, theta_r, theta_tot, pathtype] = smooth_earth_heights(d, h, R, htg, hrg, ae, f)
# This function derives smooth-Earth effective antenna heights according to
# Sections 4 and 5 of the Attachment 1 to Annex 1 of ITU-R P.1812-4
    
    # Input parameters:
# d         -   vector of terrain profile distances from Tx [0,dtot] (km)
# h         -   vector of terrain profile heights amsl (m)
# R         -   vector of representative clutter heights (m)
# htg, hrg  -   Tx and Rx antenna heights above ground level (m)
# ae        -   median effective Earth's radius (c.f. Eq (7a))
# f         -   frequency (GHz)
    
    # Output parameters:
    
    # hst_n, hsr_n -   Not corrected Tx and Rx antenna heigts of the smooth-Earth surface amsl (m)
# hst, hsr     -   Tx and Rx antenna heigts of the smooth-Earth surface amsl (m)
# hstd, hsrd   -   Tx and Rx effective antenna heigts for the diffraction model (m)
# hte, hre     -   Tx and Rx terminal effective heights for the ducting/layer reflection model (m)
# hm           -   The terrain roughness parameter (m)
# dlt          -   interfering antenna horizon distance (km)
# dlr          -   Interfered-with antenna horizon distance (km)
# theta_t      -   Interfering antenna horizon elevation angle (mrad)
# theta_r      -   Interfered-with antenna horizon elevation angle (mrad)
# theta_tot    -   Angular distance (mrad)
# pathtype     -   1 = 'los', 2 = 'transhorizon'
    
    n = len(d)
    dtot = d[-1]
    #Tx and Rx antenna heights above mean sea level amsl (m)
    hts = h[0] + htg
    hrs = h[-1] + hrg
    g = h + R
    g[0] = h[0]
    g[-1] = h[-1]
    #htc = max(hts, g(1));
#hrc = max(hrs, g(end));
    htc = hts
    hrc = hrs
    # Section 5.6.1 Deriving the smooth-Earth surface
    
    # v1 = 0;
# for ii = 2:n
#     v1 = v1 + (d(ii)-d(ii-1))*(h(ii)+h(ii-1));  # Eq (85)
# end
# v2 = 0;
# for ii = 2:n
#     v2 = v2 + (d(ii)-d(ii-1))*( h(ii)*( 2*d(ii) + d(ii-1) ) + h(ii-1) * ( d(ii) + 2*d(ii-1) ) );  # Eq (86)
# end
    
    # the above equations optimized for speed, as suggested by Roger LeClair (leclairtelecom)
    
    #v1 = sum(np.multiply(np.diff(d),(h[1:n] + h[0:n-1])))
    v1 = sum(np.diff(d) * (h[1:n] + h[0:n-1]))
   #v2 = sum(np.multiply(np.diff(d),(np.multiply(h[1:n],(2*d[1:n] + d[0:n-1] + np.multiply(h[0:n-1],(d[1:n] + 2*d[0:n-1])))))))
    v2 = sum(np.diff(d)*(h[1:n]*(2 * d[1:n] + d[0:n-1]) + h[0:n-1]*(d[1:n] + 2 * d[0:n-1])))
    
    hst = (2 * v1 * dtot - v2) / dtot ** 2
    
    hsr = (v2 - v1 * dtot) / dtot ** 2
    
    hst_n = hst
    hsr_n = hsr
    # Section 5.6.2 Smooth-surface heights for the diffraction model
    
    HH = h - (htc * (dtot - d) + hrc * d) / dtot
    
    hobs = max(HH[1:n-1])
    
    alpha_obt = max(HH[1:n-1] / d[1:n-1])
    
    alpha_obr = max(HH[1:n-1] / (dtot - d[1:n-1]))
    
    # Calculate provisional values for the Tx and Rx smooth surface heights
    
    gt = alpha_obt / (alpha_obt + alpha_obr)
    
    gr = alpha_obr / (alpha_obt + alpha_obr)
    
    if hobs <= 0:
        hstp = hst
        hsrp = hsr
    else:
        hstp = hst - hobs * gt
        hsrp = hsr - hobs * gr
    
    # calculate the final values as required by the diffraction model
    
    if hstp >= h[0]:
        hstd = h[0]
    else:
        hstd = hstp
    
    if hsrp > h[-1]:
        hsrd = h[-1]
    else:
        hsrd = hsrp
    
    # Interfering antenna horizon elevation angle and distance
    
    ii = np.arange(1,n-1)
    theta = 1000 * np.arctan((h[ii] - hts) / (1000 * d[ii]) - d[ii] / (2 * ae))
    
    theta_td = 1000 * np.arctan((hrs - hts) / (1000 * dtot) - dtot / (2 * ae))
    
    theta_rd = 1000 * np.arctan((hts - hrs) / (1000 * dtot) - dtot / (2 * ae))
    
    theta_max = max(theta)
    
    if theta_max > theta_td:
        pathtype = 2
    else:
        pathtype = 1
    
    theta_t = max(theta_max,theta_td)
    
    if (pathtype == 2):
        kindex = np.where(theta == theta_max)
        lt = kindex[0] + 1
        dlt = d[lt][0]
        # Interfered-with antenna horizon elevation angle and distance
        theta = 1000 * np.arctan((h[ii] - hrs) / (1000 * (dtot - d[ii])) - (dtot - d[ii]) / (2 * ae))
        theta_r = max(theta)
        kindex = np.where(theta == theta_r)
        lr = kindex[-1] + 1
        dlr = dtot - d[lr][0]
    else:
        theta_r = theta_rd
        ii = np.arange(1,n-1)
        # speed of light as per ITU.R P.2001
        lambda_ = 0.2998 / f
        Ce = 1 / ae
        nu = (h[ii] + 500 * Ce * d[ii] * (dtot - d[ii]) - (hts * (dtot - d[ii]) + hrs * d[ii]) / dtot) * np.sqrt(0.002 * dtot / (lambda_ * d[ii] * (dtot - d[ii])))      
        numax = max(nu)
        kindex = np.where(nu == numax)
        lt = kindex[-1] + 1
        dlt = d[lt][0]
        dlr = dtot - dlt
        lr = lt
    
    # Angular distance
    
    theta_tot = 1000.0 * dtot / ae + theta_t + theta_r
    
    # Section 5.6.3 Ducting/layer-reflection model
    
    # Calculate the smooth-Earth heights at transmitter and receiver as
# required for the roughness factor
    
    hst = min(hst,h[0])
    
    hsr = min(hsr,h[-1])
    
    # Slope of the smooth-Earth surface
    
    m = (hsr - hst) / dtot
    
    # The terminal effective heigts for the ducting/layer-reflection model
    
    hte = htg + h[0] - hst
    
    hre = hrg + h[-1] - hsr
    
    ii = np.arange(lt,lr+1)
    hm = max(h[ii] - (hst + m * d[ii]))
    
    return hst_n,hsr_n,hst,hsr,hstd,hsrd,hte,hre,hm,dlt,dlr,theta_t,theta_r,theta_tot,pathtype
 