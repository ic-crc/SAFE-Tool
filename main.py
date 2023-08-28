from propagation.tower import Tx, Rx
from safe_metrics import compute_safe_metrics

def main(): 
    
    # declaring Tx and Rx
    index = 0
    tx = Tx(45.473870457910564, -75.90535057848327, height = 30, frequency = 3500)
    rx = Rx(45.209584832872444, -76.28604664049735, height = 5)

    # running single simulation
    print(f"\nRunning simulation\n")
    metrics = compute_safe_metrics(index, tx, rx)

    if metrics:
        print("**Metrics**")
        print(f"Clutter Path by Type : {metrics.get('clutter_path_by_type')} meters")
        print(f"Clutter Depth by Type : {metrics.get('clutter_depth_by_type')} meters")
        print(f"Total Clutter Depth : {metrics.get('total_clutter_depth')} meters")
        print(f"Link Distance : {metrics.get('link_distance')} meters")
        print(f"P1812 path loss : {metrics.get('p1812_path_loss')} dB")
        print(f"SAFE path loss: {metrics.get('safe_path_loss')} dB")
    
if __name__ == '__main__':
    
    main()