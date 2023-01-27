

def earth_rad_eff(DN = None): 
    #earth_rad_eff Median value of the effective Earth radius
#     [ae, ab] = earth_rad_eff(DN)
#     This function computes the median value of the effective earth
#     radius, and the effective Earth radius exceeded for beta0# of time
#     as defined in ITU-R P.1812-4.
    
    #     Input arguments:
#     DN      -   the average radiorefractive index lapse-rate through the
#                 lowest 1 km of the atmosphere (N-units/km)
    
    #     Output arguments:
#     ae      -   the median effective Earth radius (km)
#     ab      -   the effective Earth radius exceeded for beta0 # of time
    
    #     Example:
#     [ae, ab] = earth_rad_eff(DN)
    
    k50 = 157 / (157 - DN)
    
    ae = 6371 * k50
    
    kbeta = 3
    ab = 6371 * kbeta
    
    return ae,ab
   