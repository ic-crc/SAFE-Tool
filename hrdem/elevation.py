import numpy as np
import pyproj
import rasterio as rio

from hrdem.hrdem_esa import get_hrdem_along_path, get_esa_along_path

def compute_tx_rx_path(lat_lon, tower_latlon, distance_to_tower):
    # Linearly interpolate the path between the tower and receiver at 1m intervals
    path_coords = (np.linspace(tower_latlon[0], lat_lon[0], distance_to_tower), np.linspace(tower_latlon[1], lat_lon[1], distance_to_tower))

    return path_coords


def return_elevation_profile(lat_lon, tower_latlon, distance_to_tower):

    # Get the HRDEM tiles that intersect the path
    hrdem_intersection_line = get_hrdem_along_path(lat_lon, tower_latlon)

    # Return if no HRDEM tiles are available
    if len(hrdem_intersection_line) == 0:
        return np.zeros(distance_to_tower), np.zeros(distance_to_tower)

    # Initialize HRDEM surface and terrain height arrays
    full_surface_h = np.zeros(distance_to_tower)
    full_terrain_h = np.zeros(distance_to_tower)
    segment_already_full = []

    # Get the interpolated lat lon coordinates along the path from the tower to the receiver
    tx_rx_path_lat_lon = compute_tx_rx_path(lat_lon, tower_latlon, distance_to_tower)

    # Loop through tiles that intersect the path (multiple HRDEM could be on top of each other (newest tiles sorted first))
    for project_id, itrsct in hrdem_intersection_line.values:

        # If more recent HRDEM points already have been added
        if itrsct in segment_already_full: continue

        dsm_s3_path = f"s3://datacube-prod-data-public/store/elevation/hrdem/hrdem-lidar/{project_id}-dsm.tif"
        dtm_s3_path = f"s3://datacube-prod-data-public/store/elevation/hrdem/hrdem-lidar/{project_id}-dtm.tif"

        with rio.open(dsm_s3_path) as dsm_tif:
            with rio.open(dtm_s3_path) as dtm_tif:

                # Get the bounds and CRS of the DSM file
                bounds = dsm_tif.bounds

                # CRS for WGS84 (lat lon coordinate system)
                src_crs = pyproj.CRS.from_epsg(4326)

                # CRS for current HRDEM tile
                dst_crs = pyproj.CRS.from_wkt(dsm_tif.crs.wkt)

                # Define the transformer to convert from the source CRS to the tile's CRS
                transformer = pyproj.Transformer.from_crs(src_crs, dst_crs)

                # Transform the lat lon coordinates to the HRDEM tile's CRS
                x_coords, y_coords = transformer.transform(tx_rx_path_lat_lon[0], tx_rx_path_lat_lon[1])

                # Extract indices that fall within the tile
                tx_rx_path_indices = np.where((x_coords >= bounds[0]) & (x_coords <= bounds[2]) & (y_coords >= bounds[1]) & (
                        y_coords <= bounds[3]))[0]

                # Get the row and column DTM and DSM file indices for the indices on the path that fall within the tile
                row_indices, col_indices = dsm_tif.index(x_coords[tx_rx_path_indices], y_coords[tx_rx_path_indices])

                if len(tx_rx_path_indices) == 0:
                    continue

                step = 1000

                # Read the window from the DSM and DTM files in chunks (speeds up the download process)
                for i in range(0, len(tx_rx_path_indices), step):
                    # Get the indices and file coordinates for the chunk
                    tx_rx_path_chunk_indices = tx_rx_path_indices[i:i + step] if i + step < len(tx_rx_path_indices) else tx_rx_path_indices[i:]
                    chunk_row_indices = row_indices[i:i + step] if i + step < len(tx_rx_path_indices) else row_indices[i:]
                    chunk_col_indices = col_indices[i:i + step] if i + step < len(tx_rx_path_indices) else col_indices[i:]

                    # Get the min and max file indices to download for the chunk
                    min_col_index = min(chunk_col_indices)
                    max_col_index = max(chunk_col_indices)
                    min_row_index = min(chunk_row_indices)
                    max_row_index = max(chunk_row_indices)

                    # Download the chunk of the DSM and DTM files
                    dsm_array = dsm_tif.read(1, window=(
                    (min_row_index, max_row_index + 1), (min_col_index, max_col_index + 1)))

                    dtm_array = dtm_tif.read(1, window=(
                    (min_row_index, max_row_index + 1), (min_col_index, max_col_index + 1)))

                    # Replace negative elevation values
                    dsm_array[dsm_array < 0] = 0
                    dtm_array[dtm_array < 0] = 0

                    # Adjust the row and col indices to match the index of the downloaded chunk's array
                    chunk_row_indices = [row - min_row_index for row in chunk_row_indices]
                    chunk_col_indices = [col - min_col_index for col in chunk_col_indices]

                    # Replace empty (represented as 0) values with the new DSM and DTM values
                    full_surface_h[tx_rx_path_chunk_indices] = np.where(full_surface_h[tx_rx_path_chunk_indices] == 0,
                                                           dsm_array[(chunk_row_indices, chunk_col_indices)],
                                                           full_surface_h[tx_rx_path_chunk_indices])

                    full_terrain_h[tx_rx_path_chunk_indices] = np.where(full_terrain_h[tx_rx_path_chunk_indices] == 0,
                                                           dtm_array[(chunk_row_indices, chunk_col_indices)],
                                                           full_terrain_h[tx_rx_path_chunk_indices])


            # If surface already completed for that segment, break out of that segment (speeds up the process)
            if 0 not in full_surface_h[tx_rx_path_indices]:
                segment_already_full.append(itrsct)

    return full_surface_h, full_terrain_h


def return_land_cover_profile(lat_lon, tower_latlon, distance_to_tower):

    # Get the interpolated lat lon coordinates along the path from the tower to the receiver
    tx_rx_path_lat_lon = compute_tx_rx_path(lat_lon, tower_latlon, distance_to_tower)

    # Initialize ESA profile array
    dlu_profile = np.zeros(distance_to_tower)

    # Get the ESA tiles that intersect the path from the tower to the receiver
    esa_intersection_line = get_esa_along_path(lat_lon, tower_latlon)

    # Loop through the ESA tiles that intersect the path
    for tile in esa_intersection_line:
        # Get the ESA tile's S3 path
        esa_tile_s3_path = f"s3://esa-worldcover/v200/2021/map/ESA_WorldCover_10m_2021_v200_{tile}_Map.tif"

        with rio.open(esa_tile_s3_path) as esa_tif:

            bounds = esa_tif.bounds

            # Extract indices that fall within the tile
            tx_rx_path_indices = np.where((tx_rx_path_lat_lon[1] >= bounds[0]) & (tx_rx_path_lat_lon[1] <= bounds[2]) & (tx_rx_path_lat_lon[0] >= bounds[1]) & (
                    tx_rx_path_lat_lon[0] <= bounds[3]))[0]

            # Get the row and column ESA file indices for the indices that fall within the tile
            row_indices, col_indices = esa_tif.index(tx_rx_path_lat_lon[1][tx_rx_path_indices], tx_rx_path_lat_lon[0][tx_rx_path_indices])

            if len(tx_rx_path_indices) == 0:
                continue

            # Get the min and max ESA file indices to download for the ESA tile
            min_col_index = min(col_indices)
            max_col_index = max(col_indices)
            min_row_index = min(row_indices)
            max_row_index = max(row_indices)

            # Download the ESA tile within the specified bounds
            esa_tile_array = esa_tif.read(1, window=((min_row_index, max_row_index + 1), (min_col_index, max_col_index + 1)))

            # Adjust the row and col indices to match the index of the downloaded tile array
            row_indices = [row - min_row_index for row in row_indices]
            col_indices = [col - min_col_index for col in col_indices]

            # Set the dlu profile values to the corresponding ESA tile values
            dlu_profile[tx_rx_path_indices] = esa_tile_array[(row_indices, col_indices)]

    return dlu_profile
