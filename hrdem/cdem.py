import numpy as np
import requests

from geopy.distance import geodesic
from propagation.tower import get_heading

def clustering_algorithm(points, eps = 1):
    clusters = []
    if points:
        curr_point = points[0]
        curr_cluster = [curr_point]
        for point in points[1:]:
            if point <= curr_point + eps:
                curr_cluster.append(point)
            else:
                clusters.append(curr_cluster)
                curr_cluster = [point]
            curr_point = point
        clusters.append(curr_cluster)
    
    return clusters


def replace_terrain_if_no_hrdem(tx, rx, surface_h, terrain_h):
    # Get heading in order to get elevation in a direction
    direction = get_heading((tx.lat, tx.lon), (rx.lat, rx.lon))

    hrdem_available = True

    if 0 in terrain_h:
        hrdem_available = False
        points = list(np.where(terrain_h==0)[0])
        groups = clustering_algorithm(points)
        for group in groups : 
            terrain_h = replace_elevation_profile(terrain_h, group, direction, (tx.lat, tx.lon))
    
    surface_h = np.where(surface_h < terrain_h, terrain_h, surface_h)

    return hrdem_available, surface_h, terrain_h


def replace_elevation_profile(full_terrain, group, direction_LOS, tx_point, surface='cdem'):

    destinationA = geodesic(kilometers=float(group[0] / 1000)).destination(tx_point, direction_LOS)
    destinationB = geodesic(kilometers=float(group[-1] / 1000)).destination(tx_point, direction_LOS)
    pointA = (destinationA.latitude, destinationA.longitude)
    pointB = (destinationB.latitude, destinationB.longitude)

    # Number of steps to API
    distance = (group[-1]-group[0])
    steps = int(distance / 30)

    # print("Accessing Geogratis API for elevation at 30m resolution")
    url_terrain = f"http://geogratis.gc.ca/services/elevation/{surface}/profile?path=LINESTRING({pointA[1]}%20{pointA[0]},%20{pointB[1]}%20{pointB[0]})&steps={steps}"
    request_terrain = requests.get(url_terrain)

    if request_terrain.status_code == 200:

        terrain_ld = [element['altitude'] if element['altitude'] is not None else 0 for element in
                      request_terrain.json()]
        if terrain_ld:
            xvals = np.linspace(0, len(terrain_ld), distance+1)
            new_terrain = np.interp(xvals, range(len(terrain_ld)), terrain_ld)
            full_terrain[group[0]:(group[-1]+1)] = new_terrain

    return full_terrain