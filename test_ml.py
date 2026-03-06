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
print("Best Model: {}".format(best_model_name))
