import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import pairwise_distances

def run_optimization_phase():
    # 1. THE INPUT: The Symmetrized P Matrix (The "Blueprint")
    # (Simplified values from our previous discussion)
    # A, B, C are SciFi. D is History. E is Poetry.
    P = np.array([
        [0.0, 0.9, 0.6, 0.0, 0.0], # A
        [0.9, 0.0, 0.6, 0.0, 0.0], # B
        [0.6, 0.6, 0.0, 0.1, 0.0], # C
        [0.0, 0.0, 0.1, 0.0, 0.9], # D (Linked to E!)
        [0.0, 0.0, 0.0, 0.9, 0.0]  # E (Linked to D!)
    ])
    names = ['SciFi-A', 'SciFi-B', 'SciFi-C', 'History-D', 'Poetry-E']

    # 2. INITIALIZATION: Random positions in 2D
    np.random.seed(42)
    Y = np.random.rand(5, 2) * 10 # Random box 10x10

    # Hyperparameters
    learning_rate = 1.0
    n_epochs = 50

    # Store history for plotting
    history = [Y.copy()]

    print("Starting Optimization Loop (Push/Pull)...")

    # 3. THE LOOP (Simplified SGD)
    for epoch in range(n_epochs):
        # Calculate current Low-D distances
        dist_matrix = pairwise_distances(Y)
        
        # Calculate Q (Student t-distribution: 1 / (1 + dist^2))
        # We add epsilon to avoid division by zero
        Q = 1 / (1 + dist_matrix**2 + 1e-6)

        # Gradients (Simplified forces)
        # Attraction: Pull if P is high
        # Repulsion: Push if P is low (simulated by repulsive sampling in real UMAP)
        
        # We will calculate a simplified displacement vector for each point
        grad = np.zeros_like(Y)
        
        for i in range(5):
            for j in range(5):
                if i == j: continue
                
                # Direction vector from i to j
                diff = Y[j] - Y[i]
                dist = np.linalg.norm(diff) + 1e-4
                direction = diff / dist
                
                # ATTRACTION (Springs)
                # Strength depends on P[i,j]
                attraction = P[i, j] * direction * dist 
                
                # REPULSION (Magnets)
                # Push away from everyone slightly
                # Real UMAP uses probabilistic sampling for this
                repulsion = -0.1 * direction / (dist**2 + 0.1) 
                
                # Combine
                grad[i] += (attraction + repulsion) * learning_rate

        # Update positions
        Y += grad
        history.append(Y.copy())
        
        # Decay learning rate
        learning_rate *= 0.95

    # 4. VISUALIZATION
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    steps = [0, 10, 49] # Start, Middle, End
    
    for idx, step in enumerate(steps):
        ax = axes[idx]
        current_Y = history[step]
        
        # Plot connections based on P matrix
        for i in range(5):
            for j in range(i+1, 5):
                if P[i, j] > 0.5: # Only draw strong connections
                    ax.plot([current_Y[i,0], current_Y[j,0]], 
                            [current_Y[i,1], current_Y[j,1]], 
                            'k-', alpha=0.2)

        # Plot points
        ax.scatter(current_Y[:3, 0], current_Y[:3, 1], c='blue', s=200, label='SciFi')
        ax.scatter(current_Y[3, 0], current_Y[3, 1], c='green', s=200, label='History')
        ax.scatter(current_Y[4, 0], current_Y[4, 1], c='red', s=200, label='Poetry')
        
        for i, txt in enumerate(names):
            ax.annotate(txt, (current_Y[i,0]+0.2, current_Y[i,1]+0.2))

        ax.set_title(f"Epoch {step}: {'Chaos' if step==0 else 'Converging' if step==10 else 'Final Structure'}")
        ax.grid(True, alpha=0.3)
        if idx == 0: ax.legend()

    plt.tight_layout()
    plt.show()

run_optimization_phase()