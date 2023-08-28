import numpy as np
from propagation.config import MINIMAL_CLUTTER_DEPTH, MINIMAL_CLUTTER_HEIGHT

def get_path_length_below_terrain(terrain_h, tx_height, rx_height):
    
    # Get antenna height above sea level
    tx_height_asl = tx_height + terrain_h[0]
    rx_height_asl = rx_height + terrain_h[-1]
    
    # Get y = alpha * x + b
    alpha = (tx_height_asl - rx_height_asl) / len(terrain_h)

    # Get number of points below terrain - list comprehension
    return len([i for i in range(len(terrain_h)) if terrain_h[i] >= tx_height_asl - alpha * i])

ESA_DICT = {10: 'Tree Cover', 20: "Shrubland", 30: "Grassland", 40: "Cropland", 50: 'Built-up', 60: "Sparse Vegetation", 70: "Snow and Ice", 80: "Water", 90: 'Wetland', 100: "Mangroves", 110: "Moss and Lichen"}

def clutter_path_feature_count(clutter_path):
	
	# Count number of features in clutter path
	return dict((ESA_DICT.get(x, 'unknown'), list(clutter_path).count(x)) for x in set(clutter_path))

def clustering_algorithm(points, eps = 1):
	grouped_points = []
	
	if points:
		curr_point = points[0]
		curr_cluster = [curr_point]
		for point in points[1:]:
			if point <= curr_point + 1:
				curr_cluster.append(point)
			else:
				if len(curr_cluster) >= eps:	
					grouped_points.extend(curr_cluster)
					# print(curr_cluster)
				curr_cluster = [point]
			curr_point = point

		if len(curr_cluster) >= eps:
			grouped_points.extend(curr_cluster)

	return grouped_points

def extrapolate_clutter_path(clutter_path, desired_length):
	num_elements = len(clutter_path)
	repetitions_per_element = desired_length // num_elements
	remaining_positions = desired_length % num_elements

	extrapolated_list = []
	for x in clutter_path:
		repetitions = repetitions_per_element
		if remaining_positions > 0:
			repetitions += 1
			remaining_positions -= 1
		extrapolated_list.extend([x] * repetitions)
  
	return np.array(extrapolated_list)

def get_clutter_features(tx, rx, surface_h, terrain_h, clutter_path):
	
	# Increase resolution of terrain and surface (1 point is 1m)
	# 0.1 meter resolution means 10 points every meter
	resolution = 0.1
	
	# Get antenna height above sea level
	tx_height_asl = tx.height + terrain_h[0]
	rx_height_asl = rx.height + terrain_h[-1]
	
	# Get link_elevation = alpha * x + b
	alpha = (tx_height_asl - rx_height_asl) / len(terrain_h)
	
	# Get angle of incidence (in degrees)
	theta = np.degrees(np.arctan(alpha))

	# Create linear function trom top of tx antenna to rx antenna height every 1m/resolution
	xvals = np.linspace(0, len(terrain_h), int(len(terrain_h)/resolution))
	link_elevation = tx_height_asl - xvals*alpha

	# Interpolate terrain and surface to new resolution
	terrain_h_inter = np.interp(xvals, range(len(terrain_h)), terrain_h)
	surface_h_inter = np.interp(xvals, range(len(surface_h)), surface_h)
	clutter_path_inter = extrapolate_clutter_path(clutter_path, len(terrain_h_inter))
	
	# Get points above terrain but lower than surface and also higher than MINIMAL_CLUTTER_HEIGHT
	intersecting_points = np.where((surface_h_inter >= link_elevation) & (link_elevation >= terrain_h_inter) & (surface_h_inter-terrain_h_inter > MINIMAL_CLUTTER_HEIGHT))[0]

  	# Get first and last intersection point
	first_intersection_point_m = len(terrain_h); last_intersection_point_m = len(terrain_h)
	if len(intersecting_points) != 0 : 
		first_intersection_point_m = round(intersecting_points[0]*resolution, 1)
		last_intersection_point_m = round(len(terrain_h) - intersecting_points[-1]*resolution, 1)

	# Keep only points with minimal clutter depth. If a tree is only 1m long, it will be removed
	index_of_points_with_minimal_depth = clustering_algorithm(list(intersecting_points), int(MINIMAL_CLUTTER_DEPTH/resolution))
	
	# Type of clutter that is intersecting the clutter
	clutter_types_in_between_s_and_t = clutter_path_inter[index_of_points_with_minimal_depth]
	clutter_depth_by_type = clutter_path_feature_count(clutter_types_in_between_s_and_t)
	clutter_depth_by_type = {key: round(value * resolution, 1) for key, value in clutter_depth_by_type.items()}

	# Heights of clutter that is intersecting the clutter
	heights_in_between_s_and_t = surface_h_inter-terrain_h_inter
	heights_in_between_s_and_t = heights_in_between_s_and_t[index_of_points_with_minimal_depth]
	
	# Get total foliage depth
	total_clutter_depth = round(len(heights_in_between_s_and_t)*resolution, 1)
	
 	# Get avg tree height in path by type
	avg_clutter_h_by_type = {ESA_DICT.get(key, 'unknown'): round(np.mean(heights_in_between_s_and_t[clutter_types_in_between_s_and_t == key]), 1) for key in np.unique(clutter_types_in_between_s_and_t)}
	
	# Get avg tree height in path
	avg_clutter_h_in_path = round(np.mean(heights_in_between_s_and_t), 1) if len(heights_in_between_s_and_t) > 0 else 0

	return clutter_depth_by_type, total_clutter_depth, avg_clutter_h_by_type, avg_clutter_h_in_path, first_intersection_point_m, last_intersection_point_m, theta

