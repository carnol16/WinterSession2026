import numpy as np
import matplotlib.pyplot as plt

# --- PART 1: CALCULATION (Same as before) ---

# 1. Input Data [cite: 3]
data = np.array([
    [4, 2],   # Student A
    [6, 4],   # Student B
    [8, 8],   # Student C
    [10, 10]  # Student D
])

# 2. Standardize [cite: 5]
means = np.mean(data, axis=0) # [7, 6] [cite: 7, 9]
centered_data = data - means  # Subtract mean to center at 0,0 

# 3. Covariance Matrix [cite: 13]
# rowvar=False means rows are samples, ddof=1 for sample variance (divide by N-1)
cov_matrix = np.cov(centered_data, rowvar=False, ddof=1)

# 4. Eigenvalues and Eigenvectors [cite: 24]
eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)

# Sort to find the main trend (PC1)
sorted_indices = np.argsort(eigenvalues)[::-1]
sorted_eigenvalues = eigenvalues[sorted_indices]
sorted_eigenvectors = eigenvectors[:, sorted_indices]

pc1_value = sorted_eigenvalues[0]   # ~19.91 [cite: 33]
pc1_vector = sorted_eigenvectors[:, 0] # Normalized vector ~[0.58, 0.82] [cite: 51]

# 5. Projection [cite: 55]
# Dot product projects the data onto the PC1 line
projected_data = np.dot(centered_data, pc1_vector)


# PART 2: VISUALIZATION

plt.figure(figsize=(8, 8))
plt.title("PCA: Projecting 2D Grades onto 1D Aptitude")

# 1. Plot the centered data points (Blue dots)
plt.scatter(centered_data[:, 0], centered_data[:, 1], color='blue', s=100, label='Student Data (Centered)')

# Label points A, B, C, D
students = ['A', 'B', 'C', 'D']
for i, txt in enumerate(students):
    plt.annotate(txt, (centered_data[i, 0] + 0.2, centered_data[i, 1]), fontsize=12)

# 2. Plot the Principal Component Line (Red line)
# We extend the vector to make it look like a line going through the data
line_x = np.linspace(-4, 4, 100)
line_y = (pc1_vector[1] / pc1_vector[0]) * line_x
plt.plot(line_x, line_y, color='red', label='PC1 (Main Trend)', linewidth=2)

# 3. Visualize the Projections (Green dashed lines)
# This shows exactly how a 2D point "lands" on the 1D line
for i in range(len(centered_data)):
    # Calculate the coordinate on the line for this point
    # projection = (scalar_score) * (unit_vector)
    proj_coord = projected_data[i] * pc1_vector
    
    # Draw line from data point to the red PC1 line
    plt.plot([centered_data[i, 0], proj_coord[0]], 
             [centered_data[i, 1], proj_coord[1]], 
             color='green', linestyle='--', alpha=0.5)

# Formatting the graph
plt.axhline(0, color='black', linewidth=0.5)
plt.axvline(0, color='black', linewidth=0.5)
plt.grid(True, linestyle=':', alpha=0.6)
plt.xlabel('Math Grade (Centered)')
plt.ylabel('Science Grade (Centered)')
plt.legend()
plt.axis('equal') # Important: keeps the aspect ratio square so angles are correct
plt.show()

# Print Final 1D Scores
print("\nFinal 1D 'Aptitude' Scores (PC1 Projections):")
for i, student in enumerate(students):
    print(f"Student {student}: {projected_data[i]:.2f}")