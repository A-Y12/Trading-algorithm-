from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import os
import json

app = Flask(__name__)

# Load the trained model
model = load_model("models/models/stock_lstm.keras")


# Load normalization parameters (from training)
def load_normalization_params():
    # Ideally, load min_price and max_price from a JSON file or a database
    try:
        with open("models/normalization_params.json", "r") as file:
            params = json.load(file)
        return params["min_price"], params["max_price"]
    except Exception as e:
        print(f"Error loading normalization params: {e}")
        return None, None


min_price, max_price = load_normalization_params()

if min_price is None or max_price is None:
    raise ValueError("Normalization parameters (min_price, max_price) are not available.")


# Function to prepare input data for prediction
def preprocess_data(data, time_steps=10):
    # Check if data is a valid list of numbers
    if not isinstance(data, list) or len(data) < time_steps:
        raise ValueError("Data must be a list with at least 10 values.")

    data = (np.array(data) - min_price) / (max_price - min_price)  # Normalize
    sequences = []
    for i in range(len(data) - time_steps):
        sequences.append(data[i:i + time_steps])
    return np.array(sequences)


@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Parse JSON request
        input_data = request.json.get("data")
        if not input_data:
            return jsonify({"error": "No data provided"}), 400

        # Preprocess data
        time_steps = 5
        sequences = preprocess_data(input_data, time_steps)

        # Reshape for LSTM input
        sequences = sequences.reshape((sequences.shape[0], sequences.shape[1], 1))

        # Make predictions
        predictions = model.predict(sequences)
        predictions = predictions.flatten()  # Convert to 1D array

        # Denormalize predictions
        predictions = predictions * (max_price - min_price) + min_price

        return jsonify({"predictions": predictions.tolist()})

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400  # Handle invalid data input

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route("/", methods=["GET"])
def home():
    return "Welcome to the Stock Prediction API! Use the /predict endpoint to get predictions."



if __name__ == "__main__":
    app.run(debug=True)
