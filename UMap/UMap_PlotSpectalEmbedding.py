import matplotlib.pyplot as plt
import networkx as nx

# 1. Define the Positions (From the Spectral Embedding Calculation)
# Notice the clear Left-to-Right structure
pos = {
    'A': (-0.55, -0.20), # Sci-Fi Anchor
    'B': (-0.45,  0.10), # Sci-Fi
    'C': (-0.40,  0.40), # Sci-Fi
    'D': ( 0.10, -0.50), # History (The Bridge)
    'E': ( 0.80,  0.10)  # Poetry (The Loner)
}

# 2. Define the Graph Connections (The Springs)
# These are the relationships with high values in your Symmetrized Matrix
edges = [
    ('A', 'B'), ('A', 'C'), ('B', 'C'), # The tight Sci-Fi Cluster
    ('A', 'D'),                         # The Bridge (D holding A's hand)
    ('D', 'E')                          # The Long Reach (E holding D's hand)
]

# 3. Create the Plot
plt.figure(figsize=(10, 6))

# Draw Edges (The Springs)
for edge in edges:
    p1 = pos[edge[0]]
    p2 = pos[edge[1]]
    plt.plot([p1[0], p2[0]], [p1[1], p2[1]], color='gray', linestyle='--', alpha=0.5, zorder=1)

# Draw Nodes (The Books)
x_vals = [coord[0] for coord in pos.values()]
y_vals = [coord[1] for coord in pos.values()]
labels = list(pos.keys())

# Color coding clusters
colors = ['#FF6B6B', '#FF6B6B', '#FF6B6B', '#4ECDC4', '#556270'] # Red (SciFi), Teal (History), Blue (Poetry)

plt.scatter(x_vals, y_vals, s=1000, c=colors, edgecolors='black', zorder=2)

# Add Labels inside the circles
for label, (x, y) in pos.items():
    plt.text(x, y, label, fontsize=14, fontweight='bold', ha='center', va='center', color='white')

# Annotate the Global Structure
plt.text(-0.5, 0.6, "The 'Sci-Fi' Cluster\n(Left Side)", ha='center', fontsize=12, fontweight='bold', color='#D9534F')
plt.text(0.1, -0.7, "The 'Bridge'\n(Middle)", ha='center', fontsize=12, fontweight='bold', color='#4ECDC4')
plt.text(0.8, 0.3, "The 'Poetry' Outlier\n(Right Side)", ha='center', fontsize=12, fontweight='bold', color='#556270')

# Formatting
plt.title("Step 3: Spectral Initialization (Unfolding the Graph)", fontsize=16)
plt.xlabel("Eigenvector 2 (X-Axis)")
plt.ylabel("Eigenvector 3 (Y-Axis)")
plt.grid(True, linestyle=':', alpha=0.6)
plt.xlim(-1.0, 1.2)
plt.ylim(-1.0, 1.0)

plt.tight_layout()
plt.show()