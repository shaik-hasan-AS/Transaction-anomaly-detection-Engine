-- This view generates the base features and risk scores for all transactions.

CREATE OR REPLACE VIEW transaction_features AS
WITH base_metrics AS (
    SELECT 
        t.transaction_id,
        t.account_id,
        t.card_id,
        t.merchant_id,
        t.device_id,
        t.timestamp,
        t.amount,
        t.latitude,
        t.longitude,
        t.country AS merchant_country,
        c.country AS customer_country,
        m.category AS merchant_category,
        
        -- Rule 1: High-Velocity Card Testing
        COUNT(*) OVER (
            PARTITION BY t.card_id 
            ORDER BY t.timestamp 
            RANGE BETWEEN INTERVAL '2 minutes' PRECEDING AND CURRENT ROW
        ) AS velocity_count,

        -- Micro-Charge Testing
        SUM(CASE WHEN t.amount < 2.00 THEN 1 ELSE 0 END) OVER (
            PARTITION BY t.card_id
            ORDER BY t.timestamp
            RANGE BETWEEN INTERVAL '24 hours' PRECEDING AND CURRENT ROW
        ) AS micro_charge_count,
        
        -- Historical metrics for Rule 2
        AVG(t.amount) OVER (
            PARTITION BY t.account_id
            ORDER BY t.timestamp
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS account_avg_amount,
        
        STDDEV(t.amount) OVER (
            PARTITION BY t.account_id
            ORDER BY t.timestamp
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS account_std_amount,
        
        -- Previous transaction metrics for Rule 3 & Category Hopping
        LAG(t.latitude) OVER w_card AS prev_latitude,
        LAG(t.longitude) OVER w_card AS prev_longitude,
        LAG(t.timestamp) OVER w_card AS prev_timestamp,
        LAG(m.category) OVER w_card AS prev_category,
        
        -- Previous device for Rule 4
        LAG(t.device_id) OVER w_account AS prev_device_id
        
    FROM transactions t
    JOIN accounts a ON t.account_id = a.account_id
    JOIN customers c ON a.customer_id = c.customer_id
    JOIN merchants m ON t.merchant_id = m.merchant_id
    WINDOW 
        w_card AS (PARTITION BY t.card_id ORDER BY t.timestamp),
        w_account AS (PARTITION BY t.account_id ORDER BY t.timestamp)
),
calculated_features AS (
    SELECT
        *,
        -- Z-Score for Value Anomaly
        CASE 
            WHEN account_std_amount > 0 THEN ABS(amount - account_avg_amount) / account_std_amount
            ELSE 0 
        END AS z_score,
        
        -- Distance in km (earthdistance returns meters)
        CASE 
            WHEN prev_latitude IS NOT NULL AND prev_longitude IS NOT NULL 
            THEN earth_distance(ll_to_earth(latitude, longitude), ll_to_earth(prev_latitude, prev_longitude)) / 1000.0
            ELSE 0
        END AS distance_km,
        
        -- Time difference in hours
        CASE 
            WHEN prev_timestamp IS NOT NULL 
            THEN EXTRACT(EPOCH FROM (timestamp - prev_timestamp)) / 3600.0
            ELSE NULL
        END AS time_diff_hours,
        
        -- New device flag
        CASE 
            WHEN prev_device_id IS NOT NULL AND device_id != prev_device_id THEN 1
            ELSE 0
        END AS new_device_flag,

        -- Category Change Flag
        CASE
            WHEN prev_category IS NOT NULL AND merchant_category != prev_category THEN 1
            ELSE 0
        END AS category_change_flag
        
    FROM base_metrics
),
risk_scoring AS (
    SELECT
        *,
        -- Travel speed (km/h)
        CASE 
            WHEN time_diff_hours > 0 THEN distance_km / time_diff_hours
            ELSE 0
        END AS travel_speed_kmh
    FROM calculated_features
)
SELECT 
    *,
    
    -- Evaluate rules (Boolean flags)
    velocity_count >= 5 AS rule_high_velocity,
    z_score >= 3.0 AS rule_amount_anomaly,
    travel_speed_kmh > 1000 AS rule_impossible_travel,
    new_device_flag = 1 AS rule_new_device,
    
    -- New Rules
    (merchant_country != customer_country) AS rule_foreign_transaction,
    (EXTRACT(HOUR FROM timestamp) BETWEEN 1 AND 5) AS rule_late_night,
    (micro_charge_count >= 3) AS rule_micro_testing,
    (category_change_flag = 1 AND time_diff_hours < 1.0) AS rule_rapid_category_hopping,
    
    -- Calculate Risk Score with finely-tuned realistic weights
    (
        CASE WHEN velocity_count >= 5 THEN 60 ELSE 0 END +
        CASE WHEN z_score >= 3.0 THEN 45 ELSE 0 END +
        CASE WHEN travel_speed_kmh > 1000 THEN 80 ELSE 0 END +
        CASE WHEN new_device_flag = 1 THEN 20 ELSE 0 END +
        CASE WHEN merchant_country != customer_country THEN 20 ELSE 0 END +
        CASE WHEN EXTRACT(HOUR FROM timestamp) BETWEEN 1 AND 5 THEN 15 ELSE 0 END +
        CASE WHEN micro_charge_count >= 3 THEN 40 ELSE 0 END +
        CASE WHEN category_change_flag = 1 AND time_diff_hours < 1.0 THEN 10 ELSE 0 END
    ) AS sql_risk_score

FROM risk_scoring;
