from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
import os
import json
from datetime import datetime
from typing import List
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import cross_val_score, GridSearchCV

app = FastAPI()

# Mount static files for dashboard at root level so CSS/JS load properly
app.mount("/static", StaticFiles(directory="dashboard"), name="static")

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "production_model.pkl")
METADATA_PATH = os.path.join(os.path.dirname(__file__), "models", "model_metadata.json")
MODEL_VERSIONS_PATH = os.path.join(os.path.dirname(__file__), "models", "model_versions.json")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
RUNS_PATH = os.path.join(os.path.dirname(__file__), "runs")
LOGS_PATH = os.path.join(os.path.dirname(__file__), "logs")
PREDICTIONS_LOG_PATH = os.path.join(LOGS_PATH, "predictions.json")
DATASETS_PATH = os.path.join(os.path.dirname(__file__), "datasets")

model = None


def get_next_model_version():
    """Get the next available model version number."""
    try:
        if os.path.exists(MODEL_VERSIONS_PATH):
            with open(MODEL_VERSIONS_PATH, "r") as f:
                versions_data = json.load(f)
                versions = versions_data.get("versions", [])
                if versions:
                    last_version = versions[-1]["version"]
                    version_num = int(last_version[1:])  # Remove 'v' prefix
                    return f"v{version_num + 1}"
        return "v1"
    except:
        return "v1"


def save_versioned_model(model, model_name, task_type, score, best_params=None):
    """Save model with versioning and update metadata."""
    version = get_next_model_version()
    
    # Save versioned model
    os.makedirs(MODELS_DIR, exist_ok=True)
    versioned_model_path = os.path.join(MODELS_DIR, f"model_{version}.pkl")
    joblib.dump(model, versioned_model_path)
    
    # Also save as production model for backward compatibility
    joblib.dump(model, MODEL_PATH)
    
    # Update model versions metadata
    if os.path.exists(MODEL_VERSIONS_PATH):
        with open(MODEL_VERSIONS_PATH, "r") as f:
            try:
                versions_data = json.load(f)
            except json.JSONDecodeError:
                versions_data = {"versions": []}
    else:
        versions_data = {"versions": []}
    
    # Add new version
    version_entry = {
        "version": version,
        "model_name": model_name,
        "task_type": task_type,
        "score": score,
        "timestamp": datetime.now().isoformat()
    }
    
    if best_params:
        version_entry["best_params"] = best_params
    
    versions_data["versions"].append(version_entry)
    versions_data["latest_version"] = version
    versions_data["production_model"] = version
    
    # Save updated versions metadata
    with open(MODEL_VERSIONS_PATH, "w") as f:
        json.dump(versions_data, f, indent=2)
    
    # Update regular metadata for backward compatibility
    metadata = {
        "model_name": model_name,
        "task_type": task_type,
        "score": score,
        "version": version,
        "timestamp": datetime.now().isoformat()
    }
    
    if best_params:
        metadata["best_params"] = best_params
    
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    
    return version


def append_prediction_log(log_entry):
    os.makedirs(LOGS_PATH, exist_ok=True)

    if not os.path.exists(PREDICTIONS_LOG_PATH):
        with open(PREDICTIONS_LOG_PATH, "w") as f:
            json.dump([], f, indent=2)

    with open(PREDICTIONS_LOG_PATH, "r") as f:
        try:
            logs = json.load(f)
            if not isinstance(logs, list):
                logs = []
        except json.JSONDecodeError:
            logs = []

    logs.append(log_entry)

    with open(PREDICTIONS_LOG_PATH, "w") as f:
        json.dump(logs, f, indent=2)

@app.on_event("startup")
def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
    else:
        model = None

class PredictRequest(BaseModel):
    features: List[float]

class PredictResponse(BaseModel):
    prediction: int

class BatchPredictRequest(BaseModel):
    features: List[List[float]]

class BatchPredictResponse(BaseModel):
    predictions: List[int]

@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    if not os.path.exists(MODEL_PATH):
        raise HTTPException(status_code=500, detail=f"Model file not found at {MODEL_PATH}")

    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    if len(request.features) != 4:
        raise HTTPException(status_code=400, detail="Features must have exactly 4 elements")
    
    features_array = np.array(request.features).reshape(1, 4)
    prediction = model.predict(features_array)[0]

    append_prediction_log(
        {
            "timestamp": datetime.now().isoformat(),
            "input": request.features,
            "prediction": int(prediction),
        }
    )
    
    return PredictResponse(prediction=int(prediction))

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}

@app.get("/model-info")
def model_info():
    if not os.path.exists(METADATA_PATH):
        raise HTTPException(status_code=404, detail=f"Model metadata not found at {METADATA_PATH}")

    with open(METADATA_PATH, "r") as f:
        metadata = json.load(f)

    return {
        "model_name": metadata.get("model_name"),
        "task_type": metadata.get("task_type"),
        "best_params": metadata.get("best_params", {}),  # Default to empty dict for backward compatibility
        "score": metadata.get("score", metadata.get("accuracy")),  # Backward compatibility
        "timestamp": metadata.get("timestamp")
    }

@app.get("/runs")
def list_runs():
    if not os.path.exists(RUNS_PATH):
        return {"runs": []}

    run_names = [
        name for name in os.listdir(RUNS_PATH)
        if os.path.isdir(os.path.join(RUNS_PATH, name))
    ]
    run_names.sort(reverse=True)
    return {"runs": run_names}

@app.post("/batch-predict", response_model=BatchPredictResponse)
def batch_predict(request: BatchPredictRequest):
    if not os.path.exists(MODEL_PATH):
        raise HTTPException(status_code=500, detail=f"Model file not found at {MODEL_PATH}")

    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    features_array = np.array(request.features)

    if features_array.ndim != 2 or features_array.shape[1] != 4:
        raise HTTPException(status_code=400, detail="Each feature row must contain exactly 4 values")

    predictions = model.predict(features_array)
    prediction_list = [int(p) for p in predictions]

    append_prediction_log(
        {
            "timestamp": datetime.now().isoformat(),
            "input": request.features,
            "predictions": prediction_list,
        }
    )

    return BatchPredictResponse(predictions=prediction_list)

@app.get("/prediction-stats")
def prediction_stats():
    """
    Analyze predictions stored in logs/predictions.json and return total predictions,
    class distribution, and last prediction timestamp.
    """
    try:
        # Check if prediction log file exists
        if not os.path.exists(PREDICTIONS_LOG_PATH):
            return {
                "message": "no predictions logged yet"
            }
        
        # Load prediction logs
        try:
            with open(PREDICTIONS_LOG_PATH, "r") as f:
                logs = json.load(f)
                if not isinstance(logs, list):
                    logs = []
        except (json.JSONDecodeError, FileNotFoundError):
            return {
                "message": "no predictions logged yet"
            }
        
        # Handle empty logs
        if not logs:
            return {
                "message": "no predictions logged yet"
            }
        
        total_predictions = 0
        class_distribution = {}
        latest_timestamp = None
        
        # Process each log entry
        for log_entry in logs:
            # Handle single predictions
            if "prediction" in log_entry:
                total_predictions += 1
                pred_class = str(log_entry["prediction"])
                class_distribution[pred_class] = class_distribution.get(pred_class, 0) + 1
            
            # Handle batch predictions
            elif "predictions" in log_entry:
                predictions = log_entry["predictions"]
                total_predictions += len(predictions)
                for pred in predictions:
                    pred_class = str(pred)
                    class_distribution[pred_class] = class_distribution.get(pred_class, 0) + 1
            
            # Update latest timestamp
            if "timestamp" in log_entry:
                timestamp = log_entry["timestamp"]
                if latest_timestamp is None or timestamp > latest_timestamp:
                    latest_timestamp = timestamp
        
        return {
            "total_predictions": total_predictions,
            "class_distribution": class_distribution,
            "last_prediction": latest_timestamp
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction stats analysis failed: {str(e)}")

@app.post("/retrain")
def retrain():
    """
    Retrain the model using iris dataset with RandomForestClassifier and LogisticRegression.
    Select the best model based on 5-fold cross-validation accuracy.
    """
    try:
        # Load iris dataset
        iris = load_iris()
        X, y = iris.data, iris.target
        
        # Define models to compare
        models = {
            "RandomForestClassifier": RandomForestClassifier(random_state=42),
            "LogisticRegression": LogisticRegression(random_state=42, max_iter=200)
        }
        
        best_model_name = None
        best_accuracy = 0
        best_model = None
        
        # Evaluate each model using 5-fold cross-validation
        for model_name, model_instance in models.items():
            cv_scores = cross_val_score(model_instance, X, y, cv=5, scoring='accuracy')
            mean_accuracy = cv_scores.mean()
            
            if mean_accuracy > best_accuracy:
                best_accuracy = mean_accuracy
                best_model_name = model_name
                best_model = model_instance
        
        # Train the best model on the full dataset
        best_model.fit(X, y)
        
        # Save the model with versioning
        version = save_versioned_model(
            best_model, 
            best_model_name, 
            "classification", 
            float(best_accuracy),
            {}  # No hyperparameter tuning in retrain endpoint
        )
        
        # Reload the model in memory
        global model
        model = best_model
        
        return {
            "status": "retraining completed",
            "task_type": "classification",
            "best_model": best_model_name,
            "version": version,
            "best_params": {},
            "score": float(best_accuracy)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")

@app.post("/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):
    """
    Upload a CSV dataset file and save it to the datasets folder.
    """
    try:
        # Check if the uploaded file is a CSV
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
        # Create datasets directory if it doesn't exist
        os.makedirs(DATASETS_PATH, exist_ok=True)
        
        # Define the file path
        file_path = os.path.join(DATASETS_PATH, "user_dataset.csv")
        
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "status": "dataset uploaded successfully",
            "filename": "user_dataset.csv"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/train-uploaded-dataset")
def train_uploaded_dataset():
    """
    Train models using uploaded dataset from datasets/user_dataset.csv with automatic model selection 
    and hyperparameter optimization.
    The last column is assumed to be the target label.
    Automatically detects task type (classification/regression) and applies GridSearchCV for RandomForest models.
    """
    try:
        # Check if uploaded dataset exists
        dataset_path = os.path.join(DATASETS_PATH, "user_dataset.csv")
        if not os.path.exists(dataset_path):
            raise HTTPException(status_code=404, detail="No dataset found. Please upload a dataset first using /upload-dataset.")
        
        # Load dataset using pandas
        df = pd.read_csv(dataset_path)
        
        # Check if dataset has at least 2 columns (features + target)
        if df.shape[1] < 2:
            raise HTTPException(status_code=400, detail="Dataset must have at least 2 columns (features + target)")
        
        # Split data: X = all columns except last, y = last column
        X = df.iloc[:, :-1].values
        y = df.iloc[:, -1].values
        
        # Determine appropriate cross-validation strategy based on dataset size
        n_samples = len(X)
        if n_samples < 3:
            raise HTTPException(status_code=400, detail="Dataset must have at least 3 samples for training")
        
        # Choose appropriate CV strategy based on dataset size
        if n_samples >= 10:
            cv_folds = 5
        elif n_samples >= 6:
            cv_folds = 3
        else:
            cv_folds = 2  # Minimum for cross-validation
        
        # Detect task type based on target column unique values
        target_column = df.columns[-1]
        unique_target_values = df[target_column].nunique()
        
        best_model_name = None
        best_score = -float('inf')  # Use -inf to handle negative scores (like R2)
        best_model = None
        best_params = {}
        
        if unique_target_values <= 10:
            task_type = "classification"
            scoring = 'accuracy'
            
            # GridSearchCV for RandomForestClassifier
            rf_param_grid = {
                "n_estimators": [50, 100, 200],
                "max_depth": [None, 10, 20]
            }
            
            try:
                rf_classifier = RandomForestClassifier(random_state=42)
                rf_grid_search = GridSearchCV(rf_classifier, rf_param_grid, cv=cv_folds, scoring=scoring, n_jobs=-1)
                rf_grid_search.fit(X, y)
                rf_score = rf_grid_search.best_score_
                
                if rf_score > best_score:
                    best_score = rf_score
                    best_model_name = "RandomForestClassifier"
                    best_model = rf_grid_search.best_estimator_
                    best_params = rf_grid_search.best_params_
            except Exception as e:
                pass  # Continue with next model if this one fails
            
            # LogisticRegression without tuning
            try:
                lr_model = LogisticRegression(random_state=42, max_iter=1000)
                lr_scores = cross_val_score(lr_model, X, y, cv=cv_folds, scoring=scoring)
                lr_score = lr_scores.mean()
                
                if lr_score > best_score:
                    best_score = lr_score
                    best_model_name = "LogisticRegression"
                    best_model = lr_model
                    best_params = {}  # No hyperparameter tuning for LR
            except Exception as e:
                pass  # Continue if this model fails
                
        else:
            task_type = "regression"
            scoring = 'r2'
            
            # GridSearchCV for RandomForestRegressor
            rf_param_grid = {
                "n_estimators": [50, 100],
                "max_depth": [None, 10]
            }
            
            try:
                rf_regressor = RandomForestRegressor(random_state=42)
                rf_grid_search = GridSearchCV(rf_regressor, rf_param_grid, cv=cv_folds, scoring=scoring, n_jobs=-1)
                rf_grid_search.fit(X, y)
                rf_score = rf_grid_search.best_score_
                
                if rf_score > best_score:
                    best_score = rf_score
                    best_model_name = "RandomForestRegressor"
                    best_model = rf_grid_search.best_estimator_
                    best_params = rf_grid_search.best_params_
            except Exception as e:
                pass  # Continue with next model if this one fails
            
            # LinearRegression without tuning
            try:
                lr_model = LinearRegression()
                lr_scores = cross_val_score(lr_model, X, y, cv=cv_folds, scoring=scoring)
                lr_score = lr_scores.mean()
                
                if lr_score > best_score:
                    best_score = lr_score
                    best_model_name = "LinearRegression"
                    best_model = lr_model
                    best_params = {}  # No hyperparameter tuning for linear regression
            except Exception as e:
                pass  # Continue if this model fails
        
        if best_model is None:
            raise HTTPException(status_code=500, detail="No model could be trained successfully. Please check your dataset format.")
        
        # Train the best model on the full dataset if it wasn't already trained by GridSearchCV
        if best_params == {}:  # Only fit if it's not a GridSearchCV result
            best_model.fit(X, y)
        
        # Save the model with versioning
        version = save_versioned_model(
            best_model, 
            best_model_name, 
            task_type, 
            float(best_score),
            best_params
        )
        
        # Reload the model in memory
        global model
        model = best_model
        
        return {
            "status": "training completed",
            "task_type": task_type,
            "best_model": best_model_name,
            "version": version,
            "best_params": best_params,
            "score": float(best_score)
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@app.get("/dataset-info")
def dataset_info():
    """
    Analyze the dataset and return information about samples, features, columns, 
    target column, task type, and missing values.
    """
    try:
        # Check if dataset exists
        dataset_path = os.path.join(DATASETS_PATH, "user_dataset.csv")
        if not os.path.exists(dataset_path):
            raise HTTPException(status_code=404, detail="Dataset not found. Please upload a dataset first using /upload-dataset.")
        
        # Load dataset using pandas
        df = pd.read_csv(dataset_path)
        
        # Get number of samples (rows) and features (columns - 1)
        samples = len(df)
        features = df.shape[1] - 1
        
        # Get column names
        columns = df.columns.tolist()
        
        # Assume last column is the target
        target_column = columns[-1]
        
        # Count missing values across entire dataset
        missing_values = df.isnull().sum().sum()
        
        # Determine task type based on target column unique values
        unique_target_values = df[target_column].nunique()
        if unique_target_values <= 10:
            task_type = "classification"
        else:
            task_type = "regression"
        
        return {
            "samples": samples,
            "features": features,
            "columns": columns,
            "target_column": target_column,
            "task_type": task_type,
            "missing_values": int(missing_values)
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dataset analysis failed: {str(e)}")


@app.get("/feature-importance")
def feature_importance():
    """
    Get feature importance from the production model.
    Uses model.feature_importances_ for tree-based models or absolute coefficients for linear models.
    """
    try:
        # Check if model is loaded
        if model is None:
            raise HTTPException(status_code=500, detail="Model not loaded")
        
        # Check if dataset exists to get feature names
        dataset_path = os.path.join(DATASETS_PATH, "user_dataset.csv")
        if not os.path.exists(dataset_path):
            raise HTTPException(status_code=404, detail="Dataset not found. Feature names cannot be determined.")
        
        # Load dataset to get feature names
        df = pd.read_csv(dataset_path)
        
        # Extract feature names (all columns except target - last column)
        feature_names = df.columns[:-1].tolist()
        
        # Check if model has feature_importances_ attribute (tree-based models)
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        # Check if model has coef_ attribute (linear models like LogisticRegression)
        elif hasattr(model, 'coef_'):
            # Use absolute values of coefficients
            coef = model.coef_
            if len(coef.shape) > 1:
                # For multi-class classification, take mean of absolute values across classes
                importances = np.mean(np.abs(coef), axis=0)
            else:
                # For binary classification or regression
                importances = np.abs(coef.flatten())
        else:
            raise HTTPException(status_code=400, detail="Model does not support feature importance extraction")
        
        # Check if number of features matches
        if len(feature_names) != len(importances):
            raise HTTPException(status_code=500, detail="Mismatch between number of features in dataset and model")
        
        # Create feature importance dictionary
        feature_importance_dict = {
            feature_name: float(importance) 
            for feature_name, importance in zip(feature_names, importances)
        }
        
        return {
            "feature_importance": feature_importance_dict
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feature importance extraction failed: {str(e)}")


@app.get("/prediction-history")
def prediction_history():
    """
    Get prediction history analysis including total predictions, class distribution,
    last prediction time, and recent predictions.
    """
    try:
        # Check if prediction log file exists
        if not os.path.exists(PREDICTIONS_LOG_PATH):
            return {
                "message": "no predictions logged yet"
            }
        
        # Load prediction logs
        try:
            with open(PREDICTIONS_LOG_PATH, "r") as f:
                logs = json.load(f)
                if not isinstance(logs, list):
                    logs = []
        except (json.JSONDecodeError, FileNotFoundError):
            return {
                "message": "no predictions logged yet"
            }
        
        # Handle empty logs
        if not logs:
            return {
                "message": "no predictions logged yet"
            }
        
        total_predictions = 0
        class_distribution = {}
        latest_timestamp = None
        all_predictions = []
        
        # Process each log entry
        for log_entry in logs:
            # Handle single predictions
            if "prediction" in log_entry:
                total_predictions += 1
                pred_class = str(log_entry["prediction"])
                class_distribution[pred_class] = class_distribution.get(pred_class, 0) + 1
                
                # Add to all predictions list for recent predictions
                prediction_data = {
                    "timestamp": log_entry.get("timestamp"),
                    "input": log_entry.get("input"),
                    "prediction": log_entry["prediction"]
                }
                all_predictions.append(prediction_data)
            
            # Handle batch predictions
            elif "predictions" in log_entry:
                predictions = log_entry["predictions"]
                total_predictions += len(predictions)
                
                # Process each prediction in the batch
                for i, pred in enumerate(predictions):
                    pred_class = str(pred)
                    class_distribution[pred_class] = class_distribution.get(pred_class, 0) + 1
                    
                    # Add each batch prediction to all predictions list
                    prediction_data = {
                        "timestamp": log_entry.get("timestamp"),
                        "input": log_entry.get("input", [[]])[i] if log_entry.get("input") and i < len(log_entry.get("input", [])) else None,
                        "prediction": pred
                    }
                    all_predictions.append(prediction_data)
            
            # Update latest timestamp
            if "timestamp" in log_entry:
                timestamp = log_entry["timestamp"]
                if latest_timestamp is None or timestamp > latest_timestamp:
                    latest_timestamp = timestamp
        
        # Get last 5 predictions (most recent first)
        recent_predictions = all_predictions[-5:] if len(all_predictions) >= 5 else all_predictions
        recent_predictions.reverse()  # Most recent first
        
        return {
            "total_predictions": total_predictions,
            "class_distribution": class_distribution,
            "last_prediction_time": latest_timestamp,
            "recent_predictions": recent_predictions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction history analysis failed: {str(e)}")


@app.get("/model-versions")
def model_versions():
    """
    Get list of all trained model versions.
    """
    try:
        if not os.path.exists(MODEL_VERSIONS_PATH):
            return {
                "message": "No model versions found",
                "versions": []
            }
        
        with open(MODEL_VERSIONS_PATH, "r") as f:
            versions_data = json.load(f)
        
        return {
            "latest_version": versions_data.get("latest_version"),
            "production_model": versions_data.get("production_model"),
            "versions": versions_data.get("versions", [])
        }
        
    except json.JSONDecodeError:
        return {
            "message": "Invalid model versions file",
            "versions": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model versions: {str(e)}")


@app.get("/model-performance")
def model_performance():
    """
    Compare performance of all model versions.
    """
    try:
        if not os.path.exists(MODEL_VERSIONS_PATH):
            return {
                "message": "No model versions found",
                "models": []
            }
        
        with open(MODEL_VERSIONS_PATH, "r") as f:
            versions_data = json.load(f)
        
        versions = versions_data.get("versions", [])
        
        if not versions:
            return {
                "message": "No model versions available",
                "models": []
            }
        
        # Extract model performance data
        models = []
        best_score = -float('inf')
        best_model = None
        
        for version in versions:
            model_data = {
                "version": version["version"],
                "model_name": version.get("model_name", "Unknown"),
                "task_type": version.get("task_type", "Unknown"),
                "score": version["score"],
                "timestamp": version.get("timestamp")
            }
            models.append(model_data)
            
            # Track best model
            if version["score"] > best_score:
                best_score = version["score"]
                best_model = version["version"]
        
        response = {
            "models": models,
            "best_model": best_model
        }
        
        # Calculate improvement over first version if available
        if len(versions) > 1:
            first_score = versions[0]["score"]
            latest_score = versions[-1]["score"]
            improvement = ((latest_score - first_score) / first_score) * 100
            
            response["improvement_over_v1"] = f"{improvement:.1f}%"
            response["first_model_score"] = first_score
            response["latest_model_score"] = latest_score
        
        return response
        
    except json.JSONDecodeError:
        return {
            "message": "Invalid model versions file",
            "models": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze model performance: {str(e)}")


@app.get("/dataset-summary")
def dataset_summary():
    """
    Analyze the dataset and return comprehensive summary including rows, columns,
    column names, and missing values per column.
    """
    try:
        # Check if dataset exists
        dataset_path = os.path.join(DATASETS_PATH, "user_dataset.csv")
        if not os.path.exists(dataset_path):
            raise HTTPException(status_code=404, detail="Dataset not found. Please upload a dataset first using /upload-dataset.")
        
        # Load dataset using pandas
        df = pd.read_csv(dataset_path)
        
        # Get basic info
        rows = len(df)
        columns = len(df.columns)
        column_names = df.columns.tolist()
        
        # Calculate missing values per column
        missing_values = {}
        for column in df.columns:
            missing_values[column] = int(df[column].isnull().sum())
        
        return {
            "rows": rows,
            "columns": columns,
            "column_names": column_names,
            "missing_values": missing_values
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dataset summary analysis failed: {str(e)}")


@app.get("/model-dashboard")
def model_dashboard():
    """
    Return summary of the ML system including production model, total models,
    total predictions, and latest model accuracy.
    """
    try:
        # Initialize default values
        production_model = None
        total_models = 0
        total_predictions = 0
        latest_model_accuracy = None
        
        # Load model versions
        if os.path.exists(MODEL_VERSIONS_PATH):
            try:
                with open(MODEL_VERSIONS_PATH, "r") as f:
                    versions_data = json.load(f)
                    production_model = versions_data.get("production_model")
                    versions = versions_data.get("versions", [])
                    total_models = len(versions)
                    
                    # Get latest model accuracy
                    if versions:
                        latest_model_accuracy = versions[-1].get("score")
            except (json.JSONDecodeError, KeyError):
                pass  # Keep default values
        
        # Load prediction logs to count total predictions
        if os.path.exists(PREDICTIONS_LOG_PATH):
            try:
                with open(PREDICTIONS_LOG_PATH, "r") as f:
                    logs = json.load(f)
                    if isinstance(logs, list):
                        for log_entry in logs:
                            if "prediction" in log_entry:
                                total_predictions += 1
                            elif "predictions" in log_entry:
                                total_predictions += len(log_entry["predictions"])
            except (json.JSONDecodeError, KeyError):
                pass  # Keep default value
        
        return {
            "production_model": production_model,
            "total_models": total_models,
            "total_predictions": total_predictions,
            "latest_model_accuracy": latest_model_accuracy
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model dashboard analysis failed: {str(e)}")


@app.get("/platform-summary")
def platform_summary():
    """
    Return complete AutoML platform status including models, datasets,
    experiments, and predictions.
    """
    try:
        # Initialize counters
        production_model_name = None
        total_models = 0
        datasets_available = 0
        total_experiments = 0
        predictions_logged = 0
        
        # Check production model
        if os.path.exists(MODEL_PATH):
            if os.path.exists(METADATA_PATH):
                try:
                    with open(METADATA_PATH, "r") as f:
                        metadata = json.load(f)
                        production_model_name = metadata.get("model_name")
                except (json.JSONDecodeError, KeyError):
                    pass
        
        # Count model versions
        if os.path.exists(MODEL_VERSIONS_PATH):
            try:
                with open(MODEL_VERSIONS_PATH, "r") as f:
                    versions_data = json.load(f)
                    versions = versions_data.get("versions", [])
                    total_models = len(versions)
            except (json.JSONDecodeError, KeyError):
                pass
        
        # Count datasets
        if os.path.exists(DATASETS_PATH):
            try:
                dataset_files = [f for f in os.listdir(DATASETS_PATH) if f.endswith('.csv')]
                datasets_available = len(dataset_files)
            except (OSError, FileNotFoundError):
                pass
        
        # Count experiments (training runs)
        if os.path.exists(RUNS_PATH):
            try:
                run_dirs = [d for d in os.listdir(RUNS_PATH) if os.path.isdir(os.path.join(RUNS_PATH, d))]
                total_experiments = len(run_dirs)
            except (OSError, FileNotFoundError):
                pass
        
        # Count logged predictions
        if os.path.exists(PREDICTIONS_LOG_PATH):
            try:
                with open(PREDICTIONS_LOG_PATH, "r") as f:
                    logs = json.load(f)
                    if isinstance(logs, list):
                        for log_entry in logs:
                            if "prediction" in log_entry:
                                predictions_logged += 1
                            elif "predictions" in log_entry:
                                predictions_logged += len(log_entry["predictions"])
            except (json.JSONDecodeError, KeyError):
                pass
        
        # Determine platform status
        platform_status = "running" if production_model_name else "no_model_loaded"
        
        return {
            "platform_status": platform_status,
            "production_model": production_model_name,
            "total_models": total_models,
            "datasets_available": datasets_available,
            "total_experiments": total_experiments,
            "predictions_logged": predictions_logged
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Platform summary analysis failed: {str(e)}")


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """
    Serve the main dashboard page.
    """
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard", "index.html")
    try:
        with open(dashboard_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Dashboard not found</h1><p>Please ensure the dashboard files are present in the dashboard directory.</p>", 
            status_code=404
        )
