

from propagation.p1812.find_intervals import find_intervals

import numpy as np

def path_fraction(d = None,zone = None,zone_r = None): 
    #path_fraction Path fraction belonging to a given zone_r
#     omega = path_fraction(d, zone, zone_r)
#     This function computes the path fraction belonging to a given zone_r
#     of the great-circle path (km)
    
    #     Input arguments:
#     d       -   vector of distances in the path profile
#     zone    -   vector of zones in the path profile
#     zone_r  -   reference zone for which the fraction is computed
    
    #     Output arguments:
#     omega   -   path fraction belonging to the given zone_r
    
    #     Example:
#     omega = path_fraction(d, zone, zone_r)
    
    dm = 0
    start,stop = find_intervals((zone == zone_r))
    n = len(start)
    for i in np.arange(n):
        delta = 0
        if d[stop[i]] < d[-1]:
             delta = delta + (d[stop[i] + 1] - d[stop[i]]) / 2.0
        if d[start[i]] > 0:
             delta = delta + (d[stop[i]] - d[stop[i] - 1]) / 2.0
        dm = dm + d[stop[i]] - d[start[i]] + delta
    
    omega = dm / (d[-1] - d[0])
    return omega