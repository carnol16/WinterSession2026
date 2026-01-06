import numpy as np

def find_sigma_demo():
    # SETUP
    k = 3
    target_budget = np.log2(k) # Target is ~1.585
    
    # Let's use the 'Popular Book A' distances from before
    # Neighbor 1 is at 0.1 (This is rho)
    # Neighbor 2 is at 0.5
    # Neighbor 3 is at 2.0
    distances = np.array([0.1, 0.2, 2.0])
    rho = distances[0] # 0.1
    
    print(f"TARGET SUM: {target_budget:.4f}")
    print(f"Distances: {distances}")
    print("-" * 40)
    
    #BINARY SEARCH
    min_sigma = 0.001
    max_sigma = 10.0
    
    # We will do 5 iterations to show the convergence
    for i in range(1, 20):
        # 1. Make a guess (middle of current range)
        current_sigma = (min_sigma + max_sigma) / 2
        
        # 2. Calculate scores with this sigma
        # formula: exp(-(d - rho) / sigma)
        scores = np.exp(-(distances - rho) / current_sigma)
        
        # 3. Sum the scores
        current_sum = np.sum(scores)
        
        # 4. Check against target
        diff = current_sum - target_budget
        
        print(f"Round {i}: Guess Sigma = {current_sigma:.4f} | Sum = {current_sum:.4f}", end=" ")
        
        if current_sum > target_budget:
            print(f"--> Too High! (Shrink Sigma)")
            max_sigma = current_sigma # The correct answer is below this
        else:
            print(f"--> Too Low!  (Grow Sigma)")
            min_sigma = current_sigma # The correct answer is above this

    print("-" * 40)
    print(f"Final Estimated Sigma: {current_sigma:.4f}")

find_sigma_demo()