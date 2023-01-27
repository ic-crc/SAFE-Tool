
from os.path import join, dirname, realpath
import numpy as np

DN50 = np.loadtxt(join(dirname(realpath(__file__)),"DN50.txt"))
N050 = np.loadtxt(join(dirname(realpath(__file__)),"N050.txt"))
    
def InterpolateDN50andN050CTR(lat = None,lon = None): 
    #import pdb;pdb.set_trace()
    # Computes the median annual refractivity gradient in the lowest first km of the troposphere (DN50) and the median annual refractivity at sea level (N050) given the lat/long coordinates
    # at the path centre using bilinear interpolation (see Section 1b of P.1144-11, on page 13).
    # Inputs:
    #   lat: latitude of the path centre (degrees);
    #   lon: longitude of the path centre (degrees). For negative longitudes, add 360 degrees. For example, for 75 degrees West (-75 degrees), lon is equal to 285 degrees.
    # Outputs:
    #   DN50atthePathCentre in N-units/km;
    #   N050atthePathCentre in N-units.
    # Integral data products from P.1812-6:
    
    
    # The DN50 & N050 maps have a 1.5-degree resolution:
    latCeilPos = int(np.floor((90 - lat) / 1.5)) + 1
    latFloorPos =int(np.ceil((90 - lat) / 1.5)) + 1
    lonCeilPos = int(np.ceil(lon / 1.5)) + 1
    lonFloorPos = int(np.floor(lon / 1.5)) + 1
    
    # Interpolating corners
    c = lon / 1.125 + 1
    r = (90 - lat) / 1.125 + 1
    C = int(np.floor(lon / 1.125)) + 1
    R = int(np.floor((90 - lat) / 1.125)) + 1

    # Bi-linear interpolation for median, annual refractivity gradient in the
    # lowest first km of the troposphere:
    DNtopleft = DN50[latCeilPos-1, lonFloorPos-1]
    DNbottomleft = DN50[latFloorPos-1, lonFloorPos-1]
    DNtopright = DN50[latCeilPos-1, lonCeilPos-1]
    DNbottomright = DN50[latFloorPos-1 ,lonCeilPos-1]
    DN50atthePathCentre = DNtopleft * (R + 1 - r) * (C + 1 - c) + DNbottomleft * (r - R) * (C + 1 - c) + DNtopright * (R + 1 - r) * (c - C) + DNbottomright * (r - R) * (c - C)
    
    # Bi-linear interpolation for median, annual sea-level refractivity:
    N0topleft = N050[latCeilPos-1, lonFloorPos-1]
    N0bottomleft = N050[latFloorPos-1, lonFloorPos-1]
    N0topright = N050[latCeilPos-1, lonCeilPos-1]
    N0bottomright = N050[latFloorPos-1, lonCeilPos-1]
    N050atthePathCentre = N0topleft * (R + 1 - r) * (C + 1 - c) + N0bottomleft * (r - R) * (C + 1 - c) + N0topright * (R + 1 - r) * (c - C) + N0bottomright * (r - R) * (c - C)
    
    return DN50atthePathCentre, N050atthePathCentre
    
