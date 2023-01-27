

def stdDev(f = None,h = None,R = None,wa = None): 
    #stdDev computes standard deviation of location variability
#   sigmaLoc = stdDev(f, h, R, wa)
#   This function computes the standard deviation according to ITU-R
#   P.1812-5, Annex 1, §4.8 and §4.10
#     Input parameters:
#     f       -   Frequency (GHz)
#     h       -   receiver/mobile antenna height above the ground (m)
#     R       -   height of representative clutter at the receiver/mobile location (m)
#     wa      -   prediction resolution, i.e., the width of the square area over which the variability applies
    
    # note that there is a typo in ITU-R P.1814-5 in equation (66)
# the coefficient multiplying f should be 0.024 and not 0.0024
# this will be corrected at the 2020 WP 3K meeting
    
    sigmaLoc = (0.52 + 0.024 * f) * wa ** 0.28
    if (h < R):
        uh = 1
    else:
        if (h >= R + 10):
            uh = 0
        else:
            uh = 1 - (h - R) / 10
    
    sigmaLoc = sigmaLoc * uh
    return sigmaLoc