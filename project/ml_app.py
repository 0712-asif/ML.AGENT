from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import json
import os
from datetime import datetime

def check_production_model(models_dir):
    """Check if production model exists and return its accuracy."""
    metadata_path = os.path.join(models_dir, "model_metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        return metadata.get("test_accuracy"), metadata
    return None, None

def promote_model(models_dir, best_model, selected_model, test_accuracy, timestamp):
    """Promote model to production."""
    os.makedirs(models_dir, exist_ok=True)
    
    prod_model_path = os.path.join(models_dir, "production_model.pkl")
    joblib.dump(best_model, prod_model_path)
    
    metadata = {
        "model_name": selected_model,
        "test_accuracy": float(test_accuracy),
        "timestamp": timestamp
    }
    
    metadata_path = os.path.join(models_dir, "model_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)

X, y = load_iris(return_X_y=True)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

rf = RandomForestClassifier(random_state=42)
lr = LogisticRegression(max_iter=1000, random_state=42)

rf_train_cv_scores = cross_val_score(rf, X_train, y_train, cv=5)
lr_train_cv_scores = cross_val_score(lr, X_train, y_train, cv=5)

rf_train_cv_accuracy = rf_train_cv_scores.mean()
lr_train_cv_accuracy = lr_train_cv_scores.mean()

print("========================")
print("TRAIN CV PERFORMANCE")
print("========================")
print()
print(f"RandomForest Train CV Accuracy: {rf_train_cv_accuracy:.4f}")
print(f"LogisticRegression Train CV Accuracy: {lr_train_cv_accuracy:.4f}")
print()

if rf_train_cv_accuracy > lr_train_cv_accuracy:
    best_model = RandomForestClassifier(random_state=42)
    selected_model = "RandomForest"
else:
    best_model = LogisticRegression(max_iter=1000, random_state=42)
    selected_model = "LogisticRegression"

print(f"Selected Model: {selected_model}")
print()

best_model.fit(X_train, y_train)

y_test_pred = best_model.predict(X_test)
test_accuracy = accuracy_score(y_test, y_test_pred)

print("========================")
print("TEST PERFORMANCE")
print("========================")
print()
print(f"Test Accuracy: {test_accuracy:.4f}")
print()

class_report = classification_report(y_test, y_test_pred)
conf_matrix = confusion_matrix(y_test, y_test_pred)

print("========================")
print("CLASSIFICATION REPORT")
print("========================")
print()
print(class_report)

print("========================")
print("CONFUSION MATRIX")
print("========================")
print()
print(conf_matrix)
print()

runs_dir = os.path.join(os.getcwd(), "runs")
os.makedirs(runs_dir, exist_ok=True)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
exp_dir = os.path.join(runs_dir, timestamp)
os.makedirs(exp_dir, exist_ok=True)

model_path = os.path.join(exp_dir, "best_model.pkl")
joblib.dump(best_model, model_path)

train_cv_metrics = {
    "RandomForest_train_cv_accuracy": float(rf_train_cv_accuracy),
    "LogisticRegression_train_cv_accuracy": float(lr_train_cv_accuracy),
    "selected_model": selected_model
}

train_cv_path = os.path.join(exp_dir, "train_cv_metrics.json")
with open(train_cv_path, "w") as f:
    json.dump(train_cv_metrics, f, indent=4)

test_metrics = {
    "test_accuracy": float(test_accuracy),
    "model": selected_model
}

test_metrics_path = os.path.join(exp_dir, "test_metrics.json")
with open(test_metrics_path, "w") as f:
    json.dump(test_metrics, f, indent=4)

report_path = os.path.join(exp_dir, "classification_report.txt")
with open(report_path, "w") as f:
    f.write(class_report)

matrix_path = os.path.join(exp_dir, "confusion_matrix.txt")
with open(matrix_path, "w") as f:
    f.write(str(conf_matrix))

print("========================")
print("EXPERIMENT SAVED")
print("========================")
print(f"Location: {exp_dir}")
print()

models_dir = os.path.join(os.getcwd(), "models")
os.makedirs(models_dir, exist_ok=True)

production_accuracy, old_metadata = check_production_model(models_dir)

print("========================")
print("MODEL REGISTRY")
print("========================")
print()

if production_accuracy is None:
    promote_model(models_dir, best_model, selected_model, test_accuracy, timestamp)
    print("NEW MODEL PROMOTED TO PRODUCTION")
else:
    if test_accuracy > production_accuracy:
        promote_model(models_dir, best_model, selected_model, test_accuracy, timestamp)
        print("NEW MODEL PROMOTED TO PRODUCTION")
    else:
        print("CURRENT PRODUCTION MODEL RETAINED")

print()