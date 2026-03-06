import ollama

def ml_planner(task):
    """Generate ML-specific implementation plan."""
    response = ollama.chat(
        model="llama3:8b",
        messages=[
            {
                "role": "user",
                "content": f"""You are a senior ML engineer.

ML TASK: {task}

Create a MINIMAL technical plan for a fast ML pipeline (must complete in <30 seconds).

CONSTRAINTS:
- Use iris or digits dataset (builtin, no loading delays)
- Train ONLY 2 models: RandomForest and LogisticRegression
- NO hyperparameter tuning (use defaults only)
- Use 5-fold cross-validation only (no train/test split overhead)
- NO GridSearchCV or RandomSearchCV
- NO feature engineering
- NO data preprocessing beyond what sklearn requires
- Keep it simple and fast

PLAN MUST INCLUDE:
- Dataset choice (iris or digits)
- 2 models (RF, LR)
- Metrics to track (accuracy)
- 5-fold CV approach
- Expected runtime (<30s)

Keep it SHORT and PRACTICAL."""
            }
        ]
    )
    return response['message']['content'].strip()


def ml_coder(plan):
    """Generate complete ML pipeline code - EXACT RAW CODE ONLY."""
    response = ollama.chat(
        model="deepseek-coder:6.7b",
        messages=[
            {
                "role": "user",
                "content": """Generate ONLY raw Python code. NO markdown. NO backticks. NO explanations. NO comments.

from sklearn.datasets import load_iris
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import joblib
import numpy as np

X, y = load_iris(return_X_y=True)

rf = RandomForestClassifier(n_estimators=50, random_state=42)
rf_scores = cross_val_score(rf, X, y, cv=5, scoring='accuracy')
rf_mean = np.mean(rf_scores)

lr = LogisticRegression(max_iter=200, random_state=42)
lr_scores = cross_val_score(lr, X, y, cv=5, scoring='accuracy')
lr_mean = np.mean(lr_scores)

print("RandomForest Mean Accuracy: {:.4f}".format(rf_mean))
print("LogisticRegression Mean Accuracy: {:.4f}".format(lr_mean))

if rf_mean > lr_mean:
    best_model_name = "RandomForest"
    best_model = RandomForestClassifier(n_estimators=50, random_state=42)
else:
    best_model_name = "LogisticRegression"
    best_model = LogisticRegression(max_iter=200, random_state=42)

best_model.fit(X, y)
joblib.dump(best_model, "best_model.pkl")
print("Best Model: {}".format(best_model_name))"""
            }
        ]
    )
    return response['message']['content'].strip()


def ml_debugger(code, error_msg):
    """Fix ML code with full context."""
    response = ollama.chat(
        model="phi3",
        messages=[
            {
                "role": "user",
                "content": f"""You are an expert ML Python debugger. Return ONLY raw Python code. NO markdown. NO backticks. NO explanations.

BROKEN CODE:
{code}

ERROR:
{error_msg}

FIX IT. Return ONLY raw Python code:"""
            }
        ]
    )
    return response['message']['content'].strip()
