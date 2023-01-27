

from propagation.p1812.dl_se_ft_inner import dl_se_ft_inner
    
def dl_se_ft(d = None,hte = None,hre = None,adft = None,f = None,omega = None): 
    #dl_se_ft First-term part of spherical-Earth diffraction according to ITU-R P.1812-4
#   This function computes the first-term part of Spherical-Earth diffraction
#   loss exceeded for p# time for antenna heights
#   as defined in Sec. 4.3.3 of the ITU-R P.1812-4
    
    #     Input parameters:
#     d       -   Great-circle path distance (km)
#     hte     -   Effective height of interfering antenna (m)
#     hre     -   Effective height of interfered-with antenna (m)
#     adft    -   effective Earth radius (km)
#     f       -   frequency (GHz)
#     omega   -   fraction of the path over sea
    
    #     Output parameters:
#     Ldft   -   The first-term spherical-Earth diffraction loss not exceeded for p# time
#                Ldft(1) is for the horizontal polarization
#                Ldft(2) is for the vertical polarization
    
    #     Example:
#     Ldft = dl_se_ft(d, hte, hre, adft, f, omega)
    
    # First-term part of the spherical-Earth diffraction loss over land
    
    epsr = 22
    sigma = 0.003
    Ldft_land = dl_se_ft_inner(epsr,sigma,d,hte,hre,adft,f)
    # First-term part of the spherical-Earth diffraction loss over sea
    
    epsr = 80
    sigma = 5
    Ldft_sea = dl_se_ft_inner(epsr,sigma,d,hte,hre,adft,f)
    # First-term spherical diffraction loss
    
    Ldft = omega * Ldft_sea + (1 - omega) * Ldft_land
    
    # floatformat= '#.10g;\n';
# fid = fopen('Ldsph.csv', 'a');
# fprintf(fid,['Ldft land hor ;Eq (28);;' floatformat],Ldft_land(1));
# fprintf(fid,['Ldft land ver ;Eq (28);;' floatformat],Ldft_land(2));
# fprintf(fid,['Ldft sea hor ;Eq (28);;' floatformat],Ldft_sea(1));
# fprintf(fid,['Ldft sea ver ;Eq (28);;' floatformat],Ldft_sea(2));
# fprintf(fid,['Ldft hor ;Eq (28);;' floatformat],Ldft(1));
# fprintf(fid,['Ldft ver ;Eq (28);;' floatformat],Ldft(2));
# fprintf(fid,'\n');
#fid.close()
    
    return Ldft
    