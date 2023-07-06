import numpy as np

# define your data
x = np.array([10.36, 9.96, 12.5])
y_true = np.array([87.87, 89.83, 71.61])

# function to calculate predicted y


def predict(x):
    return 145.5 - 5.5 * x


# calculate predicted y
y_pred = predict(x)

# calculate the differences between actual and predicted y
differences = y_true - y_pred

# square the differences
squared_differences = differences ** 2

# calculate mean squared error
mean_squared_error = np.mean(squared_differences)

# calculate root mean squared error
rmse = np.sqrt(mean_squared_error)

print("RMSE: ", rmse)
