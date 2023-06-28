import numpy as np

# transition matrix
P = np.array([[0.8, 0.1, 0.1],
              [0.1, 0.6, 0.3],
              [0.5, 0.4, 0.1]])

# initial distribution
pi = np.array([1/3, 1/3, 1/3])

while True:
    pi_next = np.dot(pi, P)
    if np.allclose(pi, pi_next):
        break
    pi = pi_next

print(pi)
