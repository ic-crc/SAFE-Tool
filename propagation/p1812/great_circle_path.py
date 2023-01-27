


import numpy as np
    
def great_circle_path(Phire = None,Phite = None,Phirn = None,Phitn = None,Re = None,dpnt = None): 
    #great_circle_path Great-circle path calculations according to Attachment H
#   This function computes the great-circle intermediate points on the
#   radio path as defined in ITU-R P.2001-2 Attachment H
    
    #     Input parameters:
#     Phire   -   Receiver longitude, positive to east (deg)
#     Phite   -   Transmitter longitude, positive to east (deg)
#     Phirn   -   Receiver latitude, positive to north (deg)
#     Phitn   -   Transmitter latitude, positive to north (deg)
#     Re      -   Average Earth radius (km)
#     dpnt    -   Distance from the transmitter to the intermediate point (km)
    
    #     Output parameters:
#     Phipnte -   Longitude of the intermediate point (deg)
#     Phipntn -   Latitude of the intermediate point (deg)
#     Bt2r    -   Bearing of the great-circle path from Tx towards the Rx (deg)
#     dgc     -   Great-circle path length (km)
    
    #     Example:
#     [Bt2r, Phipnte, Phipntn, dgc] = great_circle_path(Phire, Phite, Phirn, Phitn, Re, dpnt)
    
    ## H.2 Path length and bearing
    
    # Difference (deg) in longitude between the terminals (H.2.1)
    
    Dlon = Phire - Phite
    # Calculate quantity r (H.2.2)
    
    r = np.sin(np.pi/180*Phitn) * np.sin(np.pi/180*Phirn) + np.cos(np.pi/180*Phitn) * np.cos(np.pi/180*Phirn) * np.cos(np.pi/180*Dlon)
    # Calculate the path length as the angle subtended at the center of
# average-radius Earth (H.2.3)
    
    Phid = np.arccos(r)
    
    # Calculate the great-circle path length (H.2.4)
    
    dgc = Phid * Re
    
    # Calculate the quantity x1 (H.2.5a)
    
    x1 = np.sin(np.pi/180*Phirn) - r * np.sin(np.pi/180*Phitn)
    # Calculate the quantity y1 (H.2.5b)
    
    y1 = np.cos(np.pi/180*Phitn) * np.cos(np.pi/180*Phirn) * np.sin(np.pi/180*Dlon)
    # Calculate the bearing of the great-circle path for Tx to Rx (H.2.6)
    
    if (np.abs(x1) < 1e-09 and np.abs(y1) < 1e-09):
        Bt2r = Phire
    else:
        Bt2r = (180/np.pi)*np.arctan2(y1,x1)
    
    ## H.3 Calculation of intermediate path point
    
    # Calculate the distance to the point as the angle subtended at the center
# of average-radius Earth (H.3.1)
    
    Phipnt = dpnt / Re
    
    # Calculate quantity s (H.3.2)
    
    s = np.sin(np.pi/180*Phitn) * np.cos(Phipnt) + np.cos(np.pi/180*Phitn) * np.sin(Phipnt) * np.cos(np.pi/180*Bt2r)
    # The latitude of the intermediate point is now given by (H.3.3)
    
    Phipntn = (180/np.pi)*np.arcsin(s)
    
    # Calculate the quantity x2 (H.3.4a)
    
    x2 = np.cos(Phipnt) - s * np.sin(np.pi/180*Phitn)
    # Calculate the quantity y2 (H.3.4b)
    
    y2 = np.cos(np.pi/180*Phitn) * np.sin(Phipnt) * np.sin(np.pi/180*Bt2r)
    # Calculate the longitude of the intermediate point Phipnte (H.3.5)
    
    if (x2 < 1e-09 and y2 < 1e-09):
        Phipnte = Bt2r
    else:
        Phipnte = Phite + (180/np.pi)*np.arctan2(y2,x2)
    
    return Phipnte,Phipntn,Bt2r,dgc
    