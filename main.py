from propagation.tower import Tx, Rx
from safe_metrics import compute_safe_metrics

def main(): 
    
    # declaring Tx and Rx
    index = 0
    tx = Tx(lat = 45.35755587724909, lon = -75.89139665209142, height = 10, band = 3500)
    rx = Rx(lat = 45.3532516568705, lon = -75.84831022990471, height = 10)

    # running single simulation
    print(f"\nRunning simulation\n")
    metrics = compute_safe_metrics(index, tx, rx)
    
    print(f"P1812 path loss no clutter : {metrics.get('p1812_path_loss_no_clutter')} dB")
    print(f"P1812 path loss : {metrics.get('p1812_path_loss')} dB")
    print(f"SAFE path loss: {metrics.get('safe_path_loss')} dB")
    
if __name__ == '__main__':
    
    main()
