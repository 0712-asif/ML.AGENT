import os
import sys
import subprocess
from ml_agent import ml_planner, ml_coder, ml_debugger
from executor import create_file, run_python, auto_install_missing_module, detect_program_type, ML_EXECUTION_TIME

MAX_RETRIES = 3
ML_DEPS = ['numpy', 'pandas', 'scikit-learn', 'joblib']
DEFAULT_TASK = "Build a fast ML classifier using iris dataset with RandomForest and LogisticRegression models, perform 5-fold cross-validation, and save the best model"

def install_ml_dependencies():
    """Pre-install ML dependencies."""
    print("\n" + "="*60)
    print("Installing ML dependencies...")
    print("="*60)
    
    for dep in ML_DEPS:
        try:
            pip_name = dep
            if dep == 'scikit-learn':
                pip_name = 'scikit-learn'
            
            print(f"  Installing {pip_name}...", end=' ')
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-q', pip_name],
                timeout=60,
                capture_output=True
            )
            print("[OK]")
        except Exception as e:
            print("[WARN] (may already exist)")
    
    print("[OK] Dependencies ready\n")

print("\n" + "="*60)
print("AUTONOMOUS ML ENGINEERING AGENT")
print("="*60)

task = DEFAULT_TASK
print(f"\nML Task: {task}")

install_ml_dependencies()

print("\n" + "="*60)
print("STEP 1: ML PLANNING")
print("="*60)

try:
    plan = ml_planner(task)
    print("\nML Plan:\n")
    print(plan)
except Exception as e:
    print(f"ERROR: Planning failed - {e}")
    sys.exit(1)

print("\n" + "="*60)
print("STEP 2: ML PIPELINE GENERATION")
print("="*60)

try:
    code = ml_coder(plan)
    print("[OK] ML pipeline generated")
except Exception as e:
    print(f"ERROR: Code generation failed - {e}")
    sys.exit(1)

if 'rf_scores' not in code or 'cross_val_score' not in code or 'joblib' not in code:
    print("  [WARN] Generated code appears incomplete, using fallback template...")
    code = """from sklearn.datasets import load_iris
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import numpy as np
import json

X, y = load_iris(return_X_y=True)

rf = RandomForestClassifier(n_estimators=50, random_state=42)
rf_scores = cross_val_score(rf, X, y, cv=5)
rf_mean = rf_scores.mean()

lr = LogisticRegression(max_iter=200, random_state=42)
lr_scores = cross_val_score(lr, X, y, cv=5)
lr_mean = lr_scores.mean()

print("========================")
print("MODEL PERFORMANCE REPORT")
print("========================")
print()
print("RandomForest Mean Accuracy: {:.4f}".format(rf_mean))
print("LogisticRegression Mean Accuracy: {:.4f}".format(lr_mean))
print()

if rf_mean > lr_mean:
    best_model_name = "RandomForest"
    best_model = RandomForestClassifier(n_estimators=50, random_state=42)
else:
    best_model_name = "LogisticRegression"
    best_model = LogisticRegression(max_iter=200, random_state=42)

print("Best Model: {}".format(best_model_name))
print()

best_model.fit(X, y)
joblib.dump(best_model, "best_model.pkl")

y_pred = best_model.predict(X)
class_report = classification_report(y, y_pred)
conf_matrix = confusion_matrix(y, y_pred)

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

metrics = {
    "RandomForest_accuracy": float(rf_mean),
    "LogisticRegression_accuracy": float(lr_mean),
    "best_model": best_model_name
}

with open("metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)"""

project_dir = os.path.join(os.getcwd(), "project")
os.makedirs(project_dir, exist_ok=True)
file_path = os.path.join(project_dir, "ml_app.py")

if not create_file(file_path, code):
    print("ERROR: Code rejected before execution (syntax or safety check failed)")
    from executor import extract_python_code
    cleaned = extract_python_code(code)
    print(f"  Cleaned code length: {len(cleaned)} chars")
    print(f"  Preview: {cleaned[:200]}...")
    sys.exit(1)

print(f"[OK] ML pipeline saved to {file_path}")
print(f"\nGenerated code preview ({len(code)} chars):\n")
print(code[:300] + ("..." if len(code) > 300 else ""))
print()

attempt = 1
success = False

while attempt <= MAX_RETRIES and not success:
    print("\n" + "="*60)
    print(f"STEP 3: ML TRAINING (Attempt {attempt}/{MAX_RETRIES})")
    print("="*60)
    
    output, error = run_python(file_path, timeout=ML_EXECUTION_TIME)
    
    if error:
        print(f"\n[ERROR]:\n{error}")
        
        if auto_install_missing_module(error):
            print("[OK] Module installed, retrying...")
            attempt += 1
            continue
        
        if attempt < MAX_RETRIES:
            print("\n" + "="*60)
            print(f"STEP 4: DEBUGGING (Attempt {attempt})")
            print("="*60)
            
            try:
                print("Analyzing and fixing error...")
                fixed_code = ml_debugger(code, error)
                
                if not create_file(file_path, fixed_code):
                    print("ERROR: Fixed code failed validation")
                    break
                
                code = fixed_code
                print("[OK] Code fixed and saved")
            except Exception as e:
                print(f"ERROR: Debugging failed - {e}")
                break
        
        attempt += 1
    else:
        print("\n" + "="*60)
        print("STEP 5: ML RESULTS")
        print("="*60)
        print("\nPipeline Output:\n")
        print(output if output else "(No output produced)")
        success = True

print("\n" + "="*60)
if success:
    print("[OK] ML PIPELINE COMPLETED SUCCESSFULLY")
    print("="*60 + "\n")
    sys.exit(0)
else:
    print("[FAILED] ML PIPELINE FAILED")
    print("="*60 + "\n")
    sys.exit(1)

