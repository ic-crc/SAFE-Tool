MINIMAL_ANGLE_OF_INCIDENCE = 0.25 # degrees

RET_DB_LIMIT = 30 # dB

MINIMAL_CLUTTER_DEPTH = 2 # meters
MINIMAL_CLUTTER_HEIGHT = 2 # meters

## P1812 parameters

# Climatic zones
ZONE_COASTAL = 3
ZONE_INLAND = 4

# Water (1), open (2), suburban (3), urban/trees (4), Dense urban (5)  
# Water (0), open (0), suburban (10), urban/trees (15), Dense urban (20)  
CLUTTER_VALUES = {2: 0, 3: 10, 4: 15, 5:20}

# Time and location percentage for P1812
TIME_PERCENTAGE_P1812 = 50
LOCATION_PERCENTAGE_P1812 = 50