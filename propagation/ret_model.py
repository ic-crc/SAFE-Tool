import numpy as np
import math
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

### Useful functions

def DeltaJN(jjj,nnn):
    zz = 1 if jjj==nnn else 0
    return zz

def Fn(idxn,mu,mu_n,N):
    smalleps = 1e-9
    yy=0
    
    if idxn == 0:
        yy=0
        if( ( (abs(mu+1) < smalleps) or (mu>-1) ) and ( (mu<mu_n[2-1]) or (abs(mu-mu_n[2-1])<smalleps) ) ):
            yy = (mu_n[2-1] - mu)/(mu_n[2-1]+1)
            #print('idxn = 0: ',mu_n[2-1])
            #print('idxn N')
          
    elif idxn == N:
        yy=0
        if( (abs(mu-1) < smalleps or (mu < 1)) and ( (mu>mu_n[N-1]) or (abs(mu-mu_n[N-1])<smalleps)) ):
            yy = (mu - mu_n[N-1])/(1 - mu_n[N-1]) 
            #print('idxn = N: ', mu_n[N-1])
            #print('idxn N')
            
    else:
        #idxn = idxn-1 # correct for python's count from zero
        yy=0
        if( (abs(mu-mu_n[idxn-1]) < smalleps or (mu > mu_n[idxn-1])) and ( (mu<mu_n[idxn+1-1]) or (abs(mu-mu_n[idxn+1-1])<smalleps)) ):
            yy = (mu - mu_n[idxn-1])/(mu_n[idxn+1-1] - mu_n[idxn-1])
            #print('else, step 1')
            
        if( (abs(mu-mu_n[idxn+1-1]) < smalleps or (mu > mu_n[idxn+1-1])) and ( (mu<mu_n[idxn+2-1]) or (abs(mu-mu_n[idxn+2-1])<smalleps)) ):
            yy = (mu_n[idxn+2-1] - mu)/(mu_n[idxn+2-1] - mu_n[idxn+1-1])
            #print('else, step 2')
            
    return yy


############ MAIN CODE ############### 

def ret_model_computation(Depth_fromPipeline, thetaP_fromPipeline, frequency, Rx_beamwidth=10.8, Foliage_type="", in_leaf = True):
    
    # Base station parameters
    f = frequency/1E9 # Frequency
    thetaP = thetaP_fromPipeline
    phiP = 0 # phiP_fromPipeline
    
    # ODU parameters
    DeltagR = Rx_beamwidth
    thetaR = thetaP
    phiR = 0
    
    TreeType = Foliage_type # currently unused
    zmax = Depth_fromPipeline # depth of foliage
    
    zres = zmax # forces a single measurement point
    
    # vegetation depth
    if(zmax==zres):
        z = np.array([zmax])
    else:
        z = np.linspace(zres,zmax,int(zmax/zres))
        
        
    if(Foliage_type == 'conifer'):
        a = 0.70
        b =  70
        W = 0.78
        sigmaT = 0.215

    elif(Foliage_type == 'deciduous' and in_leaf == True):
        a = 0.95
        b = 42
        W = 0.95
        sigmaT = 0.147

    elif(Foliage_type == 'deciduous' and in_leaf == False):
        a = 0.90
        b = 16
        W = 0.95
        sigmaT = 0.221

    elif(Foliage_type == 'mixed' and in_leaf == True):
        a = 0.825
        b = 56
        W = 0.865
        sigmaT = 0.181

    elif(Foliage_type == 'mixed' and in_leaf == False):
        a = 0.8
        b = 43
        W = 0.95
        sigmaT = 0.218

    else:
        # nominal tree
        a = 0.92 # ratio of forward-sctt power to total
        b = 103 # beamwidth of phase function (degrees)
        W = 0.87 # albedo (strong ab < 0.5, strong scat > 0.9)
        sigmaT = 0.603 # combined absortion & scatter coeff
    
    ### Algorithm Parameters ####
    N = 15 # Odd int, 11<=N<-21
    M = 10 # M=10 suitable for most cases
    
    # convert degrees to radians
    thetaP = np.deg2rad(thetaP)
    phiP = np.deg2rad(phiP)
    thetaR = np.deg2rad(thetaR)
    phiR = np.deg2rad(phiR)
    DeltagR = np.deg2rad(DeltagR)
    b = np.deg2rad(b)
    
    # Find the attenuation coefficients s_k for k = (N+1)/2 to N, as positive solutions of eq.(12), P.833-9:
    What = ((1-a)*W)/(1-a*W)
    bs=0.6*b
    
    mu_n = np.zeros((N+1,1)) 
    for n in range(N+1): # RANGE 0 to N is range(N+1)
        #print(n)
        mu_n[n]=-np.cos(n*np.pi/N)
    
    # Pn by Johnson & Schwering (30b) or P.833-9 for n = 1, ... , N-1:
    Pn = np.zeros((N+1,1))
    for n in range(N+1):
        Pn[n]=np.sin(np.pi/N)*np.sin(n*np.pi/N)
    end_value = np.power(np.sin(np.pi/(2*N)),2)
    Pn[0] = end_value
    Pn[N] = end_value
    
    # Evaluate the LHS of (12) for 60N values of s between 0 and +1, omitting 0, 0.5 and 1
    s = np.zeros((300*N,1))
    L12 = np.zeros((300*N,1))
    kMin = int((N+1)/2)
    sk = np.zeros((kMin,1))
    lk = np.zeros((kMin,1))
    k = -1
    
    for j in range(0,300*N):
        s[j] = (j+1-0.3)/(50*N)
        
        for n in range(N+1):
            L12[j] = L12[j] + Pn[n]/(1-mu_n[n]/s[j])
            
        L12[j]=L12[j]*What/2
        
        if j > 0:
            if L12[j] <= 1 and L12[j-1] >= 1:
                k = k + 1
                lk[k]=1
                sk[k]=(s[j]*(L12[j-1]-1)+s[j-1]*(1-L12[j]))/(L12[j-1]-L12[j])
    
    if k < kMin-1:
        print("Warning - the algorithm found less than ", kMin, " eigenvalues.")
    skC = sk
    
    #########################
           
    sum_ = np.zeros((kMin,1))
    for kk in range(0,kMin):
        sum_[kk] = np.sin(np.pi/(2*N))*np.sin(np.pi/(2*N))/(1 + 1/skC[kk]) + np.sin(np.pi/(2*N))*np.sin(np.pi/(2*N))/(1 - 1/skC[kk])
        
        for nn in range(1,N):
            sum_[kk] = sum_[kk] + (np.sin(np.pi/(N))*np.sin((nn)*np.pi/(N)))/(1 + np.cos((nn)*np.pi/N)/skC[kk])
    
    FinalSum = 0.5*What*sum_
    ErrorEq12 = FinalSum - 1
    
    # Find the amplitude factors A_k as solutions of eq.(13):
    # matrix formulation (13) as X*A = D
    
    X = np.zeros((kMin,kMin))
    D = np.zeros((kMin,1))
    
    # Format: X*A = D,  where X is of dimensions (N+1)/2, (N+1)/2), vector A is ((N+1)/2,1), vector D is ((N+1)/2,1).
    # Construction of matrix X:
    for i in range(0,kMin):
        for j in range(0,kMin):
            X[i,j] = 1 / (1-mu_n[(i)+kMin]/sk[j])
    
    muP = np.cos(thetaP)
    
    to_sort = abs(muP - mu_n)
    nestm = np.where(to_sort == np.amin(to_sort))[0]
    jj = nestm - 1
    
    for n in range(kMin,N):
        D[(n-kMin+1,0)] = DeltaJN(jj,n) / Pn[jj+1]
    
    A = np.linalg.lstsq(X,D,rcond=None)[0]
    Nn = np.linalg.norm(np.matmul(X,A) - D) 
    # note this is where MATLAB and PYTHON DIVERGE SLIGHTLY
    # The LSTSQ is slightly more accurate than MATLAB's X\D numerical approach
    # the downstream consequences appear to be negligible
    
    tt = np.size(z)
    LscatPredicted = np.zeros((tt,1))
    tau = sigmaT*z
    tauHat = (1-a*W)*tau
    muR = np.cos(thetaR)
    argPR = (1-muP*muP)*(1-muR*muR)
    gammaPR = np.arccos(np.cos(phiP-phiR)*np.sqrt(argPR) + muP*muR)
    
    LscatPredicted = np.zeros((tt,1))
    
    for oo in range(tt):
        
        qMbar = 4/(pow(DeltagR,2) + M*bs*bs)*np.exp(-(pow(gammaPR,2)) / (pow(DeltagR,2) + M*bs*bs))
    
        mSum = 0
        
        for m in range(M):
            qmbar = 4/(pow(DeltagR,2) + (m+1)*bs*bs)*np.exp(-(pow(gammaPR,2)) / (pow(DeltagR,2) + (m+1)*bs*bs))
            mSum = mSum + ((a*W*tau[oo]/muP)**(m+1))*(qmbar-qMbar)/math.factorial(m+1)
    
        Lscat = np.exp(-(gammaPR/DeltagR)**2 - tau[oo]/muP) + ((DeltagR**2)/4)*( (np.exp(-tauHat[oo]/muP) - np.exp(-tau[oo]/muP))*qMbar + np.exp(-tau[oo]/muP)*mSum)
    
    
        kSum = 0
        for k in range(kMin):
            nSum = 0
            for n in range(N+1):
                nSum = nSum + Fn(n,muR,mu_n,N)/(1-(mu_n[n]/sk[k]))
            kSum = kSum + A[k]*np.exp(-tauHat[oo]/sk[k])*nSum
        
        if(kSum<0):
            kSum = 0
            
        
        Lscat = Lscat + ((DeltagR**2)/2)*((-np.exp(-tauHat[oo]/muP)*Fn(jj+1,muR,mu_n,N)/Pn[jj+1]) + kSum)
        Lscat = -10*np.log10(Lscat)
        LscatPredicted[oo] = Lscat
    
    return LscatPredicted

