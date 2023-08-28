from geographiclib.geodesic import Geodesic as geo
from geopy.distance import geodesic

def get_distance_to_tower(latlon, tower_lat_lon):
    return int(geodesic(latlon, tower_lat_lon).m)

def get_heading(latlon, tower_latlon):
    
    lat, lon = latlon
    tower_lat, tower_lon = tower_latlon
    
    brng = 180 + geo.WGS84.Inverse(lat, lon, tower_lat, tower_lon)['azi1']
    direction = (brng - 180) if brng > 180 else (brng + 180) 
    
    return direction

class Tx:
    def __init__(self, lat, lon, height, frequency):
        self.lat = lat
        self.lon = lon
        self.height = height if height >= 1 else 1
        self.frequency = frequency # in MHz

class Rx:
    def __init__(self, lat, lon, height, beamwidth = 10.8):
        self.lat = lat
        self.lon = lon
        self.height = height if height >= 1 else 1
        self.beamwidth = beamwidth # in degrees 
