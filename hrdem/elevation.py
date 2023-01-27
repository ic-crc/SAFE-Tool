import numpy as np
import requests

from geopy.distance import geodesic
from utm import from_latlon
from os.path import join

from hrdem.hrdem import get_dtm_dsm_index_along_path, get_dataset_footprint, out_folder_numpy
from propagation.tower import get_heading

dataset_fp = get_dataset_footprint()

def double_array(array):
    new_arr = np.repeat(np.repeat(array, 2, axis=1), [2]*len(array), axis=0)
    return new_arr.astype(float)

def compute_x_y_index(lat_lon, tower_latlon, distance_to_tower, utm_number):
    
    # get all the index of the line between rx and tx
    x_tx, y_tx, _, _ = from_latlon(tower_latlon[0], tower_latlon[1], utm_number)
    x_rx, y_rx, _, _ = from_latlon(lat_lon[0], lat_lon[1], utm_number)
    x_index, y_index = np.linspace(round(x_tx), round(x_rx), distance_to_tower), np.linspace(round(y_tx), round(y_rx), distance_to_tower)

    return x_index, y_index

def read_numpy_array(hrdem_idx): 
    with open(join(out_folder_numpy, f"{hrdem_idx}.npy"), 'rb') as f:
        dsm_array = np.load(f)
        dtm_array = np.load(f)
        bounds = np.load(f)
                
        # Replace all negative measurements to 0
        dsm_array[dsm_array<0] = 0
        dtm_array[dtm_array<0] = 0

        # If file has a 2m resolution
        if abs(bounds[2] - bounds[0]) == 20_000 and abs(bounds[3] - bounds[1]) == 20_000:
            dsm_array = double_array(dsm_array)
            dtm_array = double_array(dtm_array)
            
    return dsm_array, dtm_array, bounds


def return_elevation_profile(lat_lon, tower_latlon, distance_to_tower):

    intersection_line, utm_number = get_dtm_dsm_index_along_path(dataset_fp, lat_lon, tower_latlon)
    
    # Return if no HRDEM tiles are available
    if len(intersection_line) == 0:
        return np.zeros(distance_to_tower), np.zeros(distance_to_tower)
        
    # If tiles have been found
    x_index, y_index = compute_x_y_index(lat_lon, tower_latlon, distance_to_tower, utm_number)
    
    # Initialize arrays
    full_surface_h = np.zeros(len(x_index)) ; full_terrain_h = np.zeros(len(x_index)) ; seen_segment = []; segment_already_full = []
    
    # For tiles within that segment (multiple HRDEM could be on top of each other)
    for hrdem_idx, itrsct in intersection_line.values:
        
        # If more recent HRDEM points already have been added
        if itrsct in segment_already_full: continue
            
        # read numpy array from pre-downloaded folder
        dsm_array, dtm_array, bounds = read_numpy_array(hrdem_idx)

        # Extract idx within that tile
        idx_list = [(int(obj[0]-bounds[0]), int((bounds[3]-bounds[1]) - (obj[1]-bounds[1])), d) for d, obj in enumerate(zip(x_index, y_index)) if bounds[2] > int(obj[0]) >= bounds[0] and bounds[3] >= int(obj[1]) > bounds[1]]
        
        if len(idx_list) == 0: continue
        
        # Unzip idx 
        x_idx, y_idx, d = zip(*idx_list)
        x_idx = np.array(x_idx); y_idx = np.array(y_idx); d_list = list(d)

        # Do this only once per segment (for speed purpose)
        # if the x_index, y_index has not been extracted for that segment
        if itrsct not in seen_segment :
            seen_segment.append(itrsct)
            # Extract elevation profile for that tile    
            full_surface_h[d_list] = dsm_array[(y_idx, x_idx)]                    
            full_terrain_h[d_list] = dtm_array[(y_idx, x_idx)]                    

        # For the second, third, ... tile, for the same x_index, y_index as before
        # We compute the elevation profile 
        else:
            full_surface_h[d_list] = np.where(full_surface_h[d_list] == 0, dsm_array[(y_idx, x_idx)], full_surface_h[d_list])
            full_terrain_h[d_list] = np.where(full_terrain_h[d_list] == 0, dtm_array[(y_idx, x_idx)], full_terrain_h[d_list])

        # If surface already completed for that segment, break out of that segment (for speed purpose)
        if 0 not in full_surface_h[d_list]:
            segment_already_full.append(itrsct)

    return full_surface_h, full_terrain_h


def replace_terrain_if_no_hrdem(tx, rx, terrain_h):
    
    # Get heading in order to get elevation in a direction
    direction = get_heading((rx.lat, rx.lon), (tx.lat, tx.lon))

    hrdem_available = True
    if terrain_h[0] == 0:
        hrdem_available = False
        terrain_h = replace_elevation_profile(terrain_h, direction, (tx.lat, tx.lon))

    # If terrain is missing at the Rx
    if terrain_h[-1] == 0:
        hrdem_available = False
        terrain_h = replace_elevation_profile(terrain_h, direction, (rx.lat, rx.lon), inverted=True)
        
    return hrdem_available, terrain_h


def replace_elevation_profile(elevation, direction_LOS, pointA, surface='cdem', inverted = False):
    
    if inverted :
        pointB = pointA
        distance = np.where(elevation == 0)[0][-1] - np.where(elevation == 0)[0][0]
        destinationA = geodesic(kilometers=float(distance/1000)).destination(pointA, direction_LOS)
        pointA = (destinationA.latitude, destinationA.longitude)
    else:
        distance = np.where(elevation == 0)[0][-1] + 1
        destinationB = geodesic(kilometers=float(distance/1000)).destination(pointA, direction_LOS+180)
        pointB = (destinationB.latitude, destinationB.longitude)
    
    # Number of steps to API    
    steps = int(distance/30)

    # print("Accessing Geogratis API for elevation at 30m resolution")
    url_terrain=f"http://geogratis.gc.ca/services/elevation/{surface}/profile?path=LINESTRING({pointA[1]}%20{pointA[0]},%20{pointB[1]}%20{pointB[0]})&steps={steps}"
    request_terrain = requests.get(url_terrain)
    full_terrain = np.zeros(len(elevation))

    if request_terrain.status_code == 200:
        
        terrain_ld = [element['altitude'] if element['altitude'] is not None else 0 for element in request_terrain.json()]
        if terrain_ld:
            xvals = np.linspace(0, len(terrain_ld), distance)
            new_terrain = np.interp(xvals, range(len(terrain_ld)), terrain_ld)

            # When it is only zeros
            if np.array_equal(full_terrain, elevation):
                full_terrain = new_terrain
            elif inverted:
                full_terrain[-distance:] = new_terrain
                full_terrain[:-distance] = elevation[:-distance]
            else:
                full_terrain[:distance] = new_terrain
                full_terrain[distance:] = elevation[distance:]
    else:
        full_terrain = elevation
        
    return full_terrain
