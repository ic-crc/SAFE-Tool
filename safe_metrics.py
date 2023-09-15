from os.path import join, dirname, realpath
from os import makedirs

from hrdem.elevation import return_elevation_profile, return_land_cover_profile
from hrdem.cdem import replace_terrain_if_no_hrdem
from plot import plot_tx_to_rx_path
from propagation.path import get_path_length_below_terrain, clutter_path_feature_count, get_clutter_features
from propagation.pathloss  import get_SAFE_path_loss, compute_p1812
from propagation.tower import get_distance_to_tower

def compute_safe_metrics(index, tx, rx):
	
	# Get distance path between tx and rx
	print("Extracting 2D elevation profile")
	distance_to_tower = get_distance_to_tower((rx.lat, rx.lon), (tx.lat, tx.lon))
	if distance_to_tower < 1: return None # If distance is less than 1 meter, return None
	
 	# Get path profile from HRDEM dataset
	surface_height, terrain_height = return_elevation_profile((rx.lat, rx.lon), (tx.lat, tx.lon), distance_to_tower)

	# Get land cover profile from ESA dataset
	clutter_path = return_land_cover_profile((rx.lat, rx.lon), (tx.lat, tx.lon), distance_to_tower)
	
	# Replace terrain if HRDEM is not available
	hrdem_available, surface_height, terrain_height = replace_terrain_if_no_hrdem(tx, rx, surface_height, terrain_height)
		
	# Extract clutter features
	print("Extracting features & metrics")
	clutter_path_by_type = clutter_path_feature_count(clutter_path)
	clutter_depth_by_type, total_clutter_depth, avg_clutter_h_by_type, avg_clutter_h_in_path, first_intersection_point_m, last_intersection_point_m, theta = \
	 get_clutter_features(tx, rx, surface_height, terrain_height, clutter_path)

	# Get path length below terrain (m)
	total_terrain_depth = get_path_length_below_terrain(terrain_height, tx.height, rx.height)
 
	# Compute p1812 with and without clutter (dB)
	p1812_no_clutter = compute_p1812(tx, rx, terrain_height, terrain_height, distance_to_tower)
	p1812_path_loss = compute_p1812(tx, rx, surface_height, terrain_height, distance_to_tower, clutter_type=4) if hrdem_available else p1812_no_clutter

	# compute other loss and total path loss
	tree_loss, top_diffraction, ret_plus_top, safe_path_loss = \
	 get_SAFE_path_loss(tx, rx, p1812_no_clutter, total_clutter_depth, avg_clutter_h_in_path, theta) if hrdem_available else (0, 0, 0, p1812_no_clutter)
	
	# Plot and save path profile
	# print("Plotting path profile\n")
	# save_folder = join(dirname(realpath(__file__)), "data")
	# makedirs(save_folder, exist_ok=True)
	# plot_tx_to_rx_path(surface_height, terrain_height, clutter_path, tx.height, rx.height, save_folder, index)
	
	return {
		"index": index,
		"link_distance": distance_to_tower,
		'clutter_path_by_type': clutter_path_by_type,
		"clutter_depth_by_type": clutter_depth_by_type,
		"total_clutter_depth": total_clutter_depth,
		"total_terrain_depth": round(total_terrain_depth, 2),
		"p1812_path_loss_no_clutter": round(p1812_no_clutter, 2),
		"p1812_path_loss": round(p1812_path_loss, 2),
		"safe_path_loss": round(safe_path_loss, 2)
	}
