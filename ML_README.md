# ML SPECIALIST AGENT - USAGE GUIDE

## Overview

The ML Specialist Agent is an autonomous machine learning pipeline generator.

It handles:
- ✅ Automatic model selection (RandomForest, XGBoost, Neural Networks)
- ✅ Hyperparameter tuning
- ✅ Cross-validation (5-fold+)
- ✅ Performance metrics
- ✅ Feature importance analysis
- ✅ Evaluation reports

## Usage

### Start ML Mode
```bash
python ml_main.py
```

### Example Tasks

#### Task 1: Stock Price Prediction
```
Build an ML model to predict stock prices using historical data and technical indicators
```

#### Task 2: Classification
```
Build a machine learning classifier for iris flower classification with cross-validation
```

#### Task 3: Time Series
```
Create a time series forecasting model for monthly sales data with train/test split
```

#### Task 4: Regression
```
Train multiple regression models to predict house prices from features
```

## What Happens

1. **ML PLANNING** - Generates technical architecture for ML pipeline
   - Data handling strategy
   - Model selection rationale
   - Hyperparameter ranges
   - Evaluation metrics

2. **ML PIPELINE GENERATION** - Creates full Python code
   - Auto-installs pandas, numpy, sklearn, xgboost
   - Generates/loads dataset
   - Trains 2-3 model variants
   - Runs cross-validation
   - Calculates metrics
   - Prints comparison reports

3. **ML TRAINING** - Executes with 60s timeout (allows for CV)
   - Longer timeout than regular scripts
   - Auto-retries on import errors
   - Debugging on failure

4. **RESULTS** - Displays model performance table
   - Accuracy/RMSE/F1/AUC
   - Feature importance
   - Model recommendations

## Auto-Routing

When you run `python main.py` with an ML-related task:
- System detects ML keywords
- Auto-suggests: "Run python ml_main.py instead"
- Provides better pipeline generation

## Advanced Features

### Custom Models
The agent can use:
- scikit-learn: DecisionTree, RandomForest, SVM, KNN
- XGBoost: Gradient boosting
- Neural Networks: MLP from sklearn
- Ensembles: Voting, Stacking

### Automatic Hyperparameter Tuning
Models include:
- GridSearchCV for small spaces
- RandomSearchCV for large spaces
- Default hyperparameter recommendations

### Metrics (Auto-Selected)
- Classification: Accuracy, F1, Precision, Recall, AUC-ROC
- Regression: RMSE, MAE, R²
- Cross-validation: Mean CV scores

### Report Generation
Automatic output includes:
```
Model Performance Summary:
============================
Model 1: RandomForest
  - CV Score: 0.92 (+/- 0.03)
  - Test Accuracy: 0.91

Model 2: XGBoost
  - CV Score: 0.94 (+/- 0.02)
  - Test Accuracy: 0.93

Recommended: XGBoost (Best performance)
```

## Limitations

Current constraints:
- ✓ No real-time streaming
- ✓ Limited to <60s execution
- ✓ Synthetic data or small datasets
- ✓ Single-machine training (no distributed)
- ✓ Classification and regression only (no clustering)

## Dependencies Auto-Installed

- pandas
- numpy
- scikit-learn
- xgboost
- (matplotlib/seaborn: if needed)

## Troubleshooting

**Problem:** "ModuleNotFoundError: No module named sklearn"
- Solution: Agent auto-installs, just retry

**Problem:** "Timeout after 60s"
- Task too complex for pipeline generation
- Try simpler dataset or fewer models

**Problem:** "Column selection error"
- Data format issue
- Check if task description is clear about features

## Next Steps

After ML Specialist works well, we can add:
- Deep learning (TensorFlow/PyTorch)
- AutoML integration (AutoSklearn)
- Hyperparameter optimization (Optuna)
- Feature engineering automation
- Time series forecasting specialization
