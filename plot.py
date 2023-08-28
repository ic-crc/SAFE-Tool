from os.path import join
import matplotlib.pyplot as plt

land_cover_colors = {0: "#000000", 10: "#006400", 20: "#ffbb22", 30: "#ffff4c", 40: "#f096ff", 50: "#fa0000", 60: "#b4b4b4", 70: "#f0f0f0", 80: "#0064c8", 90: "#0096a0", 95: "#00cf75", 100: "#fae6a0"}

def plot_tx_to_rx_path(surface_height, terrain_height, clutter_path, tx_height, rx_height, save_folder, index, high_resolution_plot=False):

    fig, ax = plt.subplots(figsize=(15,5))
    ax.set_title(f"2D elevation profile - Index {index}")

    # Set background and scale
    ax.set_facecolor('skyblue')
    ax.set_xlabel("Axes are not equally scaled",  style='italic', loc='right')

    # Add Transmitter and Receiver
    odu_pos = len(surface_height)
    ax.plot([0, 0], [tx_height + terrain_height[0], terrain_height[0]], 'navy', linewidth=4)
    ax.plot([odu_pos, odu_pos], [terrain_height[-1], rx_height + terrain_height[-1]], 'orange', linewidth=4)
    
    # Add signal radio path
    ax.plot([0, odu_pos], [tx_height + terrain_height[0], rx_height + terrain_height[-1]], 'r-')
    
    width = 0
    step = 10 if high_resolution_plot else 1
    
    # Add surface
    for clutter, h in zip(clutter_path, surface_height):
        if width % step == 0:
            coords = [[width, h]]
            coords.append([width, min(terrain_height)-3])
            coords.append([width+step, min(terrain_height)-3])
            coords.append([width+step, h])
            coords.append(coords[0])
            xs, ys = zip(*coords)
            ax.fill(xs, ys, land_cover_colors.get(clutter, "skyblue"))
        width += 1

    # Add terrain
    coords = [[idx,h] for idx, h in enumerate(terrain_height)]
    coords.append([odu_pos, min(terrain_height)-3])
    coords.append([0, min(terrain_height)-3])
    coords.append(coords[0])
    xs, ys = zip(*coords) #create lists of x and y values
    ax.fill(xs, ys, 'saddlebrown')

    fig.tight_layout()
    fig.savefig(join(save_folder, f'path{index}.png'))
