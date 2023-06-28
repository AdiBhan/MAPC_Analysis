import numpy as np

# transition matrix
P = np.array([
    [0, 0.5, 0.5],
    [0.5, 0, 0.5],
    [1, 0, 0]
])

# initial distribution
P0 = np.array([1/3, 1/3, 1/3])

# compute P1
P1 = np.dot(P0, P)

# compute P2
P2 = np.dot(P1, P)

print(f"P1: {P1}")
print(f"P2: {P2}")
