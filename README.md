# 🤖 ML.AGENT - Autonomous AI Engineer & Production AutoML Platform

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135.1-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F79A3E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.ai)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

A production-ready **Autonomous AI Coding & ML Agent** combined with an interactive **AutoML Web Operations Dashboard**. Built for automated machine learning workflows, self-healing code generation, model tuning, and web-based model deployment.

---

## 📑 Table of Contents

- [🌟 Key Highlights](#-key-highlights)
- [🏗️ System Architecture](#️-system-architecture)
- [🧠 Autonomous AI Agent System](#-autonomous-ai-agent-system)
- [📊 Production AutoML Platform & Dashboard](#-production-automl-platform--dashboard)
- [🚀 Quick Start Guide](#-quick-start-guide)
- [📁 Project Structure](#-project-structure)
- [📡 REST API Documentation](#-rest-api-documentation)
- [💻 CLI & Agent Usage](#-cli--agent-usage)
- [🛠️ Configuration & Environment](#️-configuration--environment)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🌟 Key Highlights

### 🧠 Autonomous Multi-LLM Agent Architecture
- **Self-Healing Code Loop**: Autonomous Planner → Coder → Sandbox Executor → Self-Debugging loop.
- **Local Ollama LLMs**: Powered by `Llama3 (8B)` for architecture planning, `DeepSeek-Coder (6.7B)` for precise code generation, and `Phi-3` for error diagnostics.
- **Sandboxed Execution Engine**: Automatically tests generated Python code non-interactively with runtime error capture and multi-iteration auto-repair.

### 🔥 Comprehensive AutoML Platform
- **Automated Model Training**: Trains and compares multiple algorithms (`RandomForest`, `LogisticRegression`, `LinearRegression`).
- **Hyperparameter Tuning**: Dynamic optimization via `GridSearchCV` with cross-validation.
- **Auto Task Detection**: Intelligent task classification (Classification vs. Regression).
- **Model Lifecycle & Registry**: Version-controlled model storage and active deployment tracking.

### 📊 Modern Web Dashboard
- **Interactive UI**: Real-time stats, prediction testing playground, dataset analytics, and model performance comparisons.
- **Explainable AI (XAI)**: Feature importance breakdown and performance metric charts.
- **Prediction Analytics**: Comprehensive history logs and batch inference capabilities.

---

## 🏗️ System Architecture

```
                                  ┌──────────────────────────────────────────────┐
                                  │           Autonomous AI Agent Loop           │
                                  │   (Planner -> Coder -> Sandbox -> Fix)       │
                                  └──────────────────────┬───────────────────────┘
                                                         │
                                                         ▼
┌────────────────────────────────┐       ┌────────────────────────────────┐       ┌────────────────────────────────┐
│         Web Dashboard          │       │         FastAPI Engine         │       │          AutoML Core           │
│   (HTML5 / CSS3 / Vanilla JS)  │ ◄───► │      (REST API Server)         │ ◄───► │   (Scikit-Learn / Pandas)     │
└────────────────────────────────┘       └────────────────────────────────┘       └────────────────────────────────┘
                                                         │                                        │
                                                         ▼                                        ▼
                                         ┌────────────────────────────────┐       ┌────────────────────────────────┐
                                         │         Model Registry         │       │       Prediction Analytics     │
                                         │       (best_model.pkl)         │       │         (metrics.json)         │
                                         └────────────────────────────────┘       └────────────────────────────────┘
```

---

## 🧠 Autonomous AI Agent System

The project features a standalone AI Engineer agent pipeline in the root directory that writes, tests, and fixes machine learning and general Python scripts independently:

| Agent Module | LLM Model | Role / Function |
|--------------|-----------|-----------------|
| **Planner** | `llama3:8b` | Analyzes task requirements and designs execution plans adhering to sandboxing constraints. |
| **Coder** | `deepseek-coder:6.7b` | Synthesizes executable single-file Python programs with sample data. |
| **Debugger** | `phi3` | Diagnoses runtime tracebacks/errors and outputs fixed code. |
| **Executor** | `executor.py` | Runs code in a isolated subprocess, evaluates return codes, and feeds failures back to Debugger. |

### Running the AI Agent Pipeline

```bash
# General AI Coding Agent
python main.py

# Machine Learning Specialized Agent Pipeline
python ml_main.py
```

---

## 📊 Production AutoML Platform & Dashboard

The platform includes a complete FastAPI application with an integrated dashboard in the `project/` directory.

### Core Capabilities
- **Dataset Ingestion**: Upload custom CSV datasets or test on standard datasets.
- **Automated Training**: Trigger multi-model cross-validation and hyperparameter optimization in 1 click.
- **Real-Time Predictions**: Test single inputs or batch payloads via UI form or API.
- **Model Performance Overview**: Detailed metrics (Accuracy, F1, R², MSE) compared visually.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python**: Version `3.8+` (Python 3.9-3.11 recommended)
- **Ollama**: (Optional for LLM Agent loop) [Download Ollama](https://ollama.ai)

### 2. Clone the Repository
```bash
git clone https://github.com/0712-asif/ML.AGENT.git
cd ML.AGENT
```

### 3. Setup Virtual Environment & Dependencies
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 4. Start the AutoML Dashboard Server
```bash
cd project
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Open Web Dashboard
Navigate to **`http://localhost:8000`** in your browser.

---

## 📁 Project Structure

```
ML.AGENT/
├── agents.py                 # Multi-LLM agents (Planner, Coder, Debugger)
├── ml_agent.py              # ML-specific agents & prompt templates
├── executor.py              # Code sandbox executor & debug loop runner
├── main.py                  # CLI runner for general code generation
├── ml_main.py               # CLI runner for ML pipeline generation
├── run_pipeline.py          # Quick execution helper
├── verify_setup.py          # Setup verification script
├── requirements.txt         # Project dependencies
├── Dockerfile               # Production container definition
├── DEPLOYMENT.md            # Cloud deployment guide
├── GIT_SETUP.md             # Git repository setup notes
├── LICENSE                  # MIT License
├── README.md                # Project documentation
│
└── project/                 # AutoML Web Application
    ├── api_server.py        # FastAPI server & REST API routes
    ├── ml_app.py            # AutoML training & tuning logic
    ├── best_model.pkl       # Serialized active production model
    ├── metrics.json         # Current model evaluation metrics
    ├── dashboard/           # Frontend Web Interface
    │   ├── index.html       # Web UI HTML markup
    │   ├── style.css        # Modern glassmorphism & responsive CSS
    │   └── script.js        # Interactive dashboard logic
    ├── datasets/            # Stored dataset uploads
    ├── models/              # Saved model versions
    └── logs/                # Prediction history logs
```

---

## 📡 REST API Documentation

The FastAPI application serves a comprehensive REST API. Interactive Swagger documentation is available at `http://localhost:8000/docs`.

### Core API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the web dashboard interface |
| `POST` | `/upload-dataset` | Uploads a CSV dataset for training |
| `POST` | `/train-uploaded-dataset` | Runs AutoML model comparison & tuning |
| `POST` | `/predict` | Evaluates a single prediction vector |
| `POST` | `/batch-predict` | Evaluates multiple prediction vectors |
| `GET` | `/model-info` | Returns information about active deployed model |
| `GET` | `/platform-summary` | Returns overall platform operational metrics |
| `GET` | `/model-performance` | Compares scores across trained models |
| `GET` | `/feature-importance` | Returns feature importance / weights |
| `GET` | `/dataset-info` | Metadata and columns of current dataset |

### Example Request (Single Prediction)

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

---

## 💻 CLI & Agent Usage

You can run setup checks and execute autonomous coding tasks directly from the command line:

### Verify Environment & Ollama LLMs
```bash
python verify_setup.py
```

### Run Autonomous Machine Learning Agent
```bash
python ml_main.py
```

### Docker Deployment
```bash
# Build Docker image
docker build -t ml-agent .

# Run container
docker run -p 8000:8000 ml-agent
```

---

## 🛠️ Configuration & Environment

You can configure the host and port settings using environment variables:

```bash
export AUTOML_HOST=0.0.0.0
export AUTOML_PORT=8000
export AUTOML_RELOAD=true
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
1. Fork the Project (`https://github.com/0712-asif/ML.AGENT/fork`)
2. Create your Feature Branch (`git checkout -b feature/AwesomeFeature`)
3. Commit your Changes (`git commit -m 'Add some AwesomeFeature'`)
4. Push to the Branch (`git push origin feature/AwesomeFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.

---

<p align="center">
  <b>Developed by <a href="https://github.com/0712-asif">0712-asif</a></b>
</p>