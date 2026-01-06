import numpy as np
import matplotlib.pyplot as plt

# --- PART 1: DEFINING THE MODEL PARAMETERS ---
# S = Hidden States, O = Observations
states = ["Sunny", "Rainy"]
observations = ["Walk", "Shop", "Clean"]

# Initial Probabilities (PDF Source 102)
# Sunny: 0.5, Rainy: 0.5
start_probs = np.array([0.5, 0.5])

# Transition Probabilities (PDF Source 90)
# Rows: Current State (Sunny, Rainy) -> Cols: Next State (Sunny, Rainy)
# Sunny->Sunny 0.8, Sunny->Rainy 0.2
# Rainy->Sunny 0.4, Rainy->Rainy 0.6
trans_matrix = np.array([
    [0.8, 0.2],
    [0.4, 0.6]
])

# Emission Probabilities (PDF Source 92)
# Rows: State (Sunny, Rainy) -> Cols: Observation (Walk, Shop, Clean)
# Sunny: Walk 0.6, Shop 0.3, Clean 0.1
# Rainy: Walk 0.1, Shop 0.4, Clean 0.5
emission_matrix = np.array([
    [0.6, 0.3, 0.1],
    [0.1, 0.4, 0.5]
])

# The Sequence of events observed (PDF Source 94-96)
# Day 1: Walk (Index 0), Day 2: Shop (Index 1), Day 3: Clean (Index 2)
obs_sequence = [0, 1, 2] 

# --- PART 2: CALCULATION (Greedy Approach) ---

# To store the path and probabilities for visualization
path_history = [] 
prob_history = []

# Step 1: Day 1 Initialization (PDF Source 100-105)
obs_index = obs_sequence[0]
current_probs = start_probs * emission_matrix[:, obs_index]

# Pick the winner for Day 1
winner_idx = np.argmax(current_probs)
winner_prob = current_probs[winner_idx]
path_history.append(winner_idx)
prob_history.append(winner_prob)

print(f"--- Day 1 (Observation: {observations[obs_index]}) ---")
print(f"P(Sunny) = 0.5 * {emission_matrix[0, obs_index]} = {current_probs[0]}")
print(f"P(Rainy) = 0.5 * {emission_matrix[1, obs_index]} = {current_probs[1]}")
print(f"Winner: {states[winner_idx]} ({winner_prob})\n")

# Step 2 & 3: Iterate through remaining days
for t in range(1, len(obs_sequence)):
    obs_index = obs_sequence[t]
    prev_state_idx = path_history[-1]
    prev_prob = prob_history[-1]
    
    # Calculate probabilities for moving to Next Sunny vs Next Rainy
    # Formula: Previous_Prob * Transition * Emission
    
    # Path to Sunny (Index 0)
    p_sunny = prev_prob * trans_matrix[prev_state_idx, 0] * emission_matrix[0, obs_index]
    
    # Path to Rainy (Index 1)
    p_rainy = prev_prob * trans_matrix[prev_state_idx, 1] * emission_matrix[1, obs_index]
    
    next_probs = np.array([p_sunny, p_rainy])
    
    # Pick winner
    winner_idx = np.argmax(next_probs)
    winner_prob = next_probs[winner_idx]
    
    path_history.append(winner_idx)
    prob_history.append(winner_prob)
    
    print(f"--- Day {t+1} (Observation: {observations[obs_index]}) ---")
    print(f"Checking paths from Previous Winner ({states[prev_state_idx]}):")
    print(f"-> Sunny: {prev_prob:.4f} * {trans_matrix[prev_state_idx, 0]} * {emission_matrix[0, obs_index]} = {p_sunny:.5f}")
    print(f"-> Rainy: {prev_prob:.4f} * {trans_matrix[prev_state_idx, 1]} * {emission_matrix[1, obs_index]} = {p_rainy:.5f}")
    print(f"Winner: {states[winner_idx]}\n")

final_sequence = [states[i] for i in path_history]
print(f"Final Most Likely Sequence: {' => '.join(final_sequence)}") 
# Matches Source 120: Sunny => Sunny => Rainy


# --- PART 3: VISUALIZATION ---

fig, ax = plt.subplots(figsize=(10, 6))
days = [1, 2, 3]

# Plot invisible points just to set the grid (Sunny=1, Rainy=0 for y-axis plotting)
ax.set_ylim(-0.5, 1.5)
ax.set_xlim(0.5, 3.5)
ax.set_yticks([0, 1])
ax.set_yticklabels(["Rainy", "Sunny"])
ax.set_xticks(days)
ax.set_xticklabels([f"Day 1\n(Walk)", f"Day 2\n(Shop)", f"Day 3\n(Clean)"])
ax.grid(True, linestyle='--', alpha=0.5)

# Plot the path
# Map states to Y-coordinates: Sunny->1, Rainy->0
y_coords = [1 if s == "Sunny" else 0 for s in final_sequence]

# Draw the lines connecting the winning states
ax.plot(days, y_coords, color='green', linewidth=3, marker='o', markersize=10, label='Most Likely Path')

# Annotate the probabilities on the nodes
for i, (d, y, p) in enumerate(zip(days, y_coords, prob_history)):
    ax.text(d, y + 0.1, f"P={p:.5f}", ha='center', fontweight='bold', color='green')

# Add title and labels
plt.title("HMM Decoding: Tracking the Weather", fontsize=14)
plt.ylabel("Hidden State (Weather)")
plt.xlabel("Timeline")
plt.legend()

plt.tight_layout()
plt.show()