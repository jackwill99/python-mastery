import time
from typing import Tuple

import numpy as np

# SENIOR PRO-TIP: 
# In JS/Dart, you use .map() or for-loops. 
# In ML Engineering, loops are a "Code Smell." 
# We use SIMD (Single Instruction, Multiple Data) via NumPy (C-extensions).

def simulate_particle_motion_slow(n_particles: int) -> np.ndarray:
    """The 'Junior' way: Using loops (Python-level execution)."""
    positions = np.zeros(n_particles)
    velocities = np.random.rand(n_particles)
    dt = 0.01
    for i in range(n_particles):
        positions[i] = velocities[i] * dt
    return positions

def simulate_particle_motion_fast(n_particles: int) -> np.ndarray:
    """The 'Architect' way: Vectorization (C-level execution)."""
    # We treat the entire array as a single mathematical entity (a Vector)
    velocities = np.random.rand(n_particles)
    dt = 0.01
    return velocities * dt  # This happens in optimized C/Fortran memory

def run_benchmark():
    N = 1_000_000
    
    # Timing Slow version
    start = time.perf_counter()
    simulate_particle_motion_slow(N)
    slow_time = time.perf_counter() - start
    
    # Timing Fast version
    start = time.perf_counter()
    simulate_particle_motion_fast(N)
    fast_time = time.perf_counter() - start
    
    print(f"--- Physics Vectorization Benchmark (N={N}) ---")
    print(f"Looping (JS-style): {slow_time:.4f}s")
    print(f"Vectorized (MLE-style): {fast_time:.4f}s")
    print(f"Speedup: {slow_time / fast_time:.1f}x faster")

if __name__ == "__main__":
    run_benchmark()

# REAL-WORLD SCENARIO: 
# When processing sensor data from a Flutter app, never iterate over 
# the readings. Convert them to a NumPy array immediately to utilize 
# CPU cache locality.