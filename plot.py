from os.path import join, normpath, basename
from scipy.ndimage import gaussian_filter1d
import matplotlib.pyplot as plt

def plot_tx_to_rx_path(surface_h, terrain_h, tx_height, rx_height, save_folder):
    
    fig, ax = plt.subplots(figsize=(15,5))
    odu_pos = len(surface_h)
    
    index = basename(normpath(save_folder))
    ax.set_title(f"2D elevation profile - Index {index}")
    
    # Set background and scale
    ax.set_facecolor('skyblue')
    ax.set_xlabel("Axes are not equally scaled",  style='italic', loc='right')
    
    # Add path
    ax.plot([0, odu_pos], [tx_height + terrain_h[0], rx_height + terrain_h[-1]], 'r-')

    # Add tower
    ax.plot([0, 0], [tx_height + terrain_h[0], terrain_h[0]], 'navy', linewidth=4)

    # Add surface
    coords = [[idx,h] for idx, h in enumerate(surface_h)]
    xs, ys = zip(*coords)
    sigma = 1
    xs = list(xs); ys = list(gaussian_filter1d(ys, sigma))
    xs = list(xs); ys = list(ys)
    xs.append(odu_pos); ys.append(min(terrain_h)-3)
    xs.append(0); ys.append(min(terrain_h)-3)
    xs.append(xs[0]); ys.append(ys[0])
    ax.fill(xs, ys, 'g-') 
    
    # Add terrain
    coords = [[idx,h] for idx, h in enumerate(terrain_h)]
    coords.append([odu_pos, min(terrain_h)-3])
    coords.append([0, min(terrain_h)-3])
    coords.append(coords[0])
    xs, ys = zip(*coords) #create lists of x and y values
    ax.fill(xs, ys, 'saddlebrown') 

    # Add rx
    ax.plot([odu_pos, odu_pos], [terrain_h[-1], rx_height + terrain_h[-1]], 'orange', linewidth=4)
    
    fig.tight_layout()
    fig.savefig(join(save_folder, 'path.png'))
    plt.close(fig)
