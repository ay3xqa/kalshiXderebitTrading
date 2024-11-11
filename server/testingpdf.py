import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline, make_interp_spline
from scipy.integrate import quad
import json

# Load the data from strike_mark_data.json
with open('ETH_year_strike_mark_data.json', 'r') as f:
    data = json.load(f)

data_points = data.get("data", [])

x, y = zip(*data_points)
x = np.array(x)
y = np.array(y)

spline = UnivariateSpline(x, y, s=0.00001)  # Adjust s for more/less smoothness

x_range = np.linspace(min(x), max(x), 1000)
y_spline = spline(x_range)
y_spline_der1 = spline.derivative(n=1)(x_range)
y_spline_der2 = spline.derivative(n=2)(x_range)
y_spline_der2_clipped = np.clip(y_spline_der2, a_min=0, a_max=None)


# Plot spline -> only for backend visuals; not sent to frontend
plt.figure(figsize=(18, 6))
plt.subplot(1, 3, 1)
plt.scatter(x, y, color='red', label='Data Points')
plt.plot(x_range, y_spline, color='blue', label='Smoothing Spline')
plt.xlabel('x')
plt.ylabel('y')
plt.title('Smoothing Spline')
plt.legend()

# Plot first derivative
plt.subplot(1, 3, 2)
plt.plot(x_range, y_spline_der1, color='green', label="1st Derivative")
plt.xlabel('x')
plt.ylabel('y\'')
plt.title('First Derivative')
plt.legend()

# Plot second derivative
plt.subplot(1, 3, 3)
plt.plot(x_range, y_spline_der2_clipped, color='purple', label="2nd Derivative")
plt.xlabel('x')
plt.ylabel('y\'\'')
plt.title('Second Derivative')
plt.legend()

plt.tight_layout()
plt.show()

second_derivative = spline.derivative(n=2)
first_derivative = second_derivative.antiderivative(n=1)
lower_bound = 0
upper_bound = max(x)

# @brief    Transform range (y-values) of PDF to be at least 0
# @params   x:  Numpy Array -> Sample Domain (x-values) of PDF
# @return   y:  Numpy Array -> Transformed Range (y-values) of PDF
def clipped_derivative(x):
    return max(0, second_derivative(x))  # Return max(0, f''(x))

# @brief    Calculate probability of underlying asset to reach or exceed target price with data from json
# @params   target_price: FLOAT -> target_price of underlying asset
# @return   probability_percentage: FLOAT -> percentage format of the probability
def get_pdf_probability_of_gte(target_price):
    numerator, _ = quad(clipped_derivative, target_price, upper_bound)
    denominator, _ = quad(clipped_derivative, lower_bound, upper_bound)
    probability = numerator / denominator if denominator != 0 else 0
    probability_percentage = round(probability * 100,2)
    return probability_percentage

# @brief    Calculate probability of underlying asset to NOT reach or exceed target price with data from json
# @params   target_price: FLOAT -> target_price of underlying asset
# @return   probability_percentage: FLOAT -> percentage format of the probability
def get_pdf_probability_of_lte(target_price):
    numerator, _ = quad(clipped_derivative, 0, target_price)
    denominator, _ = quad(clipped_derivative, lower_bound, upper_bound)
    probability = numerator / denominator if denominator != 0 else 0
    probability_percentage = round(probability * 100,2)
    return probability_percentage

def get_pdf_probability_of_range(lower, upper):
    numerator, _ = quad(clipped_derivative, lower, upper)
    denominator, _ = quad(clipped_derivative, lower_bound, upper_bound)
    probability = numerator / denominator if denominator != 0 else 0
    probability_percentage = round(probability * 100,2)
    return probability_percentage

#function to send over data for grpahs for UI
def get_graph_data():
    data = {
        "original_function": {
            "x": x_range.tolist(),
            "y": y_spline.tolist()
        },
        "first_derivative": {
            "x": x_range.tolist(),
            "y": y_spline_der1.tolist()
        },
        "second_derivative": {
            "x": x_range.tolist(),
            "y": y_spline_der2_clipped.tolist()
        }
    }
    return data

print(get_pdf_probability_of_gte(4500))