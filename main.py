from propagation.tower import Tx, Rx
from safe_metrics import compute_safe_metrics

def main(): 
    
    # declaring Tx and Rx
    index = 1
    tx = Tx(45.473870457910564, -75.90535057848327, height = 30, band = 3500)
    rx = Rx(45.49102165209113, -75.90937433346998, height = 3)

    # running single simulation
    print(f"\nRunning simulation\n")
    metrics = compute_safe_metrics(index, tx, rx)
    
    print(f"P1812 path loss no clutter : {metrics.get('p1812_path_loss_no_clutter')} dB")
    print(f"P1812 path loss : {metrics.get('p1812_path_loss')} dB")
    print(f"SAFE path loss: {metrics.get('safe_path_loss')} dB")
    
if __name__ == '__main__':
    
    main()
