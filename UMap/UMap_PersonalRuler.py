import numpy as np
import matplotlib.pyplot as plt

def plot_library_physics():
    # 1. Distances for Book A (The Cluster)
    # Nearest neighbors are at 0.1, 0.2, 2.0
    neighbors_A = np.array([0.1, 0.2, 2.0, 10.0])
    rho_A = 0.1 # Distance to nearest neighbor
    sigma_A = 0.1865 # Calculated roughly to fit log2(3)
    
    # 2. Distances for Book E (The Outlier)
    # Nearest neighbors are at 8.0, 10.0, 10.1
    neighbors_E = np.array([8.0, 10.0, 10.1, 10.2])
    rho_E = 8.0 # Distance to nearest neighbor
    sigma_E = 4.5 # Calculated roughly to fit log2(3)

    # 3. Setup Plot
    x_range = np.linspace(0, 12, 500)
    
    # Calculate UMAP Decay curves: exp(-(x - rho) / sigma)
    # We clip x < rho to 1.0
    curve_A = np.exp(-np.maximum(0, x_range - rho_A) / sigma_A)
    curve_E = np.exp(-np.maximum(0, x_range - rho_E) / sigma_E)

    plt.figure(figsize=(10, 6))
    
    # Plot Book A
    plt.plot(x_range, curve_A, color='blue', linewidth=3, label='Book A (SciFi) - Strict Ruler')
    plt.scatter(neighbors_A, np.exp(-np.maximum(0, neighbors_A - rho_A) / sigma_A), 
                color='blue', s=100, zorder=5)
    plt.text(0.5, 0.5, "Book A drops off fast\n(Only likes close neighbors)", color='blue')

    # Plot Book E
    plt.plot(x_range, curve_E, color='red', linewidth=3, label='Book E (Poetry) - Loose Ruler')
    plt.scatter(neighbors_E, np.exp(-np.maximum(0, neighbors_E - rho_E) / sigma_E), 
                color='red', s=100, zorder=5)
    plt.text(6.5, 0.8, "Book E reaches very far\n(Distance 8.0 is treated as 'Close')", color='red')

    # Formatting
    plt.title("How UMAP Distorts Reality: The 'Adaptive Ruler'")
    plt.xlabel("Physical Distance (Euclidean)")
    plt.ylabel("UMAP Probability (Connection Strength)")
    plt.axvline(x=8.0, color='gray', linestyle='--', alpha=0.5)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.show()

plot_library_physics()