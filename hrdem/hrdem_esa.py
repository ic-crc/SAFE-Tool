import geopandas as gpd
import pandas as pd
import ssl

from os import environ
from pystac_client import Client
from shapely.geometry import LineString, shape

environ['AWS_NO_SIGN_REQUEST'] = 'YES'
environ['AWS_REGION'] = 'ca-central-1'

ssl._create_default_https_context = ssl._create_unverified_context
pd.options.mode.chained_assignment = None  # default='warn'

def get_hrdem_along_path(lat_lon, tower_lat_lon):

    # Perform spatial search against the STAC API
    collections = ['hrdem-lidar']
    stac_api_url = "https://datacube.services.geo.ca/api/"

    client = Client.open(stac_api_url)

    # Get intersection between line and all hrdem footprints
    shapely_line = LineString([(lat_lon[1], lat_lon[0]), (tower_lat_lon[1], tower_lat_lon[0])])

    results = client.search(
        collections=collections,
        intersects=shapely_line
    )

    intersection_poly = gpd.GeoDataFrame(columns=['project_name', 'date', 'geometry'])
    
    # Get DTM/DSM asset links from STAC results
    for i, item in enumerate(results.items()):

        # Append the new row to the DataFrame using append()
        intersection_poly.loc[i] = [item.id, item.datetime, shape(item.geometry)]

    # If still empty
    if intersection_poly.empty:
        return []
    else:

        # Sort by distance to tower and year
        intersection_poly['intersection_line'] = intersection_poly[['geometry']].intersection(shapely_line)
        intersection_poly['date'] = pd.to_datetime(intersection_poly['date'])
        intersection_poly['resolution'] = intersection_poly['project_name'].str[-2].astype(int)
        intersection_poly.sort_values(["resolution", "date"], ascending=[True, False], inplace=True, ignore_index=True)
        return intersection_poly[['project_name', 'intersection_line']]


def get_esa_along_path(lat_lon, tower_lat_lon):

    catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")

    shapely_line = LineString([(lat_lon[1], lat_lon[0]), (tower_lat_lon[1], tower_lat_lon[0])])

    search = catalog.search(
        collections=["esa-worldcover"],
        intersects=shapely_line,
    )

    return [str(item).split("_")[-1].split(">")[0] for item in list(search.items()) if "2021" in str(item)]
