import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
import joblib


def predict_top_cards(input_data):
    model_data = joblib.load("gpu_model.joblib")
    preprocessor = model_data["preprocessor"]
    cards_df = model_data["cards"]

    # Convert input to DataFrame
    input_df = pd.DataFrame([input_data])

    # Preprocess input
    input_encoded = preprocessor.transform(input_df)

    # Preprocess full dataset
    full_encoded = preprocessor.transform(cards_df)

    # Build and fit kNN model
    knn = NearestNeighbors(n_neighbors=10, metric="cosine")
    knn.fit(full_encoded)

    # Find nearest neighbors
    distances, indices = knn.kneighbors(input_encoded)

    # Get top 10 results
    top_matches = cards_df.iloc[indices[0]]
    return list(zip(top_matches["card"], 1 - distances[0]))


if __name__ == "__main__":
    # Example usage
    sample_input = {
        "manufacturer": "NVIDIA",
        "tdp": None,
        "power": "250",
        "architecture": "Volta",
        "performance": "High",
    }

    predictions = predict_top_cards(sample_input)
    print("Top 10 Predicted GPUs:")
    for card, score in predictions:
        print(f"{card}: {score:.4f}")
