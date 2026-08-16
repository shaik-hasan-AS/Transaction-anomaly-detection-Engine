# 🛡️ Hybrid Fraud Detection Engine

A production-ready, full-stack Transaction Anomaly Detection engine that combines the explainability of **Deterministic SQL Rules** with the probabilistic power of **Machine Learning**.

![Dashboard Preview](https://via.placeholder.com/1200x600.png?text=Fraud+Detection+Dashboard)

## 🚀 Features

- **Live Transaction Simulator**: Continuously generates realistic financial transactions in the background based on distinct customer behavioral profiles. Intentionally injects specific fraud vectors mixed with normal traffic.
- **Advanced SQL Detection Layer**: Uses PostgreSQL Window Functions and CTEs to evaluate complex fraud rules in real-time:
  - 🏃‍♂️ **High-Velocity Card Testing**: Detects rapid successive transactions.
  - 💸 **Value Anomalies**: Calculates a rolling Z-Score based on the user's historical spend.
  - ✈️ **Impossible Travel**: Calculates physical speed between consecutive transactions using the `earthdistance` extension to flag unrealistic movement.
  - 💳 **Micro-Charge Testing**: Identifies patterns of small authorizations often preceding large fraud.
  - 🌍 **Cross-Border Fraud**: Flags sudden shifts to foreign merchants.
  - 🌙 **Late-Night Anomalies**: Flags suspicious transactions occurring in the dead of night.
  - 🛒 **Rapid Category Hopping**: Detects sudden shifts in merchant category spending behavior.
- **9-Dimensional Machine Learning**: An unsupervised `IsolationForest` AI model trained on the SQL-engineered features. Calculates dynamic contamination thresholds to detect subtle, multi-variable fraud vectors that bypass rigid rules.
- **Premium React Dashboard**: A dark-mode, auto-refreshing investigation dashboard built with Vite, Tailwind CSS, and Recharts for live threat monitoring.

## 🏗️ Architecture

```mermaid
graph TD
    A[Data Generator Simulator] --> B[(PostgreSQL 15)]
    B --> C{SQL Rule Engine + Window Functions}
    C --> D[Deterministic Risk Score]
    C --> E[ML Isolation Forest]
    D --> F[Hybrid Scoring Engine]
    E --> F
    F --> G[FastAPI Backend]
    G --> H[React Dashboard]
```

## 🛠️ Quick Start (Docker)

This project is fully containerized. You do not need to install Python or Node locally to run it.

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/fraud-detection-engine.git
cd fraud-detection-engine
```

### 2. Start the Stack
Bring up the Database, FastAPI backend, and React frontend.
```bash
docker compose up --build -d
```

### 3. Seed the Database
Since the database starts empty, run the realistic data generator inside the backend container to simulate thousands of customers, merchants, and transactions.
```bash
docker compose exec backend python ../data/generate_data.py
```

### 4. Train the AI Model
Train the 9-dimensional Isolation Forest model on the dataset you just generated.
```bash
docker compose exec backend python ../ml/train_isolation_forest.py
```

### 5. Access the Dashboard
Navigate to [http://localhost:5173/](http://localhost:5173/) in your browser. 

The dashboard will populate with your freshly generated data! The live simulator will continue generating new transactions in the background every few seconds.

## 🧑‍💻 Manual Development Setup

If you prefer to run the components locally without Docker:

**1. Database**
```bash
docker compose up db -d
```

**2. Backend API**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python ../data/generate_data.py
python ../ml/train_isolation_forest.py
uvicorn main:app --reload
```

**3. Frontend**
```bash
cd frontend
npm install
npm run dev
```
