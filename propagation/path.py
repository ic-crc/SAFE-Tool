import numpy as np

def get_path_length_below_terrain(terrain_h, tx_height, rx_height):
    
    # Get antenna height above sea level
    tx_height_asl = tx_height + terrain_h[0]
    rx_height_asl = rx_height + terrain_h[-1]
    
    # Get y = alpha * x + b
    alpha = (tx_height_asl - rx_height_asl) / len(terrain_h)

    # Get number of points below terrain - list comprehension
    return len([i for i in range(len(terrain_h)) if terrain_h[i] >= tx_height_asl - alpha * i])


def get_total_foliage_depth(tx, rx, terrain_h, surface_h):
    
    # Increase resolution of terrain and surface (1 point is 0.1m)
    resolution = 10
    
    # Get antenna height above sea level
    tx_height_asl = tx.height + terrain_h[0]
    rx_height_asl = rx.height + terrain_h[-1]
    
    # Get link_elevation = alpha * x + b
    alpha = (tx_height_asl - rx_height_asl) / len(terrain_h)
    
    # Get angle of incidence (in degrees)
    theta = np.degrees(np.arctan(alpha))

    # Create linear function trom top of tx antenna to rx antenna height every 1m/resolution
    xvals = np.linspace(0, len(terrain_h), len(terrain_h)*resolution)
    link_elevation = tx_height_asl - xvals*alpha

    # Interpolate terrain and surface to new resolution
    terrain_h_inter = np.interp(xvals, range(len(terrain_h)), terrain_h)
    surface_h_inter = np.interp(xvals, range(len(surface_h)), surface_h)
    
    # Get points above terrain but lower than surface
    points_in_between_s_and_t = np.where((surface_h_inter >= link_elevation) & (link_elevation >= terrain_h_inter), surface_h_inter-terrain_h_inter, 0)
    points_in_between_s_and_t = points_in_between_s_and_t[points_in_between_s_and_t > 0]
    
    # Get total foliage depth
    total_foliage_depth = len(points_in_between_s_and_t)/resolution
    
    # Get avg tree height in path
    avg_tree_h_in_path = np.mean(points_in_between_s_and_t)

    return total_foliage_depth, avg_tree_h_in_path, theta