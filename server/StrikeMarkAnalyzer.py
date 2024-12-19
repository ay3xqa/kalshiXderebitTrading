import json
import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.integrate import quad

class StrikeMarkAnalyzer:
    def __init__(self, asset, timeline):
        self.asset = asset
        self.timeline = timeline
        self.data_points = self.load_data()
        self.update_analysis()  # Initial analysis after loading data

    def load_data(self):
        # Load data dynamically based on asset and timeline
        file_name = f'{self.asset}_{self.timeline}_strike_mark_data.json'
        try:
            with open(file_name, 'r') as f:
                data = json.load(f)
            return data.get("data", [])
        except FileNotFoundError:
            raise ValueError(f"Data file {file_name} not found")

    def update_analysis(self):
        # Extract x and y from data points
        if not self.data_points:  # Check if data_points is empty
            self.x = np.array([])
            self.y = np.array([])
            self.spline = None
            self.x_range = np.array([])
            self.y_spline = np.array([])
            self.y_spline_der1 = np.array([])
            self.y_spline_der2 = np.array([])
            self.y_spline_der2_clipped = np.array([])
            self.second_derivative = None
            self.lower_bound = 0
            self.upper_bound = 0
            return

        x, y = zip(*self.data_points)
        self.x = np.array(x)
        self.y = np.array(y)

        # Fit the spline
        self.spline = UnivariateSpline(self.x, self.y, s=0.00001)

        # Set up the x_range for plotting and derivatives
        self.x_range = np.linspace(min(self.x), max(self.x), 1000)
        self.y_spline = self.spline(self.x_range)
        self.y_spline_der1 = self.spline.derivative(n=1)(self.x_range)
        self.y_spline_der2 = self.spline.derivative(n=2)(self.x_range)
        self.y_spline_der2_clipped = np.clip(self.y_spline_der2, a_min=0, a_max=None)

        # Second derivative function for probability calculations
        self.second_derivative = self.spline.derivative(n=2)
        self.lower_bound = 0
        self.upper_bound = max(self.x)

    def refresh_data(self):
        self.data_points = self.load_data()  # Load the new data
        self.update_analysis()  # Update the analysis with the new data

    def clipped_derivative(self, x):
        return max(0, self.second_derivative(x))

    def get_pdf_probability_of_gte(self, target_price):
        numerator, _ = quad(self.clipped_derivative, target_price, self.upper_bound)
        denominator, _ = quad(self.clipped_derivative, self.lower_bound, self.upper_bound)
        probability = numerator / denominator if denominator != 0 else 0
        return round(probability * 100, 2)

    def get_pdf_probability_of_lte(self, target_price):
        numerator, _ = quad(self.clipped_derivative, 0, target_price)
        denominator, _ = quad(self.clipped_derivative, self.lower_bound, self.upper_bound)
        probability = numerator / denominator if denominator != 0 else 0
        return round(probability * 100, 2)

    def get_pdf_probability_of_range(self, lower, upper):
        numerator, _ = quad(self.clipped_derivative, lower, upper)
        denominator, _ = quad(self.clipped_derivative, self.lower_bound, self.upper_bound)
        probability = numerator / denominator if denominator != 0 else 0
        return round(probability * 100, 2)

    def get_graph_data(self):
        return {
            "original_function": {
                "x": self.x_range.tolist(),
                "y": self.y_spline.tolist()
            },
            "first_derivative": {
                "x": self.x_range.tolist(),
                "y": self.y_spline_der1.tolist()
            },
            "second_derivative": {
                "x": self.x_range.tolist(),
                "y": self.y_spline_der2_clipped.tolist()
            }
        }
