USE SCHEMA lab_db.lab_schema;
USE WAREHOUSE lab_wh;


-- Create time-series data for ML functions
CREATE OR REPLACE TABLE daily_sales (
    sale_date DATE,
    product_id INT,
    units_sold INT,
    revenue DECIMAL(10,2)
);

INSERT INTO daily_sales
SELECT
    DATEADD('day', SEQ4(), '2025-01-01')::DATE AS sale_date,
    MOD(SEQ4(), 4) + 1 AS product_id,
    GREATEST(5, FLOOR(UNIFORM(10, 100, RANDOM()) +
        10 * SIN(SEQ4() * 3.14159 / 30))) AS units_sold, -- seasonal pattern
    units_sold * (UNIFORM(10, 50, RANDOM())) AS revenue
FROM TABLE(GENERATOR(ROWCOUNT => 300));

-- Build a Forecasting Model (using only required columns to avoid exogenous features)
CREATE OR REPLACE VIEW daily_sales_forecast_input AS
SELECT sale_date, product_id, units_sold FROM daily_sales;

CREATE OR REPLACE SNOWFLAKE.ML.FORECAST sales_forecast_model(
    INPUT_DATA => SYSTEM$REFERENCE('VIEW', 'daily_sales_forecast_input'),
    SERIES_COLNAME => 'product_id',
    TIMESTAMP_COLNAME => 'sale_date',
    TARGET_COLNAME => 'units_sold'
);

-- Generate 30-day forecast
CALL sales_forecast_model!FORECAST(
    FORECASTING_PERIODS => 30,
    CONFIG_OBJECT => {'prediction_interval': 0.95}
);

-- View forecast results
SELECT * FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
ORDER BY TS;


-- Build an Anomaly Detection Model
CREATE OR REPLACE SNOWFLAKE.ML.ANOMALY_DETECTION sales_anomaly_model(
    INPUT_DATA => SYSTEM$REFERENCE('TABLE', 'daily_sales'),
    SERIES_COLNAME => 'product_id',
    TIMESTAMP_COLNAME => 'sale_date',
    TARGET_COLNAME => 'units_sold'
);

-- Detect anomalies in existing data
CALL sales_anomaly_model!DETECT_ANOMALIES(
    INPUT_DATA => SYSTEM$REFERENCE('TABLE', 'daily_sales'),
    SERIES_COLNAME => 'product_id',
    TIMESTAMP_COLNAME => 'sale_date',
    TARGET_COLNAME => 'units_sold',
    CONFIG_OBJECT => {'prediction_interval': 0.99}
);

SELECT * FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
WHERE IS_ANOMALY = TRUE
ORDER BY TS;