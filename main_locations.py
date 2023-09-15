from propagation.tower import Tx, Rx
from safe_metrics import compute_safe_metrics
import pandas as pd
from os.path import join
from os import rename

def main(): 
    
    data_path = "SAFE-Tool/data/locations"
    df = pd.read_csv(join(data_path, 'locations.txt'))
    
    with open(join(data_path, 'locations_metrics.csv'), mode="a") as w_file:
        w_file.write("IDX;location_1;location2;link_distance;clutter_path_by_type;clutter_depth_by_type;total_clutter_depth;total_terrain_depth;p1812_no_clutter;p1812;safe\n")
        index = 0
        for _, row1 in df.iterrows():
            for _, row2 in df.iterrows():
                if row1['index'] > row2['index']:
                    print(index, row1['index'], row2['index'])
                    w_file.write(f"{index};{row1['index']};{row2['index']};")
                    tx = Tx(row1['lat'], row1['lon'], height = 18, frequency = 3500)
                    rx = Rx(row2['lat'], row2['lon'], height = 18)

                    # running single simulation
                    metrics = compute_safe_metrics(index, tx, rx)
                    metrics = list(metrics.values())
                    for metric in metrics[1:-1]:
                        w_file.write(f"{metric};")
                    w_file.write(f"{metrics[-1]}\n")
                    # rename(join(data_path, 'locations', f"path{index}.png"), join(data_path, 'locations',  f"path_{i+1}_to_{j+1}.png"))
                    index += 1
    
if __name__ == '__main__':
    
    main()
