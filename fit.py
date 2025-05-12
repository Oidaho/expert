import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import joblib

# Load data
with open("gpus.json", "r") as f:
    data = pd.read_json(f)

# Define feature types
categorical_features = ["manufacturer", "architecture", "performance"]
numerical_features = ["tdp", "power"]

# Create preprocessing pipeline
preprocessor = ColumnTransformer(
    transformers=[
        (
            "num",
            Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]),
            numerical_features,
        ),
        (
            "cat",
            Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
                    ("onehot", OneHotEncoder(handle_unknown="ignore")),
                ]
            ),
            categorical_features,
        ),
    ]
)

# Fit and transform the data
X = data[categorical_features + numerical_features]
preprocessor.fit(X)

# Save the preprocessor and the full dataset
joblib.dump({"preprocessor": preprocessor, "cards": data}, "gpu_model.joblib")

print("Model saved successfully.")
