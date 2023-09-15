import numpy as np

from propagation.ret_model import ret_model_computation
from propagation.p1812.tl_p1812SAFE import tl_p1812SAFE
from propagation.p1812.great_circle_path import great_circle_path
from propagation.p1812.InterpolateDN50andN050CTR import InterpolateDN50andN050CTR
from propagation.top_diffraction import topDiffraction

from propagation.config import RET_DB_LIMIT, ZONE_COASTAL, ZONE_INLAND, CLUTTER_VALUES, TIME_PERCENTAGE_P1812, LOCATION_PERCENTAGE_P1812

def compute_p1812(tx, rx, surface_h, terrain_h, distance_to_tower, clutter_type=3):

    # P.1812 input requires a terrain and surface resolution of 30m
    xnew = np.arange(0, distance_to_tower, 30) if distance_to_tower > 250 else np.arange(0, distance_to_tower, 5)
    
    # Requires km
    d = xnew / 1000
    
    # Resampling terrain and surface heights from 1m to 30m resolution
    terrain_h = np.interp(xnew, np.linspace(0, distance_to_tower, len(terrain_h)), terrain_h)
    surface_h = np.interp(xnew, np.linspace(0, distance_to_tower, len(surface_h)), surface_h)

    # Representative clutter height
    R = np.where(surface_h - terrain_h > 1, CLUTTER_VALUES[clutter_type], 0)
    R[0] = 0; R[-1] = 0 # First and last point has to be zeros
    
    # Clutter type
    Ct = np.where(R == CLUTTER_VALUES[clutter_type], clutter_type, 2)

    zone = (np.ones(len(d)) * ZONE_INLAND).astype(int)
    
    try:
        p1812 = get_p1812_output(d, terrain_h, R, Ct, zone, tx, rx)
    except ValueError:
        p1812 = 0
    
    return p1812


def get_p1812_output(d, h, R, Ct, zone, tx, rx):

    freq = float(tx.frequency/1000) # Frequency in GHz
    dpnt = 0.5 * (d[-1] - d[0])
    
    Phipnte, Phipntn, _, _ = great_circle_path(rx.lon, tx.lon, rx.lat, tx.lat, 6371, dpnt)

    DN50PCR, N050PCR = InterpolateDN50andN050CTR(Phipntn,(Phipnte + 360))

    # flag4 should be set to 0. No need to set it here (done in tl_p1812).
    Lb = tl_p1812SAFE(freq, TIME_PERCENTAGE_P1812, d, h, R, Ct, zone, tx.height, rx.height, 2, tx.lat, rx.lat, tx.lon, rx.lon, LOCATION_PERCENTAGE_P1812, 0, DN50PCR, N050PCR); # New format for P.1812-6.

    return round(Lb, 6)


def get_SAFE_path_loss(tx, rx, p1812_path_loss_no_clutter, foliage_depth, avg_tree_h, theta):
    
    # Ret model
    tree_loss = ret_model_computation(foliage_depth, theta, tx.frequency, rx.beamwidth)[0][0] if foliage_depth > 0 else 0
    
    # Top diffraction model
    top_diffraction = topDiffraction(tx.frequency/1000, theta, avg_tree_h, foliage_depth, rx.height) if foliage_depth > 0 else 0
    
    # Linear sum of the RET and Top Diffraction model
    ret_plus_top = -10 * np.log10(sum([pow(10, top_diffraction/10), pow(10, -tree_loss/10)]))

    # Total Path Loss (dB)
    safe_path_loss = p1812_path_loss_no_clutter + min(tree_loss, RET_DB_LIMIT)

    return tree_loss, top_diffraction, ret_plus_top, safe_path_loss
