USE DATABASE DBT_TUTORIAL;

-- 1. Drop schemas created by custom schema configurations (if they exist)
DROP SCHEMA IF EXISTS RAW_STAGING;
DROP SCHEMA IF EXISTS RAW_INTERMEDIATE;
DROP SCHEMA IF EXISTS RAW_MARTS;

-- 2. Drop dbt models created directly in the RAW schema (from initial runs without custom schemas)
USE SCHEMA RAW;

-- Staging views
DROP VIEW IF EXISTS stg_customers;
DROP VIEW IF EXISTS stg_orders;
DROP VIEW IF EXISTS stg_payments;

-- Intermediate models (might be ephemeral but good to check)
DROP VIEW IF EXISTS int_customer_orders;
DROP TABLE IF EXISTS int_customer_orders;

-- Marts tables
DROP TABLE IF EXISTS fct_orders;
DROP TABLE IF EXISTS dim_customers;

-- Note: We are NOT dropping the source tables (CUSTOMERS, ORDERS, PAYMENTS)
