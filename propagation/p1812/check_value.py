

# Function check_value(var, vals, name)
#
# Checks the var (elements) to see if they belong to the values defined in
# vals
# returns false if it's in range true if not

import numpy as np
    
def check_value(var = None,vals = None,name = None): 
    d = np.in1d(var,vals)
    inds = np.where(d == False)
    kk = var[inds]
    if (not len(kk)==0 ):
        raise Exception(name+' may only contain the following values: '+str(vals)+'.')
        bool = True
        return bool
    
    bool = False
    return bool