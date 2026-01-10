import numpy as np
import matplotlib.pyplot as plt

# --- 1. SETUP THE DATA (The "Symmetrized Matrix" P) ---
# We use the values from our specific Library example.
labels = ['A', 'B', 'C', 'D', 'E']

# The Symmetrized Probability Matrix (P)
# (Rows/Cols: A, B, C, D, E)
P = np.array([
    [0.00, 1.00, 0.58, 1.00, 0.33], # A
    [1.00, 0.00, 0.58, 0.41, 0.31], # B
    [0.58, 0.58, 0.00, 0.17, 0.29], # C
    [1.00, 0.41, 0.17, 0.00, 1.00], # D
    [0.33, 0.31, 0.29, 1.00, 0.00]  # E
])

# --- 2. INITIALIZATION (Epoch 0: Spectral Embedding) ---
# We use the coordinates we calculated in the previous step.
# Format: [x, y]
coordinates = np.array([
    [-0.55, -0.20], # A (SciFi Anchor)
    [-0.45,  0.10], # B (SciFi)
    [-0.40,  0.40], # C (SciFi Lightest)
    [ 0.10, -0.50], # D (Bridge)
    [ 0.80,  0.10]  # E (Poetry Outlier)
])

# --- 3. DEFINE THE OPTIMIZATION ENGINE (Mini-UMAP) ---
def compute_low_dim_prob(Y):
    """
    Calculates Q (Low-D Probabilities) based on current distances.
    Formula: Q_ij = 1 / (1 + dist^2)  (Student t-distribution)
    """
    n = Y.shape[0]
    Q = np.zeros((n, n))
    dist_sq_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i != j:
                dist_sq = np.sum((Y[i] - Y[j])**2)
                dist_sq_matrix[i, j] = dist_sq
                Q[i, j] = 1 / (1 + dist_sq)
    return Q, dist_sq_matrix

def run_optimization_step(Y, P, learning_rate=1.0):
    """
    Runs one Epoch of Gradient Descent.
    It calculates the forces: Attraction (P) vs Repulsion (Q).
    """
    n = Y.shape[0]
    Q, dist_sq = compute_low_dim_prob(Y)
    
    # Calculate Gradients (The Push/Pull forces)
    # Simplified Gradient: (P - Q) * phi * (yi - yj)
    # If P > Q (High prob, currently far): Attraction
    # If P < Q (Low prob, currently close): Repulsion
    
    grads = np.zeros_like(Y)
    
    for i in range(n):
        total_grad = np.zeros(2)
        for j in range(n):
            if i != j:
                # The strength of the force
                attraction_repulsion = (P[i, j] - Q[i, j])
                
                # The geometric factor (from the t-dist derivative)
                geometric_factor = 1 / (1 + dist_sq[i, j])
                
                # The direction vector
                direction = Y[i] - Y[j]
                
                # Add to total force on point i
                # Factor of 4 is standard in UMAP gradient derivation
                total_grad += 4.0 * attraction_repulsion * geometric_factor * direction * -1 
        
        grads[i] = total_grad

    # Apply the move
    Y_new = Y + (grads * learning_rate)
    return Y_new

# --- 4. RUN THE SIMULATION AND PLOT ---

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
snapshots = [0, 25, 100] # The epochs we want to capture
current_coords = coordinates.copy()
learning_rate = 0.5

# Plot Helper
def plot_graph(ax, coords, epoch_title):
    ax.set_title(epoch_title, fontsize=14, fontweight='bold')
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.grid(True, linestyle=':', alpha=0.6)
    
    # Draw connections (only strong ones for visual clarity)
    for i in range(len(labels)):
        for j in range(i+1, len(labels)):
            if P[i,j] > 0.5: # Draw lines for strong friends
                ax.plot([coords[i,0], coords[j,0]], [coords[i,1], coords[j,1]], 
                        color='gray', alpha=0.3, zorder=1)

    # Draw Points
    colors = ['#FF6B6B', '#FF6B6B', '#FF6B6B', '#4ECDC4', '#556270']
    ax.scatter(coords[:,0], coords[:,1], s=800, c=colors, edgecolors='black', zorder=2)
    
    # Add Labels
    for idx, label in enumerate(labels):
        ax.text(coords[idx,0], coords[idx,1], label, 
                fontsize=12, fontweight='bold', ha='center', va='center', color='white')

# -- The Loop --
step = 0
for ax_idx, epoch_target in enumerate(snapshots):
    # Run until we hit the target epoch
    while step < epoch_target:
        current_coords = run_optimization_step(current_coords, P, learning_rate)
        # Decay learning rate slightly (Simulated annealing)
        learning_rate *= 0.99 
        step += 1
    
    plot_graph(axes[ax_idx], current_coords, f"Epoch {epoch_target}")

axes[0].set_xlabel("Initialization (Spectral)")
axes[1].set_xlabel("Sorting Phase (Clusters form)")
axes[2].set_xlabel("Final Layout (Stable)")

plt.tight_layout()
plt.show()