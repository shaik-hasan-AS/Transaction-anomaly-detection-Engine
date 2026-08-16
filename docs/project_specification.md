# SQL Rule-Based Transaction Anomaly Engine for Fraud Detection

## Detailed Project Specification and Implementation Plan

> **Project type:** Database + Backend + Machine Learning + Web
> Application\
> **Primary database:** PostgreSQL\
> **Backend:** FastAPI\
> **Frontend:** React\
> **ML:** Python, scikit-learn, optionally XGBoost\
> **Optional geospatial extension:** PostGIS

------------------------------------------------------------------------

# 1. Project Overview

The **SQL Rule-Based Transaction Anomaly Engine for Fraud Detection** is
a hybrid fraud-risk detection application built around PostgreSQL.

The system receives transaction records, analyzes transaction behavior
using advanced SQL techniques, identifies suspicious patterns using
deterministic rules, generates behavioral features, and optionally
applies machine-learning models to produce an additional anomaly/fraud
risk score.

The final application combines:

1.  **PostgreSQL** for transaction storage and analytical processing.
2.  **SQL-based rule detection** for explainable fraud patterns.
3.  **Python machine learning** for learned anomaly detection.
4.  **FastAPI** as the application/backend layer.
5.  **React** as the user-facing dashboard.
6.  **Hybrid risk scoring** to combine SQL and ML signals.

The system should identify **potentially fraudulent or anomalous
transactions**, rather than claiming that every flagged transaction is
definitively fraudulent.

------------------------------------------------------------------------

# 2. Core Idea

The project can be summarized as:

``` text
Transaction Data
       |
       v
   PostgreSQL
       |
       v
SQL Feature Engineering
       |
       v
Rule-Based Fraud Engine
       |
       +-------------------+
       |                   |
       v                   v
 SQL Risk Score       ML Feature Set
                           |
                           v
                     ML Model
                           |
                           v
                      ML Score
                           |
             +-------------+
             |
             v
       Hybrid Risk Engine
             |
             v
       Final Risk Score
             |
             v
       FastAPI Backend
             |
             v
        React Dashboard
```

The important design principle is:

> **SQL provides explainable, deterministic detection, while ML provides
> learned anomaly detection.**

ML does not need to replace SQL.

------------------------------------------------------------------------

# 3. Problem Statement

Financial transaction systems process large numbers of transactions
every day. Fraudulent behavior can be difficult to detect because
individual fraudulent transactions may appear normal when viewed in
isolation.

Fraud often becomes visible only when transaction history and contextual
information are considered.

Examples include:

-   Many transactions occurring within a very short time.
-   A transaction whose value is dramatically different from an
    account's normal behavior.
-   Transactions occurring in geographically impossible locations within
    a short period.
-   A previously unseen device suddenly performing a transaction.
-   Several failed transactions followed by a successful high-value
    transaction.
-   A sudden change in merchant category or spending behavior.

The project addresses this problem by analyzing transactions
relationally and temporally using SQL and optionally augmenting the
detection process with machine learning.

------------------------------------------------------------------------

# 4. Project Objectives

## Primary Objectives

-   Design a relational database for transaction processing.
-   Store realistic transaction and account information.
-   Use advanced SQL analytical techniques.
-   Detect suspicious transaction behavior using rules.
-   Generate explainable fraud-risk scores.
-   Create machine-learning features from transaction behavior.
-   Apply anomaly-detection or classification models.
-   Combine SQL and ML results.
-   Provide a web-based fraud investigation dashboard.

## Technical Objectives

The project should demonstrate practical use of:

-   PostgreSQL
-   Common Table Expressions (CTEs)
-   Window functions
-   `LAG()`
-   `LEAD()`
-   `ROW_NUMBER()`
-   `COUNT() OVER()`
-   `AVG()`
-   `STDDEV()`
-   Time-window analysis
-   Statistical anomaly detection
-   Geospatial distance calculations
-   Feature engineering
-   Machine learning
-   REST APIs
-   Data visualization

------------------------------------------------------------------------

# 5. Proposed Technology Stack

## Database

### PostgreSQL

PostgreSQL is the primary database.

Responsibilities:

-   Store transaction data.
-   Store accounts and cards.
-   Store merchants.
-   Store device information.
-   Store geographical information.
-   Execute SQL analytics.
-   Generate fraud features.
-   Store rule results.
-   Store final risk scores.

### Optional: PostGIS

PostGIS can be used for geographical operations such as:

-   Distance between transactions.
-   Coordinate calculations.
-   Geographic proximity.
-   Spatial queries.

------------------------------------------------------------------------

# 6. Backend

## FastAPI

FastAPI acts as the application layer between the frontend and
database/ML components.

Example API endpoints:

``` text
GET  /transactions
GET  /transactions/{transaction_id}
GET  /suspicious
GET  /accounts/{account_id}/risk
GET  /analytics/summary
GET  /analytics/fraud-types
POST /detection/run
POST /transactions
```

Responsibilities:

-   Query PostgreSQL.
-   Trigger detection pipelines.
-   Execute ML predictions.
-   Return fraud results to the frontend.
-   Handle filtering and investigation requests.

------------------------------------------------------------------------

# 7. Frontend

## React

React provides the user-facing fraud investigation dashboard.

Possible pages:

### Dashboard

Shows:

-   Total transactions.
-   Suspicious transactions.
-   High-risk transactions.
-   Critical transactions.
-   Fraud/anomaly distribution.
-   Activity timeline.
-   Geographic patterns.

### Suspicious Transactions

Displays:

-   Transaction ID.
-   Account.
-   Amount.
-   Timestamp.
-   Location.
-   Risk score.
-   Triggered rules.
-   ML score.

### Transaction Investigation

Displays:

-   Full transaction information.
-   Previous transactions.
-   Account history.
-   Triggered SQL rules.
-   ML prediction.
-   Risk explanation.

### Analytics

Charts for:

-   Transactions over time.
-   Suspicious transactions over time.
-   Fraud types.
-   High-risk accounts.
-   High-risk merchants.
-   Geographic anomalies.

------------------------------------------------------------------------

# 8. Database Design

A possible relational schema is:

``` text
customers
    |
    +---- accounts
              |
              +---- cards
              |
              +---- transactions
                         |
                         +---- merchants
                         |
                         +---- devices
```

------------------------------------------------------------------------

# 9. Tables

## 9.1 Customers

``` text
customers
---------
customer_id       PK
name
country
created_at
```

Purpose:

Stores customer-level information.

------------------------------------------------------------------------

## 9.2 Accounts

``` text
accounts
--------
account_id        PK
customer_id       FK
account_type
created_at
status
```

Relationships:

``` text
One customer
    |
    +---- many accounts
```

------------------------------------------------------------------------

## 9.3 Cards

``` text
cards
-----
card_id           PK
account_id        FK
card_type
created_at
status
```

A single account may have multiple cards.

------------------------------------------------------------------------

## 9.4 Merchants

``` text
merchants
---------
merchant_id       PK
merchant_name
category
latitude
longitude
country
```

Examples of merchant categories:

``` text
Food
Travel
Shopping
Electronics
Entertainment
Healthcare
Fuel
Jewelry
Online Services
```

------------------------------------------------------------------------

## 9.5 Devices

``` text
devices
-------
device_id         PK
device_type
operating_system
created_at
```

This allows detection of new or unusual devices.

------------------------------------------------------------------------

## 9.6 Transactions

This is the central table.

``` text
transactions
------------
transaction_id       PK
account_id            FK
card_id               FK
merchant_id           FK
device_id             FK

timestamp

amount
currency

latitude
longitude
country

ip_address
payment_method

status
```

Possible transaction statuses:

``` text
SUCCESS
FAILED
DECLINED
REVERSED
PENDING
```

------------------------------------------------------------------------

# 10. Why the Transaction Table Needs Context

A simple transaction table such as:

``` text
id
amount
date
```

would not be sufficient for the proposed project.

The system needs contextual data so that it can analyze:

-   Temporal behavior.
-   Spending behavior.
-   Geographic behavior.
-   Device behavior.
-   Merchant behavior.
-   Payment behavior.

The richer transaction structure enables meaningful feature engineering.

------------------------------------------------------------------------

# 11. Fraud Detection Rules

The initial version should implement three major fraud vectors.

## Rule 1: High-Velocity Card Testing

### Idea

Attackers may test stolen card information by performing many small
transactions in a short period.

Example:

``` text
10:00:01  ₹10
10:00:07  ₹20
10:00:13  ₹5
10:00:21  ₹15
10:00:28  ₹10
10:00:35  ₹25
```

Six transactions in approximately 35 seconds is suspicious.

### SQL concepts

Use:

-   Window functions.
-   Time ordering.
-   `COUNT() OVER()`.
-   CTEs.
-   Time intervals.

Example conceptual logic:

``` sql
COUNT(*) OVER (
    PARTITION BY card_id
    ORDER BY timestamp
    RANGE BETWEEN INTERVAL '2 minutes' PRECEDING
              AND CURRENT ROW
)
```

Then:

``` text
IF transaction_count > threshold
THEN velocity_flag = 1
```

The threshold should be configurable rather than hard-coded throughout
the application.

------------------------------------------------------------------------

# 12. Rule 2: Transaction Value Anomaly

A user's normal transaction amount can be used to detect unusually large
or small transactions.

For an account:

``` text
Average transaction = ₹900
Standard deviation = ₹500
Current transaction = ₹85,000
```

Calculate:

``` text
Z = (x - μ) / σ
```

where:

-   `x` = current transaction amount
-   `μ` = historical average
-   `σ` = historical standard deviation

Example:

``` sql
AVG(amount)
STDDEV(amount)
```

Then:

``` text
z_score = (amount - average_amount) / standard_deviation
```

Possible thresholds:

``` text
|Z| >= 2  -> moderate anomaly
|Z| >= 3  -> strong anomaly
|Z| >= 4  -> extreme anomaly
```

This rule detects account takeover or unusual spending behavior.

------------------------------------------------------------------------

# 13. Rule 3: Impossible Travel

The system compares consecutive transactions.

Example:

``` text
10:00 AM -> Chennai
10:20 AM -> London
```

The system calculates:

``` text
distance
time_difference
required_speed
```

Formula:

``` text
speed = distance / time
```

If the required travel speed is unrealistic, the transaction is flagged.

Example:

``` text
Distance = 8,000 km
Time = 20 minutes
Required speed ≈ 24,000 km/h
```

This is clearly suspicious.

### SQL requirements

The system needs:

``` text
previous latitude
previous longitude
previous timestamp
current latitude
current longitude
current timestamp
```

`LAG()` is useful for retrieving the previous transaction.

------------------------------------------------------------------------

# 14. Additional Rules

After implementing the three core rules, additional rules can improve
the project.

## Rule 4: New Device

If an account has historically used:

``` text
device_123
```

and suddenly uses:

``` text
device_987
```

the system can generate:

``` text
new_device = 1
```

This should be treated as a risk signal, not automatic proof of fraud.

------------------------------------------------------------------------

## Rule 5: New Location

If an account normally operates from one region and suddenly transacts
from a new country or distant region:

``` text
new_location = 1
```

This can contribute to the risk score.

------------------------------------------------------------------------

## Rule 6: Failed Transaction Burst

Example:

``` text
10:00 -> FAILED
10:01 -> FAILED
10:01 -> FAILED
10:02 -> FAILED
10:03 -> SUCCESS ₹80,000
```

This sequence can be suspicious.

The SQL engine can detect a high number of failed transactions followed
by a successful transaction within a time window.

------------------------------------------------------------------------

## Rule 7: Merchant Category Anomaly

If an account normally uses:

``` text
Food
Transport
Shopping
```

and suddenly performs a large transaction at:

``` text
Luxury Jewelry
```

the category change can become an anomaly feature.

------------------------------------------------------------------------

# 15. Rule-Based Risk Scoring

Instead of simply producing:

``` text
fraud = TRUE/FALSE
```

the system should produce a risk score.

Example:

  Rule                         Score
  -------------------------- -------
  High velocity                   25
  Amount anomaly                  25
  Impossible travel               30
  New device                      10
  New location                    10
  Failed transaction burst        15

The final score can be calculated as:

``` text
risk_score = sum(triggered_rule_scores)
```

The score can be capped at 100.

Example:

``` text
Velocity            +25
Amount anomaly      +25
New device          +10
Impossible travel   +30
------------------------
Risk Score           90
```

------------------------------------------------------------------------

# 16. Risk Categories

Example:

``` text
0 - 29    LOW
30 - 59   MEDIUM
60 - 79   HIGH
80 - 100  CRITICAL
```

These thresholds should be configurable.

------------------------------------------------------------------------

# 17. Explainability

One of the biggest advantages of the SQL rule engine is explainability.

Instead of simply displaying:

``` text
Risk = 93
```

the system should explain:

``` text
Risk Score: 93

Triggered Rules:
✓ High transaction velocity
✓ Unusual transaction amount
✓ New device
✓ Impossible geographical movement
```

This makes the system easier to understand and defend during a project
demonstration.

------------------------------------------------------------------------

# 18. SQL Feature Engineering

The SQL layer should not only flag transactions.

It should create a reusable **feature dataset**.

Example:

``` text
transaction_id
account_id
amount
account_avg_amount
account_std_amount
z_score
velocity_count
time_since_previous
distance_from_previous
required_travel_speed
new_device
new_location
failed_attempt_count
merchant_frequency
merchant_category_frequency
```

These features can be stored in a table or exposed through a view.

Example:

``` text
transaction_features
--------------------
transaction_id
account_id
amount
velocity_count
z_score
distance_km
time_since_previous
travel_speed
new_device
new_location
failed_attempts
```

This feature table becomes the bridge between PostgreSQL and the ML
layer.

------------------------------------------------------------------------

# 19. Machine Learning Layer

Machine learning is an optional but recommended extension.

The ML model should not replace the SQL rule engine.

Instead:

``` text
SQL Rules
    +
ML
    =
Hybrid Fraud Detection
```

------------------------------------------------------------------------

# 20. ML Approach 1: Unsupervised Anomaly Detection

This approach is useful when labelled fraud data is unavailable.

Recommended first model:

## Isolation Forest

Isolation Forest attempts to identify observations that are unusual
compared with the rest of the dataset.

Input features can include:

``` text
amount
velocity_count
z_score
distance_from_previous
time_since_previous
travel_speed
new_device
new_location
failed_attempt_count
merchant_frequency
```

Output:

``` text
anomaly_score
```

This is useful because real-world fraud datasets may not always contain
reliable labels.

------------------------------------------------------------------------

# 21. ML Approach 2: Supervised Classification

If the project dataset contains a known fraud label:

``` text
is_fraud
```

then supervised machine learning can be used.

Example:

``` text
0 = legitimate
1 = fraudulent
```

Potential models:

-   Logistic Regression
-   Random Forest
-   XGBoost
-   LightGBM

Recommended project models:

``` text
Random Forest
XGBoost
```

XGBoost can be included as an advanced comparison model.

------------------------------------------------------------------------

# 22. Creating Ground-Truth Data

A major advantage of this project is that a synthetic transaction
generator can intentionally inject fraud patterns.

Generate normal transactions:

``` text
Normal amounts
Normal locations
Normal transaction frequencies
Normal devices
Normal merchant categories
```

Then inject known fraud:

``` text
Velocity attacks
Large amount anomalies
Impossible travel
New device attacks
Failed transaction bursts
```

The generator can label injected transactions:

``` text
is_fraud = 1
```

and normal transactions:

``` text
is_fraud = 0
```

This provides ground-truth labels for supervised ML.

------------------------------------------------------------------------

# 23. Class Imbalance

Fraud is normally much less common than legitimate activity.

Example:

``` text
1,000,000 transactions
999,000 legitimate
1,000 fraud
```

Fraud rate:

``` text
0.1%
```

A model that predicts everything as legitimate could achieve 99.9%
accuracy while being useless.

Therefore, do not rely primarily on accuracy.

Use:

-   Precision
-   Recall
-   F1-score
-   ROC-AUC
-   PR-AUC
-   Confusion matrix

For fraud detection, precision and recall are especially important.

------------------------------------------------------------------------

# 24. Hybrid SQL + ML Architecture

The recommended architecture is:

``` text
                  TRANSACTIONS
                       |
                       v
                 PostgreSQL
                       |
                       v
              SQL Feature Engine
                       |
          +------------+------------+
          |                         |
          v                         v
     Rule Engine              Feature Dataset
          |                         |
          v                         v
     SQL Risk Score             ML Model
                                    |
                                    v
                              ML Risk Score
                                    |
                    +---------------+
                    |
                    v
              Hybrid Scoring
                    |
                    v
              Final Risk Score
                    |
                    v
               FastAPI API
                    |
                    v
                React App
```

------------------------------------------------------------------------

# 25. Combining SQL and ML Scores

Suppose:

``` text
SQL score = 75
ML probability = 0.91
```

Convert ML probability to a 0-100 score:

``` text
ML score = 91
```

Then:

``` text
final_score =
    0.6 * SQL_score +
    0.4 * ML_score
```

Therefore:

``` text
final_score =
    0.6 * 75 +
    0.4 * 91

= 81.4
```

Final classification:

``` text
CRITICAL
```

The weights should be experimentally evaluated.

------------------------------------------------------------------------

# 26. Alternative Hybrid Strategy

Instead of manually weighting the scores, the ML model can receive the
SQL rule outputs as features.

Example:

``` text
velocity_flag
amount_anomaly_flag
travel_flag
new_device_flag
new_location_flag
failed_attempt_flag
```

The ML model can then learn combinations of these signals.

For example:

``` text
amount anomaly
+
new device
+
high velocity
```

may be substantially more suspicious together than individually.

This is a strong extension for the project.

------------------------------------------------------------------------

# 27. Application Architecture

The final application should have four major layers.

``` text
┌─────────────────────────────────────┐
│              React UI               │
│                                     │
│ Dashboard | Alerts | Investigation │
└──────────────────┬──────────────────┘
                   |
                   v
┌─────────────────────────────────────┐
│             FastAPI                 │
│                                     │
│ REST APIs                           │
│ Authentication                      │
│ Detection triggers                  │
│ ML prediction calls                 │
└──────────────────┬──────────────────┘
                   |
          +--------+--------+
          |                 |
          v                 v
┌─────────────────┐  ┌─────────────────┐
│   PostgreSQL    │  │  Python ML      │
│                 │  │                 │
│ Transactions    │  │ sklearn         │
│ SQL rules       │  │ XGBoost         │
│ Features        │  │ Models          │
│ Risk results    │  │ Predictions     │
└─────────────────┘  └─────────────────┘
```

------------------------------------------------------------------------

# 28. Application Responsibilities

## PostgreSQL

PostgreSQL should be responsible for:

-   Data persistence.
-   Relational integrity.
-   SQL analytics.
-   Window functions.
-   CTE-based feature generation.
-   Statistical calculations.
-   Rule evaluation.
-   Storing detection results.

## Python

Python should be responsible for:

-   Data loading.
-   ML training.
-   ML inference.
-   Model evaluation.
-   Model persistence.
-   Optional synthetic data generation.

## FastAPI

FastAPI should be responsible for:

-   Exposing APIs.
-   Calling SQL queries.
-   Calling ML inference.
-   Returning JSON responses.
-   Triggering detection jobs.

## React

React should be responsible for:

-   Displaying data.
-   Filtering transactions.
-   Showing risk information.
-   Rendering charts.
-   Investigating transactions.

------------------------------------------------------------------------

# 29. Suggested Project Directory

``` text
fraud-detection-engine/
│
├── database/
│   ├── schema.sql
│   ├── seed.sql
│   ├── indexes.sql
│   └── views.sql
│
├── sql/
│   ├── velocity_detection.sql
│   ├── amount_anomaly.sql
│   ├── impossible_travel.sql
│   ├── device_anomaly.sql
│   ├── location_anomaly.sql
│   ├── failed_attempts.sql
│   ├── merchant_anomaly.sql
│   └── feature_engineering.sql
│
├── data/
│   ├── raw/
│   └── generated/
│
├── ml/
│   ├── generate_data.py
│   ├── feature_loader.py
│   ├── train_isolation_forest.py
│   ├── train_classifier.py
│   ├── evaluate.py
│   └── models/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── routes/
│   │   ├── transactions.py
│   │   ├── analytics.py
│   │   └── detection.py
│   └── services/
│       ├── fraud_engine.py
│       └── ml_service.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── charts/
│   └── package.json
│
├── docker-compose.yml
├── requirements.txt
└── README.md
```

------------------------------------------------------------------------

# 30. Development Phases

## Phase 1 --- Project Setup

Tasks:

-   Create Git repository.
-   Create PostgreSQL database.
-   Create project directory.
-   Configure Python environment.
-   Configure FastAPI.
-   Configure React.
-   Establish database connection.

Deliverable:

``` text
Working PostgreSQL + FastAPI + React skeleton
```

------------------------------------------------------------------------

# 31. Phase 2 --- Database Design

Tasks:

-   Design ER diagram.
-   Create tables.
-   Define primary keys.
-   Define foreign keys.
-   Add constraints.
-   Add indexes.

Deliverables:

``` text
ER Diagram
schema.sql
indexes.sql
```

------------------------------------------------------------------------

# 32. Phase 3 --- Transaction Data Generation

Create realistic transaction data.

Generate:

-   Customers.
-   Accounts.
-   Cards.
-   Merchants.
-   Devices.
-   Transactions.

Then inject known anomalies.

Deliverable:

``` text
Realistic transaction dataset
```

------------------------------------------------------------------------

# 33. Phase 4 --- SQL Analytics

Implement advanced SQL.

Topics:

-   CTEs.
-   Window functions.
-   Aggregations.
-   `LAG()`.
-   `LEAD()`.
-   `ROW_NUMBER()`.
-   Rolling counts.
-   Time-window calculations.
-   Statistical aggregation.

Deliverable:

``` text
SQL feature-engineering layer
```

------------------------------------------------------------------------

# 34. Phase 5 --- Core Fraud Rules

Implement:

``` text
1. High velocity
2. Transaction value anomaly
3. Impossible travel
```

Verify each rule against known injected fraud transactions.

Deliverable:

``` text
Explainable rule engine
```

------------------------------------------------------------------------

# 35. Phase 6 --- Advanced Rules

Implement:

``` text
4. New device
5. New location
6. Failed transaction burst
7. Merchant/category anomaly
```

Deliverable:

``` text
Expanded rule engine
```

------------------------------------------------------------------------

# 36. Phase 7 --- Risk Scoring

Create:

``` text
rule_scores
risk_score
risk_level
triggered_rules
```

Example:

``` text
transaction_id = TX1001

risk_score = 85

triggered_rules =
[
    "HIGH_VELOCITY",
    "AMOUNT_ANOMALY",
    "NEW_DEVICE"
]

risk_level = "CRITICAL"
```

------------------------------------------------------------------------

# 37. Phase 8 --- ML

Start with:

``` text
Isolation Forest
```

Then optionally add:

``` text
Random Forest
XGBoost
```

Train using SQL-generated features.

Evaluate using suitable metrics.

Deliverables:

``` text
Trained model
Evaluation report
Feature importance / anomaly analysis
```

------------------------------------------------------------------------

# 38. Phase 9 --- Hybrid Detection

Combine:

``` text
SQL risk
+
ML risk
```

Generate:

``` text
final_risk_score
final_risk_level
```

Also preserve the individual scores for explainability.

Example:

``` text
SQL Score:       82
ML Score:        91
Final Score:     86
Risk Level:      CRITICAL
```

------------------------------------------------------------------------

# 39. Phase 10 --- FastAPI

Implement API endpoints.

Example:

``` text
GET /transactions
GET /transactions/{id}
GET /suspicious
GET /accounts/{id}/risk
GET /analytics/summary
GET /analytics/fraud-types
POST /detection/run
```

Deliverable:

``` text
Working backend API
```

------------------------------------------------------------------------

# 40. Phase 11 --- React Dashboard

Build:

### Dashboard

-   Summary cards.
-   Fraud timeline.
-   Risk distribution.
-   Fraud type distribution.

### Transaction page

-   Search.
-   Filters.
-   Sorting.
-   Risk score.

### Investigation page

-   Transaction details.
-   Account history.
-   Rule explanations.
-   ML result.

Deliverable:

``` text
Working fraud detection web application
```

------------------------------------------------------------------------

# 41. Phase 12 --- Testing

Test individual rules.

Example test:

``` text
Input:
10 transactions within 1 minute

Expected:
HIGH_VELOCITY = TRUE
```

Another:

``` text
Input:
₹500 normal transaction
₹80,000 abnormal transaction

Expected:
AMOUNT_ANOMALY = TRUE
```

Another:

``` text
Input:
Chennai -> London within 15 minutes

Expected:
IMPOSSIBLE_TRAVEL = TRUE
```

ML tests should also evaluate false positives and false negatives.

------------------------------------------------------------------------

# 42. Phase 13 --- Performance Optimization

Once the system works:

-   Add indexes.
-   Analyze query plans.
-   Reduce unnecessary joins.
-   Use materialized views if appropriate.
-   Optimize rolling-window queries.
-   Batch ML inference.
-   Avoid running expensive detection unnecessarily.

Potential indexes:

``` text
transactions(account_id, timestamp)
transactions(card_id, timestamp)
transactions(device_id)
transactions(merchant_id)
transactions(timestamp)
```

The exact indexes should be validated using query plans rather than
added blindly.

------------------------------------------------------------------------

# 43. Example End-to-End Flow

Suppose this transaction arrives:

``` text
Transaction ID: TX98231

Account: ACC1023
Amount: ₹84,500

Location: London
Device: DEV882

Timestamp: 10:51 AM
```

Previous transaction:

``` text
Account: ACC1023
Amount: ₹700

Location: Chennai
Device: DEV101

Timestamp: 10:32 AM
```

The SQL engine calculates:

``` text
Velocity:
4 transactions in 2 minutes
→ FLAG

Amount:
Account average = ₹850
Current = ₹84,500
Z-score = 6.4
→ FLAG

Device:
DEV882 never used before
→ FLAG

Travel:
Chennai → London in 19 minutes
→ FLAG
```

SQL score:

``` text
25 + 25 + 10 + 30 = 90
```

ML model:

``` text
Anomaly probability = 0.94
```

Final score:

``` text
0.6(90) + 0.4(94)
= 91.6
```

Result:

``` text
CRITICAL
```

The dashboard displays the transaction and all reasons.

------------------------------------------------------------------------

# 44. Dashboard Concept

Example:

``` text
┌───────────────────────────────────────────────┐
│          FRAUD DETECTION ENGINE               │
├──────────────┬──────────────┬─────────────────┤
│ Transactions │ Suspicious   │ Critical        │
│   125,420    │    1,284     │     147         │
├──────────────┴──────────────┴─────────────────┤
│                                               │
│             Transaction Activity              │
│                                               │
│       █                                       │
│   █   █       █                               │
│ █ █ █ █ █ █ █ █ █                             │
│                                               │
├──────────────────────┬────────────────────────┤
│ Fraud Signals        │ High Risk Accounts     │
│                      │                        │
│ Amount       41%     │ ACC1023       97       │
│ Velocity     32%     │ ACC8821       94       │
│ Travel       18%     │ ACC5512       91       │
│ Other         9%     │ ACC9912       88       │
└──────────────────────┴────────────────────────┘
```

------------------------------------------------------------------------

# 45. Transaction Investigation View

When the user clicks a transaction:

``` text
Transaction: TX98231
Account: ACC1023
Amount: ₹84,500
Timestamp: 10:51 AM

FINAL RISK
91.6 / 100
CRITICAL

SQL RULES
--------------------------------
✓ High transaction velocity
✓ Amount anomaly
✓ New device
✓ Impossible travel

SQL SCORE
90 / 100

ML
--------------------------------
Anomaly Score: 0.94

ACCOUNT HISTORY
--------------------------------
Average amount: ₹850
Usual location: Chennai
Usual device: DEV101

TRAVEL ANALYSIS
--------------------------------
Previous location: Chennai
Current location: London
Time difference: 19 minutes
Required speed: unrealistic

RECOMMENDATION
--------------------------------
Transaction requires investigation.
```

------------------------------------------------------------------------

# 46. Why This Is a Strong Academic Project

The project demonstrates several database concepts in one practical
system.

## Database concepts

-   Relational modeling.
-   Primary/foreign keys.
-   Constraints.
-   Indexing.
-   Complex SQL.
-   CTEs.
-   Window functions.
-   Aggregation.
-   Views.

## Analytics concepts

-   Statistical anomaly detection.
-   Time-series behavior.
-   Rolling windows.
-   Geographic analysis.
-   Feature engineering.

## Machine learning concepts

-   Unsupervised anomaly detection.
-   Supervised classification.
-   Class imbalance.
-   Model evaluation.
-   Feature importance.
-   Risk scoring.

## Software engineering

-   REST API.
-   Backend/frontend separation.
-   Database integration.
-   Modular architecture.
-   Testing.
-   Deployment.

------------------------------------------------------------------------

# 47. Recommended Scope

Do not attempt to build everything at once.

## Minimum viable project

Implement:

``` text
PostgreSQL
    +
3 SQL fraud rules
    +
Risk scoring
    +
Simple dashboard
```

This is already a complete project.

## Strong version

Add:

``` text
Additional SQL rules
    +
Synthetic fraud generator
    +
Isolation Forest
    +
FastAPI
    +
React dashboard
```

## Advanced version

Add:

``` text
XGBoost
    +
Hybrid ML/rule scoring
    +
PostGIS
    +
Real-time transaction simulation
    +
Alert system
    +
Performance benchmarking
```

------------------------------------------------------------------------

# 48. Recommended Final Scope

For a college project, the ideal target is:

``` text
PostgreSQL
        |
        +-- SQL Rule Engine
        |      |
        |      +-- Velocity
        |      +-- Z-score
        |      +-- Impossible Travel
        |      +-- New Device
        |      +-- New Location
        |      +-- Failed Attempts
        |
        +-- Feature Engineering
               |
               v
         Python ML
               |
       Isolation Forest
               |
               v
       Hybrid Risk Engine
               |
               v
            FastAPI
               |
               v
             React
```

This is ambitious enough to be impressive while still being realistic to
implement.

------------------------------------------------------------------------

# 49. Key Design Principle

The most important design decision is:

> **Do not make the project "SQL versus ML." Make it "SQL + ML."**

SQL is excellent at:

-   Explicit rules.
-   Relational patterns.
-   Temporal windows.
-   Explainability.
-   Statistical calculations.

ML is excellent at:

-   Learning combinations of features.
-   Detecting complex patterns.
-   Generalizing beyond manually written rules.
-   Producing anomaly/risk probabilities.

Together they provide:

``` text
Explainability
+
Statistical analysis
+
Machine learning
+
Application interface
=
Hybrid Fraud Detection Platform
```

------------------------------------------------------------------------

# 50. Final Project Description

The project can ultimately be described as:

> **The SQL Rule-Based Transaction Anomaly Engine is a hybrid fraud-risk
> detection platform that analyzes transactional behavior using
> PostgreSQL-based analytical techniques and machine learning. The
> system processes relational transaction data using Common Table
> Expressions, window functions, statistical aggregation, temporal
> analysis, and geospatial calculations to identify suspicious patterns
> such as high-velocity card testing, transaction-value anomalies, and
> impossible geographical movement. The SQL engine produces explainable
> rule-based risk scores and behavioral features, which can be further
> analyzed by machine-learning models such as Isolation Forest or
> XGBoost. A hybrid scoring layer combines deterministic SQL signals
> with ML-generated anomaly scores, while a FastAPI backend and React
> dashboard provide transaction investigation, analytics, and risk
> visualization capabilities.**

------------------------------------------------------------------------

# 51. Final Architecture

``` text
                         ┌───────────────────────┐
                         │     React Frontend    │
                         │                       │
                         │ Dashboard             │
                         │ Transactions          │
                         │ Investigation         │
                         │ Analytics             │
                         └───────────┬───────────┘
                                     │
                                     │ REST API
                                     ▼
                         ┌───────────────────────┐
                         │       FastAPI         │
                         │                       │
                         │ API Layer             │
                         │ Detection Control     │
                         │ ML Inference          │
                         └───────────┬───────────┘
                                     │
                       ┌─────────────┴─────────────┐
                       │                           │
                       ▼                           ▼
             ┌───────────────────┐       ┌──────────────────┐
             │    PostgreSQL     │       │   Python ML      │
             │                   │       │                  │
             │ Transactions      │       │ scikit-learn     │
             │ Accounts          │       │ Isolation Forest │
             │ Cards             │       │ XGBoost          │
             │ Merchants         │       │                  │
             │ Devices           │       │ Models           │
             │                   │       │ Predictions      │
             │ SQL Analytics     │       │                  │
             │ CTEs              │       └────────┬─────────┘
             │ Window Functions  │                │
             │ Statistics        │                │
             └─────────┬─────────┘                │
                       │                          │
                       ▼                          │
             ┌───────────────────┐                │
             │ SQL Feature       │◄───────────────┘
             │ Engineering       │
             └─────────┬─────────┘
                       │
                       ▼
             ┌───────────────────┐
             │ Rule-Based Engine │
             │                   │
             │ Velocity          │
             │ Amount Anomaly    │
             │ Travel             │
             │ Device             │
             │ Location           │
             │ Failed Attempts   │
             └─────────┬─────────┘
                       │
                       ▼
             ┌───────────────────┐
             │ Hybrid Risk       │
             │ Scoring            │
             └─────────┬─────────┘
                       │
                       ▼
             ┌───────────────────┐
             │ Final Risk Result │
             │                   │
             │ Score             │
             │ Level             │
             │ Reasons           │
             └───────────────────┘
```

------------------------------------------------------------------------

# 52. Implementation Order

The actual development sequence should be:

``` text
1. PostgreSQL setup
        ↓
2. Database schema
        ↓
3. Synthetic transaction generator
        ↓
4. Insert transaction data
        ↓
5. Implement velocity SQL
        ↓
6. Implement amount anomaly SQL
        ↓
7. Implement impossible travel SQL
        ↓
8. Build SQL feature table/view
        ↓
9. Build rule-based risk scoring
        ↓
10. Validate rules
        ↓
11. Build ML dataset
        ↓
12. Train Isolation Forest
        ↓
13. Train supervised model if labels exist
        ↓
14. Compare SQL vs ML vs Hybrid
        ↓
15. Build FastAPI
        ↓
16. Build React dashboard
        ↓
17. Add investigation page
        ↓
18. Test entire pipeline
        ↓
19. Optimize PostgreSQL queries
        ↓
20. Document results
```

The **first implementation milestone** should therefore be PostgreSQL +
schema + synthetic transaction data. Once that works, the SQL fraud
engine can be built on top of the actual data.
