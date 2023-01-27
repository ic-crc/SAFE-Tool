# Function check_limit(var, low, hi, name)
#
# Checks the var to see if it's inbetween the range low <= var <= hi
# returns false if it's in range true if not


    
def check_limit(var = None,low = None,hi = None,name = None): 
    if ((var < low) or (var > hi)):
        raise Exception(name+' = '+str(var)+' is outside the limits: ['+str(low)+', '+str(hi)+'].')
        bool = True
        return bool
    
    bool = False
    
    return bool