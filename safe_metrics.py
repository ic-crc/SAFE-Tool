from os.path import join, dirname, realpath
from os import makedirs

from hrdem.elevation import return_elevation_profile, replace_terrain_if_no_hrdem
from plot import plot_tx_to_rx_path
from propagation.path import get_path_length_below_terrain, get_total_foliage_depth
from propagation.pathloss  import get_SAFE_path_loss, compute_p1812
from propagation.tower import get_distance_to_tower

def compute_safe_metrics(index, tx, rx):

    # Get distance path between tx and rx
    distance_to_tower = get_distance_to_tower((rx.lat, rx.lon), (tx.lat, tx.lon))
    
    # Get path profile from HRDEM dataset
    surface_h, terrain_h = return_elevation_profile((rx.lat, rx.lon), (tx.lat, tx.lon), distance_to_tower)
    
    # Replace terrain if HRDEM is not available
    hrdem_available, terrain_h = replace_terrain_if_no_hrdem(tx, rx, terrain_h)
        
    # Get path length below terrain (m)
    terrain_blockage = get_path_length_below_terrain(terrain_h, tx.height, rx.height)

    # Get foliage depth (m) and average tree height (m) in path
    total_foliage_depth, avg_tree_h_in_path, theta = get_total_foliage_depth(tx, rx, terrain_h, surface_h) if hrdem_available else (0, 0, 0)

    # Compute p1812 with and without clutter (dB)
    p1812_no_clutter = compute_p1812(tx, rx, terrain_h, terrain_h, distance_to_tower)
    p1812_path_loss = compute_p1812(tx, rx, surface_h, terrain_h, distance_to_tower, clutter_type=4) if hrdem_available else 0

    # compute other loss and total path loss
    tree_loss, top_diffraction, ret_plus_top, safe_path_loss = get_SAFE_path_loss(tx, rx, p1812_no_clutter, total_foliage_depth, avg_tree_h_in_path, theta) if hrdem_available else (0, 0, 0, p1812_no_clutter)
    
    # Plot plot_tx_to_rx_path
    # Create output folder
    save_folder = join(dirname(realpath(__file__)), "data", 'SAFE', f"{index}")
    makedirs(save_folder, exist_ok=True)
    plot_tx_to_rx_path(surface_h, terrain_h, tx.height, rx.height, save_folder)
    
    # return metrics
    return {
        "index": index,
        "hrdem_available" : hrdem_available,
        "link_distance": distance_to_tower,
        "tree_loss_ret": round(tree_loss, 2) if tree_loss > 0 else 0,
        "top_diffraction_loss": round(top_diffraction, 2),
        "ret_plus_top": round(ret_plus_top, 2),
        "avg_tree_h_in_path" : round(avg_tree_h_in_path, 2), 
        "total_foliage_depth": round(total_foliage_depth, 2),
        "terrain_blockage": round(terrain_blockage, 2), 
        "p1812_path_loss_no_clutter": round(p1812_no_clutter, 2), 
        "p1812_path_loss": round(p1812_path_loss, 2), 
        "safe_path_loss": round(safe_path_loss, 2), 
    }
