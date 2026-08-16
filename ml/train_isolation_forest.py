import pandas as pd
import psycopg2
from sklearn.ensemble import IsolationForest
import joblib
import os

DB_CONFIG = {
    "dbname": "fraud_db",
    "user": "fraud_user",
    "password": "fraud_password",
    "host": "localhost",
    "port": "5433"
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def main():
    print("Connecting to DB and loading features...")
    conn = get_db_connection()
    
    # Query features from the view
    query = """
    SELECT 
        transaction_id,
        amount,
        velocity_count,
        COALESCE(z_score, 0) as z_score,
        COALESCE(distance_km, 0) as distance_km,
        COALESCE(time_diff_hours, 0) as time_diff_hours,
        COALESCE(travel_speed_kmh, 0) as travel_speed_kmh,
        new_device_flag
    FROM transaction_features
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"Loaded {len(df)} transactions.")
    
    # Features to train on
    feature_cols = [
        'amount', 
        'velocity_count', 
        'z_score', 
        'travel_speed_kmh', 
        'new_device_flag'
    ]
    
    X = df[feature_cols]
    
    # Fill any remaining NaNs
    X = X.fillna(0)
    
    print("Training Isolation Forest model...")
    # contamination parameter estimates the proportion of outliers in the data
    model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
    model.fit(X)
    
    # Calculate anomaly scores (-1 for outliers, 1 for inliers)
    # The decision_function gives continuous scores where lower is more abnormal
    df['ml_anomaly_score'] = model.decision_function(X)
    
    print("Saving model to disk...")
    os.makedirs('ml/models', exist_ok=True)
    joblib.dump(model, 'ml/models/isolation_forest.joblib')
    
    print("Model trained and saved successfully.")

if __name__ == "__main__":
    main()
