import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier

# PART 1: CREATE THE DATASET (100 Pictures)
# We simulate 100 images by giving them numerical scores for features.
# 0 = Cat (Small snout, pointy ears)
# 1 = Dog (Longer snout, floppy ears)

np.random.seed(42) # Ensures we get the same random dots every time

# Generate 50 Cats (Centered at coordinates 2,2)
cats_data = np.random.normal(loc=2.0, scale=0.8, size=(50, 2))
cats_labels = [0] * 50  # Label 0 means Cat

# Generate 50 Dogs (Centered at coordinates 5,5)
dogs_data = np.random.normal(loc=5.0, scale=0.8, size=(50, 2))
dogs_labels = [1] * 50  # Label 1 means Dog

# Combine them into one big list of 100 "images"
X_train = np.concatenate([cats_data, dogs_data])

# We convert the list of labels into a NumPy array.
# This allows us to grab multiple items at once using "indices" later.
y_train = np.array(cats_labels + dogs_labels)


# PART 2: THE NEW "MYSTERY IMAGE" 
# Let's put this point right on the edge, but closer to dogs.
# (Snout length 3.8, Ear Floppiness 3.5)
new_image = [[3.8, 3.5]] 


# --- PART 3: RUNNING KNN (K=7) ---
print("--- KNN CLASSIFICATION REPORT ---")
print(f"Total Dataset: {len(X_train)} images")
print(f"K Value set to: 7")

# 1. Initialize the Brain
knn = KNeighborsClassifier(n_neighbors=7)

# 2. Train (Teach it where the 100 points are)
knn.fit(X_train, y_train)

# 3. Find the Neighbors
distances, indices = knn.kneighbors(new_image)

# Now this line works because y_train is a numpy array!
neighbors_labels = y_train[indices[0]] 

# Count the votes
dog_votes = np.sum(neighbors_labels == 1)
cat_votes = np.sum(neighbors_labels == 0)

print(f"\nScanning nearest 7 neighbors...")
print(f"Votes for Dog: {dog_votes}")
print(f"Votes for Cat: {cat_votes}")

# 4. Final Verdict
if dog_votes > cat_votes:
    print("\n>>> RESULT: CLASSIFIED AS DOG")
else:
    print("\n>>> RESULT: CLASSIFIED AS CAT")


# --- PART 4: VISUALIZATION ---
plt.figure(figsize=(8, 6))

# Plot the 50 Cats (Orange) and 50 Dogs (Blue)
plt.scatter(cats_data[:, 0], cats_data[:, 1], color='orange', label='Cats (Training)', alpha=0.6)
plt.scatter(dogs_data[:, 0], dogs_data[:, 1], color='blue', label='Dogs (Training)', alpha=0.6)

# Plot the New Image (Red Star)
plt.scatter(new_image[0][0], new_image[0][1], color='red', marker='*', s=300, label='New Image', zorder=10)

# Draw lines to the 7 Neighbors
nearest_points = X_train[indices[0]]
for point in nearest_points:
    plt.plot([new_image[0][0], point[0]], [new_image[0][1], point[1]], 'k--', alpha=0.3)

plt.title(f'KNN Visualization (k=7)\nVotes: {dog_votes} Dog vs {cat_votes} Cat')
plt.xlabel('Snout Length')
plt.ylabel('Ear Floppiness')
plt.legend()
plt.grid(True, linestyle=':', alpha=0.5)
plt.show()