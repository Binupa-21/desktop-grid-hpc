import time
import math

def heavy_computation():
    print("Starting CPU mathematical stress test...")
    start = time.time()
    # Perform 20 million mathematical square root operations
    total = sum(math.sqrt(i) for i in range(20000000))
    elapsed = time.time() - start
    print(f"Elapsed Time: {elapsed:.4f} seconds (Check value: {total:.2f})")

if __name__ == "__main__":
    heavy_computation()