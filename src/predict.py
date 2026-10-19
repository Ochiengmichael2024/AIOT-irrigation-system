"""Load a trained model artifact and predict irrigation requirements."""

from pathlib import Path
from typing import Any

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "irrigation_model.joblib"


def load_model(model_path: str | Path = DEFAULT_MODEL_PATH) -> Any:
    """Load a previously trained scikit-learn-compatible model."""
    path = Path(model_path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Model artifact not found: {path}. Train and save a model first."
        )
    return joblib.load(path)


def predict(
    input_data: pd.DataFrame,
    model_path: str | Path = DEFAULT_MODEL_PATH,
) -> Any:
    """Run inference on sensor feature rows and return model predictions."""
    if input_data.empty:
        raise ValueError("input_data must contain at least one sensor row")
    model = load_model(model_path)
    return model.predict(input_data)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Predict irrigation requirements from CSV")
    parser.add_argument("input_csv", help="CSV containing the model's sensor features")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH)
    args = parser.parse_args()

    features = pd.read_csv(args.input_csv)
    print(predict(features, args.model))
