

from propagation.p1812.dl_se_ft import dl_se_ft

import numpy as np
    
def dl_se(d = None,hte = None,hre = None,ap = None,f = None,omega = None): 
    #import pdb;pdb.set_trace()
    #dl_se spherical-Earth diffraction loss exceeded for p# time according to ITU-R P.1812-4
#   This function computes the Spherical-Earth diffraction loss exceeded
#   for p# time for antenna heights hte and hre (m)
#   as defined in Sec. 4.3.2 of the ITU-R P.1812-4
    
    #     Input parameters:
#     d       -   Great-circle path distance (km)
#     hte     -   Effective height of interfering antenna (m)
#     hre     -   Effective height of interfered-with antenna (m)
#     ap      -   the effective Earth radius in kilometers
#     f       -   frequency expressed in GHz
#     omega   -   the fraction of the path over sea
    
    #     Output parameters:
#     Ldsph   -   The spherical-Earth diffraction loss not exceeded for p# time
#                 Ldsph(1) is for the horizontal polarization
#                 Ldsph(2) is for the vertical polarization
    
    #     Example:
#     Ldsph = dl_se(d, hte, hre, ap, f, omega)
    
    ## Body of function
    
    # Wavelength in meters
# speed of light as per ITU.R P.2001
    lambda_ = 0.2998 / f
    # Calculate the marginal LoS distance for a smooth path
    
    dlos = np.sqrt(2 * ap) * (np.sqrt(0.001 * hte) + np.sqrt(0.001 * hre))
    
    if d >= dlos:
        # calculate diffraction loss Ldft using the method in Sec. 4.3.3 for
# adft = ap and set Ldsph to Ldft
        Ldsph = dl_se_ft(d,hte,hre,ap,f,omega)
        #     floatformat= '#.10g;\n';
#     fid = fopen('Ldsph.csv', 'a');
#     fprintf(fid,['dlos (km);Eq (22);;' floatformat],dlos);
#     fprintf(fid,['Ldsph (dB);Eq (27);;' floatformat],Ldsph(1));
#     fprintf(fid,[';;;\n']);
#fid.close()
        return Ldsph
    else:
        # calculate the smallest clearance between the curved-Earth path and
# the ray between the antennas, hse
        c = (hte - hre) / (hte + hre)
        m = 250 * d * d / (ap * (hte + hre))
        b = 2 * np.sqrt((m + 1) / (3 * m)) * np.cos(np.pi / 3 + 1 / 3 * np.arccos(3 * c / 2 * np.sqrt(3 * m / ((m + 1) ** 3))))
        dse1 = d / 2 * (1 + b)
        dse2 = d - dse1
        hse = (hte - 500 * dse1 * dse1 / ap) * dse2 + (hre - 500 * dse2 * dse2 / ap) * dse1
        hse = hse / d
        # Calculate the required clearance for zero diffraction loss
        hreq = 17.456 * np.sqrt(dse1 * dse2 * lambda_ / d)
        if hse > hreq:
            Ldsph = np.array([0,0])
            floatformat = '%.10g;\n'
            #         fid = fopen('Ldsph.csv', 'a');
#         fprintf(fid,['dlos (km);Eq (22);;' floatformat],dlos);
#         fprintf(fid,['hse (m);Eq (23);;' floatformat],hse);
#         fprintf(fid,['dse1 (km);Eq (24a);;' floatformat],dse1);
#         fprintf(fid,['dse2 (km);Eq (24b);;' floatformat],dse2);
#         fprintf(fid,['b ;Eq (24c);;' floatformat],b);
#         fprintf(fid,['c ;Eq (24d);;' floatformat],c);
#         fprintf(fid,['mc ;Eq (24e);;' floatformat],m);
#         fprintf(fid,['hreq (m);Eq (25);;' floatformat],hreq);
#         fprintf(fid,['aem (km);Eq (26);;' floatformat],aem);
#         fprintf(fid,['Ldsph (dB);Eq (27);;' floatformat],Ldsph(1));
#         fprintf(fid,[';;;\n']);
#fid.close()
            return Ldsph
        else:
            # calculate the modified effective Earth radius aem, which gives
# marginal LoS at distance d
            aem = 500 * (d / (np.sqrt(hte) + np.sqrt(hre))) ** 2
            # Use the method in Sec. 4.3.3 for adft = aem to obtain Ldft
            Ldft = dl_se_ft(d,hte,hre,aem,f,omega)
            if Ldft[0] < 0 and Ldft[1]<0:
                Ldsph = np.array([0,0])
                floatformat = '%.10g;\n'
                #             fid = fopen('Ldsph.csv', 'a');
#             fprintf(fid,['dlos (km);Eq (22);;' floatformat],dlos);
#             fprintf(fid,['hse (m);Eq (23);;' floatformat],hse);
#             fprintf(fid,['dse1 (km);Eq (24a);;' floatformat],dse1);
#             fprintf(fid,['dse2 (km);Eq (24b);;' floatformat],dse2);
#             fprintf(fid,['b ;Eq (24c);;' floatformat],b);
#             fprintf(fid,['c ;Eq (24d);;' floatformat],c);
#             fprintf(fid,['mc ;Eq (24e);;' floatformat],m);
#             fprintf(fid,['hreq (m);Eq (25);;' floatformat],hreq);
#             fprintf(fid,['aem (km);Eq (26);;' floatformat],aem);
#             fprintf(fid,['Ldsph (dB);Eq (27);;' floatformat],Ldsph(1));
#             fprintf(fid,[';;;\n']);
#fid.close();
                return Ldsph
            else:
                Ldsph = (1 - hse / hreq) * Ldft
    
    # floatformat= '#.10g;\n';
# fid = fopen('Ldsph.csv', 'a');
# fprintf(fid,['dlos (km);Eq (22);;' floatformat],dlos);
# fprintf(fid,['hse (m);Eq (23);;' floatformat],hse);
# fprintf(fid,['dse1 (km);Eq (24a);;' floatformat],dse1);
# fprintf(fid,['dse2 (km);Eq (24b);;' floatformat],dse2);
# fprintf(fid,['b ;Eq (24c);;' floatformat],b);
# fprintf(fid,['c ;Eq (24d);;' floatformat],c);
# fprintf(fid,['mc ;Eq (24e);;' floatformat],m);
# fprintf(fid,['hreq (m);Eq (25);;' floatformat],hreq);
# fprintf(fid,['aem (km);Eq (26);;' floatformat],aem);
# fprintf(fid,['Ldsph (dB);Eq (27);;' floatformat],Ldsph(1));
# fprintf(fid,[';;;\n']);
    
    
    #fid.close();
    
    return Ldsph
   