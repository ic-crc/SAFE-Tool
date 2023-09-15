import numpy as np
import math
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

def pochhammerhalfdivbyfact(nn):
    if (nn<0):
        print("Warning! Pochhammer's symbol not defined for negative n values")
        return
    if (nn < 171):
        #yy = scipy.special.gamma(nn+0.5)/(np.sqrt(np.pi)*scipy.special.factorial(nn))
        yy = math.gamma(nn+0.5)/(np.sqrt(np.pi)*math.factorial(nn))   
    else:
        yy = 1/np.sqrt(np.pi*nn)
    return yy


def KroneckerDeltaJN(jjj,nnn):
    if(jjj<0 or nnn<0):
        print("Warning, K-delta only defined for positive inputs")
        return
    if(jjj==nnn):
        return 1
    else:
        return 0


def IBnqof1(nn,qq):
    coeff3 = 1/(2*np.sqrt(np.pi))
    if(nn<0 or qq<0):
        print('Warning! Positive values only for the Boersma function!')
    if(nn >= 0 and qq == 0):
        return pochhammerhalfdivbyfact(nn)
    if (nn==0 and qq >= 0):
        return KroneckerDeltaJN(qq,0);  
    if(nn >= 1 and qq == 1):
        sumIB = 0
        for mm in range(0,nn):
            sumIB = sumIB + pochhammerhalfdivbyfact(mm)/np.sqrt(nn-mm)
        return coeff3*sumIB    
    if(nn >= 1 and qq > 1):
        sumIB = 0
        for mm in range(0,nn):
            sumIB = sumIB + IBnqof1(mm,qq-1)/np.sqrt(nn-mm)
        return coeff3*sumIB + 0.5*nn*(qq-1)*IBnqof1(nn,qq-2) 


def topDiffraction(freq,theta,hTrees,depthofforest,hRx):
    rmaxgfzero = 195
    #hRx = 3.7 # height of the ODU antenna in meters
    celer = 299792458 # Speed of light in vacuum (m/s)
    frequence = freq*1e9 # in Hz
    lambda_ = celer/frequence # meters
    Nedges = 40 # Number of knife edges
    d = depthofforest/Nedges # Spacing between knife edges in meters. 
    yNplusOne = hRx - hTrees
    gp = np.sqrt(d/lambda_)*np.sin(np.deg2rad(theta)) # Whitteker (2001), eq. (13)
    gf = yNplusOne/np.sqrt(lambda_*d) # Whitteker (2001), eq. (8)
    
    IBnqof1Array = np.zeros((Nedges,rmaxgfzero+1))
    
    for rr in range(Nedges): # 1 to Nedges
        IBnqof1Array[rr,1-1] = IBnqof1(rr+1,0)
        IBnqof1Array[rr,2-1] = IBnqof1(rr+1,1)   

    coeff11 = 1/(2*np.sqrt(np.pi))
    for cc in range(3,rmaxgfzero+1):  
        for rr in range(Nedges):     
            sum1 = KroneckerDeltaJN(cc-1,0)/np.sqrt(rr+1)
            for mmm in range(rr-1+1):
                sum1 = sum1 + IBnqof1Array[mmm,cc-1-1] / np.sqrt(rr+1-(mmm+1)) 
            IBnqof1Array[rr,cc-1] = 0.5*(rr+1)*(cc-2)*IBnqof1Array[rr,cc-2-1] + coeff11*sum1
  
    Coeff4 = 2*np.sqrt(complex(0,-np.pi)) # confirmed with matlab
    Coeff1 = np.exp(complex(0,np.pi*Nedges*gp*gp)) # confirmed with matlab
    SumH = 0 
    for rr in range(rmaxgfzero+1): # zero to rmaxgfzero
        if rr < 171:
            SumH = SumH + (np.power(Coeff4,rr)*np.power(gp,rr)*IBnqof1Array[Nedges-1,rr+1-1]) / math.factorial(rr)
        else:
            SumH = SumH + (np.exp(np.log(np.power(Coeff4,rr)) - math.lgamma(rr)))*np.power(gp,rr)*(IBnqof1Array[Nedges-1,rr+1-1])

    NormalizedHfieldatrooftop = np.abs(Coeff1*SumH)
    
    Aeq22 = NormalizedHfieldatrooftop/(2*np.pi*(-gf - 0.28))
    DiffractionLossEq22 = 20*np.log10(Aeq22)

    return DiffractionLossEq22