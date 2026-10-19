# Smart Irrigation ML

A starter machine-learning project for preparing IoT sensor readings and predicting irrigation requirements. Raw datasets belong in `data/raw/`; cleaned datasets are written to `data/processed/`; trained model artifacts belong in `models/`.

## Setup

From the project root, create and activate a virtual environment, then install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS/Linux, activate with `source .venv/bin/activate` after creating the environment with `python3 -m venv .venv`.

## Workflow

1. Put a sensor-data CSV in `data/raw/`.
2. Explore the dataset in `notebooks/01_data_exploration.ipynb`.
3. Clean and prepare features in `notebooks/02_data_preprocessing.ipynb` or run the preprocessing utility:

   ```powershell
   python -c "from src.preprocessing import preprocess_file; print(preprocess_file('sensor_readings.csv'))"
   ```

4. Use `notebooks/03_model_training.ipynb` to train and evaluate candidate models, then save the selected model with `joblib.dump(model, 'models/irrigation_model.joblib')`.
5. Assess results in `notebooks/04_model_evaluation.ipynb`.
6. Run inference against a CSV of feature columns expected by the trained model:

   ```powershell
   python src/predict.py data/processed/new_sensor_readings.csv
   ```

   Supply a different artifact with `--model path/to/model.joblib`.

   ## Data Flow

   ```text
   Sensor readings or historical dataset
         |
         v
         data/raw/*.csv
         |
         +----> 01_data_exploration.ipynb
         |      inspect columns, distributions, and missing values
         v
         02_data_preprocessing.ipynb
         or src/preprocessing.py
         |
         v
      data/processed/*_processed.csv
         |
      +------+------+
      |             |
      v             v
   03_model_training  04_model_evaluation
      |
      v
   models/irrigation_model.joblib
      |
      v
   Feature CSV -> src/predict.py -> printed predictions
   ```

   1. Place historical or collected sensor readings in `data/raw/` as CSV files. The exploration notebook inspects the data; it does not modify the source file.
   2. Preprocessing reads a raw CSV, interpolates short gaps in numeric sensor columns, fills remaining numeric gaps with each column's median, and writes the result to `data/processed/`. Non-numeric columns are retained as-is.
   3. Set the target column in the training notebook. It uses the remaining numeric columns as features, splits the data into training and test sets, trains a classifier or regressor based on the target type, and saves the fitted model under `models/`.
   4. The evaluation notebook reloads the processed data and saved model, then reports classification or regression metrics on its held-out split.
   5. For batch inference, provide `src/predict.py` with a CSV containing the same feature columns, names, and order used during training. The script loads the saved model and prints its predictions.

   This repository currently implements an offline, file-based machine-learning workflow. It does not acquire live readings from a device or send predictions to a pump or irrigation controller; those integrations must be added separately.

## Project Layout

   ```text
smart-irrigation/
├── data/
│   ├── raw/                   # Original sensor data (keep source files unchanged)
│   └── processed/             # Cleaned, model-ready datasets
├── models/                    # Serialized model artifacts (not included by default)
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_data_preprocessing.ipynb
│   ├── 03_model_training.ipynb
│   └── 04_model_evaluation.ipynb
├── src/
│   ├── predict.py              # Model loading and batch inference
│   └── preprocessing.py        # CSV loading, interpolation, and processed-data output
├── README.md
└── requirements.txt
```

The model's feature names and order at inference must match the data used during training. Update the sensor columns, target definition, and evaluation strategy to suit the actual device and irrigation use case; the starter project does not assume a particular dataset or target.
