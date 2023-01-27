import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio as rio
import ssl

from fiona import listlayers
from http.client import RemoteDisconnected
from os import listdir, remove, makedirs
from os.path import isfile, join, dirname, realpath, isfile
from shapely.geometry import LineString
from time import sleep
from utm import from_latlon
from urllib.error import ContentTooShortError, URLError
from wget import download
from zipfile import ZipFile

ssl._create_default_https_context = ssl._create_unverified_context
pd.options.mode.chained_assignment = None  # default='warn'

# Folders
home = join(dirname(realpath(__file__)), "..", 'data')
out_folder_numpy = join(home, 'numpy')
out_folder_geotiff = join(home, 'geotiffs')
out_folder_fp = join(home, 'footprints')
out_folder_metadata = join(home, 'metadata')


def get_dataset_footprint():
    
    # Download dataset footprint of available regions of HRDEM data in Canada
    if not isfile(join(out_folder_fp, "Datasets_Footprints.shp")):
        
        print("\nDownloading Dataset Footprints\n")
        makedirs(out_folder_fp, exist_ok=True)
        
        # Download dataset footprint of available regions of HRDEM data in Canada
        ftp_fp_link = "https://ftp.maps.canada.ca/pub/elevation/dem_mne/highresolution_hauteresolution/Datasets_Footprints.zip"
        zipped_file = "ftp_fp_link.zip"

        # Unzip file
        download(ftp_fp_link, out=zipped_file)
        with ZipFile(zipped_file, 'r') as zip_ref:
            zip_ref.extractall(out_folder_fp)
        remove(zipped_file)

    # Load dataset smaller dataset for speed purpose
    if not isfile(join(out_folder_fp, "reduced_Datasets_Footprints.shp")):
        df = gpd.read_file(join(out_folder_fp, "Datasets_Footprints.shp"))
        
        # Remove artic and columns that we don't need
        reduced_df = df[df['Provider'] != "arcticdem"]
        reduced_df = reduced_df[['Provider', 'Project', 'Meta_dtm', 'Ftp_dtm', 'Ftp_dsm', 'Coord_Sys', 'Tile_name', 'geometry']]
        
        # Create 2 more columns that will be useful later
        reduced_df["index"] = reduced_df.index
        reduced_df["year"] = None
        reduced_df.to_file(join(out_folder_fp, "reduced_Datasets_Footprints.shp"))
    
    return gpd.read_file(join(out_folder_fp, "reduced_Datasets_Footprints.shp"))


def make_date_available(df, dataset_fp):
    
    # For all the hrdem rows where the year isn't available
    while len(df.loc[df['year'].isna(), 'index'].values) > 0 :
        index = df.loc[df['year'].isna(), 'index'].values[0]
        
        if df[df['index'] == index]['year'].values[0] == None:

            # Download metadata for this hrdem dataset
            makedirs(out_folder_metadata, exist_ok=True)
            metadata_zip = df[df['index'] == index]['Meta_dtm'].values[0]
            zipped_file = join(out_folder_metadata, metadata_zip.split("/")[-1])
            gdb_file = join(out_folder_metadata,  metadata_zip.split("/")[-1].split(".zip")[0])

            if gdb_file.split("/")[-1] not in listdir(out_folder_metadata):
                print(f"\nExtracting year for index : {index}")
                
                download(metadata_zip, out=zipped_file, bar=None)
                
                with ZipFile(zipped_file, 'r') as zip_ref:
                    zip_ref.extractall(gdb_file)
                if isfile(zipped_file): remove(zipped_file)

            # Get all the layers from the metadata (.gdb) file 
            source_layer = [layer for layer in listlayers(gdb_file) if "source" in layer][0]
            gdf = gpd.read_file(gdb_file, layer=source_layer)
            
            # Assign year to the new dataframe
            df.loc[df['Meta_dtm'] == metadata_zip, "year"] = gdf['DATE'].values[0]
            
            # Save dataset with date added
            dataset_fp.loc[dataset_fp['Meta_dtm'] == metadata_zip, 'year'] = gdf['DATE'].values[0]
            dataset_fp.to_file(join(out_folder_fp, "reduced_Datasets_Footprints.shp"))
    
    return df 

def download_file(ftp_link, outfolder, max_retries=4, sleep_time_s=15):
    success = False
    # Try 4 times
    for retry_n in range(max_retries):
        try:
            download(ftp_link, out=outfolder, bar=None)
            success = True
        except (RemoteDisconnected, URLError, ContentTooShortError) as str_error:
            pass

        if not success and retry_n + 1 == max_retries:
            print("Can't connect")
            exit()
        elif not success:
            print(f"Trying again {retry_n+2}/{max_retries} in {sleep_time_s}")
            sleep(sleep_time_s)  # wait for 15 seconds before trying to fetch the data again
        else:
            break   


def make_numpy_files_available(hrdem):
    
    makedirs(out_folder_geotiff, exist_ok=True)
    makedirs(out_folder_numpy, exist_ok=True)
    
    for i, idx in enumerate(hrdem['index']):
        if not isfile(join(out_folder_numpy, f"{idx}.npy")):
            # Download dsm file only if available
            if not isfile(join(out_folder_geotiff, f"dsm_{idx}.tif")):
                    print(f"Downloading DSM {idx}.tif file ({i+1} out of {len(hrdem)})")
                    dsm_file = hrdem.loc[hrdem['index']==idx, 'Ftp_dsm'].values[0]
                    download_file(dsm_file, join(out_folder_geotiff, f"dsm_{idx}.tif"))
                        
            # Download dsm file only if available
            if not isfile(join(out_folder_geotiff, f"dtm_{idx}.tif")):
                    print(f"Downloading DTM {idx}.tif file ({i+1} out of {len(hrdem)})")
                    dtm_file = hrdem.loc[hrdem['index']==idx, 'Ftp_dtm'].values[0]
                    download_file(dtm_file, join(out_folder_geotiff, f"dtm_{idx}.tif"))
                
            # Read geotiff and convert to numpy array for speed purpose
            with rio.open(join(out_folder_geotiff, f"dsm_{idx}.tif")) as dsm_tiff:
                with rio.open(join(out_folder_geotiff, f"dtm_{idx}.tif")) as dtm_tiff:
                    with open(join(out_folder_numpy, f"{idx}.npy"), 'wb') as npy_file:
                        np.save(npy_file, np.array(dsm_tiff.read(1)))
                        np.save(npy_file, np.array(dtm_tiff.read(1)))
                        np.save(npy_file, np.array(dsm_tiff.bounds))
        

            # If file exists after download, delete it
            if isfile(join(out_folder_geotiff, f"dsm_{idx}.tif")): remove(join(out_folder_geotiff, f"dsm_{idx}.tif"))      
            if isfile(join(out_folder_geotiff, f"dtm_{idx}.tif")): remove(join(out_folder_geotiff, f"dtm_{idx}.tif"))   
            

def get_dtm_dsm_index_along_path(hrdem_fp, lat_lon, tower_lat_lon):
    
    # Get coordinate system
    utm_number = from_latlon(lat_lon[0], lat_lon[1])[2]
    coord_sys = f"utm{utm_number}"
    
    # Get intersection between line and all hrdem footprints
    shapely_line = LineString([(lat_lon[1], lat_lon[0]), (tower_lat_lon[1], tower_lat_lon[0])])
    intersection_poly = hrdem_fp[(hrdem_fp['geometry'].intersects(shapely_line)) &
                                   (hrdem_fp["Coord_Sys"] == coord_sys) &
                                   (hrdem_fp['Tile_name'].str.contains("1m_"))]
    
    # Get 2m resolution
    if intersection_poly.empty:
        intersection_poly = hrdem_fp[(hrdem_fp['geometry'].intersects(shapely_line)) &
                                    (hrdem_fp["Coord_Sys"] == coord_sys)]
    
    # If still empty
    if intersection_poly.empty:
        # print("No shapefile was found for this point")
        return [], utm_number
    else:
        # Make sure the numpy format is available, if not download/convert it
        make_numpy_files_available(intersection_poly)
        intersection_poly = make_date_available(intersection_poly, hrdem_fp)
        
        # Sort by distance to tower and year
        intersection_poly['intersection_line'] = intersection_poly[['geometry']].intersection(shapely_line)
        intersection_poly = intersection_poly.loc[intersection_poly.intersection_line.geometry.type=='LineString']
        intersection_poly['year'] = pd.to_datetime(intersection_poly['year'])
        intersection_poly.sort_values(["year"], ascending=[False], inplace=True)
        
        return intersection_poly[['index', 'intersection_line']], utm_number
