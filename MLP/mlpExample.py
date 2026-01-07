import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# PART 1: DATA SETUP (Based on Input Layer Notes)
#
# Features: [Income, Total Debt, Job Stability (yrs), Age, Location Score]
# Location: 0 = Rural, 1 = Urban (Encoded for math)

# 1. "Young Professional" (Neuron X profile)
# Logic: High Debt + High Income + Young Age = Low Risk (Good Potential)
applicant_young_prof = [100000, 200000, 1, 24, 0]

# 2. "Lives Beyond Means" (Neuron Y profile)
# Logic: Avg Income + High Debt + High Spending = High Risk
applicant_risky = [50000, 80000, 2, 30, 1]

# 3. "Established Adult" (Neuron Z profile)
# Logic: Stable Income + Low Debt + Long Term Employment = Low Risk
applicant_stable = [85000, 5000, 10, 45, 0]

# Combine into a dataset
X_train = np.array([applicant_young_prof, applicant_risky, applicant_stable])

# Labels: 1 = Approved (Low Risk), 0 = Not Approved (High Risk)
y_train = np.array([1, 0, 1]) 


# PART 2: DEFINING THE MODEL (The Architecture)

model = keras.Sequential([
    #Input Layer is implicit (5 inputs)
    
    # -- Hidden Layer 1: Simple Patterns --
    # 3 Neurons (A, B, C) handling simple ratios like Debt-to-Income
    # Activation 'relu' acts as the "Gate/Switch" mentioned in notes
    layers.Dense(3, activation='relu', input_shape=(5,), name="Layer1_Simple_Patterns"),
    
    #Hidden Layer 2: Complex Patterns
    # 3 Neurons (X, Y, Z) identifying profiles:
    # X: Young Professional (High importance on Age < 35)
    # Y: Lives Beyond Means
    # Z: Established Adult
    layers.Dense(3, activation='relu', name="Layer2_Complex_Patterns"),
    
    # Output Layer: The Verdict
    # 1 Neuron using Sigmoid to give a probability between 0 and 1
    # < 0.5 = High Risk (Not Approved), > 0.5 = Low Risk (Approved)
    layers.Dense(1, activation='sigmoid', name="Output_Verdict")
])


# PART 3: THE MATH INSIDE (Weights & Biases)
#
# As you noted: Output = Activation(Weight * Input + Bias)

# Let's verify the model shape matches your drawing
model.summary()

print("\n--- Example of 'Neuron X' Logic (Conceptual) ---")
print("During training, the network adjusts weights to learn:")
print("  - Weight for Age: High Importance (Penalize if > 35)")
print("  - Bias: Barrier of entry (Must have Income > 80k)")
print("  - Result: If Young & Rich -> Activate 'Young Professional' Neuron")


# PART 4: COMPILING & PREDICTING

# Compile with binary_crossentropy (Standard for Yes/No classification)
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train the model briefly (100 epochs) so it learns the patterns
print("\nTraining the brain...")
model.fit(X_train, y_train, epochs=100, verbose=0)

#CREATE A NEW PERSON
# Format: [Income, Debt, Stability, Age, Location]
print("\n--- Applicantion ---")
income = int(input("\nHow much money does you make?\n>"))
debt = int(input("How much debt do you have?\n>"))
job = int(input("How many years have you been at your current employer?\n>"))
age = int(input("How old are you?\n>"))
location = int(input("Do you live in a rural(0) or urban(1) area?\n>"))

new_person = [income, debt, job, age, location]

# RUN THE TEST
# We wrap it in np.array([ ... ]) because the model expects a list of lists
prediction = model.predict(np.array([new_person]))
score = prediction[0][0]

print(f"\n--- New Applicant Test ---")
print(f"Stats: {new_person}")
print(f"Approval Score: {score:.4f}")

if score > 0.5:
    print("Verdict: APPROVED")
else:
    print("Verdict: REJECTED")