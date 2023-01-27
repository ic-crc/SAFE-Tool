

import pandas as pd

import easygui

import tkinter.filedialog

from tl_p1812SAFE import tl_p1812SAFE

from great_circle_path import great_circle_path

from InterpolateDN50andN050CTR import InterpolateDN50andN050CTR

#import pdb;pdb.set_trace()

p = 50 # Required time percentage for which the calculated basic transmission loss is not exceeded (1<=p<=50%).

# Import path profile data

if __name__ == '__main__':
    root = tkinter.Tk()
    root.withdraw()

    filenameTerrain= tkinter.filedialog.askopenfilename()

    csv_data = pd.read_csv(filenameTerrain)

    data_matrix = csv_data.iloc[1:,:]

    terrainData =  data_matrix.to_numpy()

    terrainData = terrainData.astype(float)

    # Extracts input data from the terrainData matrix

    d = terrainData[:,0] / 1000 # vector of distances di of the i-th profile point (km). Note that P.1812-6 expects that d be in km (see Table 5).

    h = terrainData[:,1] # vector of heights hi of the i-th profile point (meters above mean sea level); these are the HRDEM DTM data. Note that P.1812-6 expects that h be in meters.
    
    R = terrainData[:,3] # vector of representative clutter height Ri (m) of the i-th profile point (m); these are assumed to be all tree height data (15 m) or 0m for water or open/rural clutter types. HRDEM DSM data are not used.

    Ct = terrainData[:,2] # vector of representative clutter type Cti of the i-th profile point: Water/sea (1), Open/rural (2), Suburban (3), Urban/trees/forest (4), Dense urban (5). If empty or all zeros, the default clutter used is Open/rural

    zone = terrainData[:,4]  # vector of radio-climatic zone types: Inland (4), Coastal land (3), or Sea (1).

    # Dialog boxes for frequency, hTx & hRx

    freq = easygui.enterbox("Enter the frequency in GHz:")

    freq = float(freq)

    hTx = easygui.enterbox('Enter the Tx antenna height in meters:')

    hTx= float(hTx) #htg in P.1812: Tx Antenna center height above ground level (m)

    hRx = easygui.enterbox('Enter the Rx antenna height in meters:')

    hRx= float(hRx) #hrg in P.1812: Rx Antenna center height above ground level (m)

    #########

    phi_t = terrainData[0,6] # Latitude of Tx (degrees).

    lam_t = terrainData[1,6] # Longitude of Tx (degrees).

    phi_r = terrainData[2,6] # Latitude of Rx (degrees).

    lam_r = terrainData[3,6] # Longitude of Rx (degrees).

    pol = 2 # polarization of the signal (1) horizontal, (2) vertical.

    pL = 50 # Required percentage of LOCATIONS for which the calculated basic transmission loss is not exceeded (1% - 99%).

    sigmaL = 0 # Location variability set to 0 for point-to-point links.

    dpnt = 0.5 * (d[-1] - d[0])

    Phipnte,Phipntn,Bt2r,dgc = great_circle_path(lam_r,lam_t,phi_r,phi_t,6371,dpnt)

    DN50PCR,N050PCR = InterpolateDN50andN050CTR(Phipntn,(Phipnte + 360))

    KFactor50 = 157 / (157 - DN50PCR)

    # flag4 should be set to 0. No need to set it here (done in tl_p1812).

    Lb = tl_p1812SAFE(freq, p, d, h, R, Ct, zone, hTx, hRx, pol, phi_t, phi_r, lam_t, lam_r, pL, sigmaL, DN50PCR, N050PCR); # New format for P.1812-6.

    print('The path loss not exceeded '+ str(p) + '% of the time is equal to '+ str(float(f'{Lb: .2f}')) +' dB.');