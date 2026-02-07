-- =====================================================================
-- WORKSHEET 1 : ENVIRONMENT SETUP & CORE SNOWFLAKE FEATURES
-- =====================================================================
-- Objective: Create the lab database, schema, warehouse, sample data,
--            and explore core Snowflake capabilities (Time Travel,
--            Zero-Copy Clone, Caching, Data Sharing basics).
-- =====================================================================

-- 1A. Create Lab Resources
CREATE OR REPLACE WAREHOUSE lab_wh
  WITH WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME  = TRUE;

USE WAREHOUSE lab_wh;

CREATE OR REPLACE DATABASE lab_db;
CREATE OR REPLACE SCHEMA lab_db.lab_schema;
USE SCHEMA lab_db.lab_schema;

-- 1B. Create Sample Tables
CREATE OR REPLACE TABLE customers (
    customer_id   INT AUTOINCREMENT,
    name          VARCHAR(100),
    email         VARCHAR(200),
    city          VARCHAR(100),
    signup_date   DATE,
    tier          VARCHAR(20)
);

INSERT INTO customers (name, email, city, signup_date, tier) VALUES
('Alice Johnson',  'alice@example.com',   'New York',      '2024-03-15', 'Gold'),
('Bob Smith',      'bob@example.com',     'San Francisco', '2024-06-22', 'Silver'),
('Carlos Rivera',  'carlos@example.com',  'Chicago',       '2024-01-10', 'Platinum'),
('Diana Chen',     'diana@example.com',   'Seattle',       '2024-09-05', 'Gold'),
('Eva Müller',     'eva@example.com',     'Berlin',        '2023-11-18', 'Silver'),
('Fatima Al-Sayed','fatima@example.com',  'Dubai',         '2025-01-30', 'Gold'),
('George Tanaka',  'george@example.com',  'Tokyo',         '2024-07-12', 'Platinum'),
('Hannah Lee',     'hannah@example.com',  'Seoul',         '2025-04-01', 'Silver');

CREATE OR REPLACE TABLE products (
    product_id   INT AUTOINCREMENT,
    product_name VARCHAR(200),
    category     VARCHAR(100),
    price        DECIMAL(10,2),
    description  VARCHAR(2000)
);

INSERT INTO products (product_name, category, price, description) VALUES
('Smart Home Hub',      'Electronics',  149.99, 'Voice-controlled smart home hub with AI assistant, supports 50+ device types.'),
('Wireless Earbuds Pro','Electronics',   89.99, 'Noise-cancelling wireless earbuds with 24-hour battery and spatial audio.'),
('Organic Green Tea',   'Food & Bev',    12.50, 'Premium Japanese matcha green tea, 100g tin. Rich in antioxidants.'),
('Yoga Mat Premium',    'Fitness',       45.00, 'Eco-friendly TPE yoga mat, 6mm thick, non-slip surface, carrying strap included.'),
('Running Shoes X1',    'Fitness',      129.99, 'Carbon-plated running shoes designed for marathon training, ultra lightweight.'),
('AI Coding Assistant', 'Software',     299.00, 'AI-powered code completion and review tool, supports 40+ languages.'),
('Espresso Machine',    'Appliances',   599.00, 'Professional-grade espresso machine with built-in grinder and milk frother.'),
('Data Science Bootcamp','Education',   499.00, 'Self-paced 12-week data science course covering Python, ML, and SQL.');

CREATE OR REPLACE TABLE reviews (
    review_id   INT AUTOINCREMENT,
    product_id  INT,
    customer_id INT,
    review_text VARCHAR(5000),
    rating      INT,
    review_date DATE
);

INSERT INTO reviews (product_id, customer_id, review_text, rating, review_date) VALUES
(1, 1, 'Absolutely love this smart home hub! Setup was a breeze and it connects to everything. Voice recognition is impressive.', 5, '2025-01-20'),
(1, 3, 'Good product but the app crashes sometimes. Customer support was helpful though. Firmware updates have improved things.', 3, '2025-02-10'),
(2, 2, 'Best earbuds I have ever owned. Noise cancellation is top notch and the battery lasts forever. Worth every penny.', 5, '2025-03-05'),
(2, 5, 'Sound quality is great but they fall out of my ears during workouts. Not ideal for running.', 3, '2025-03-15'),
(3, 4, 'This matcha is incredible. Smooth taste, no bitterness. I have been ordering it monthly for 6 months now.', 5, '2025-04-01'),
(4, 1, 'Decent yoga mat but started peeling after 3 months of daily use. Expected better durability at this price.', 2, '2025-05-10'),
(5, 7, 'These running shoes are game changers. Shaved 5 minutes off my half marathon time. The carbon plate really works.', 5, '2025-06-20'),
(6, 3, 'The AI coding assistant has doubled my productivity. Code suggestions are remarkably accurate. Best investment for developers.', 5, '2025-07-01'),
(6, 8, 'Decent tool but struggles with newer frameworks. Also quite expensive for individual developers.', 3, '2025-07-15'),
(7, 6, 'Espresso quality rivals my local cafe. The built-in grinder is a game changer. Only downside is the size.', 4, '2025-08-01'),
(8, 2, 'Great course content but pacing is uneven. The SQL section is excellent. Python basics could use more depth.', 4, '2025-09-01'),
(5, 4, 'Terrible experience. Sole separated after just 2 weeks of running. Returning for a refund immediately.', 1, '2025-09-15');

CREATE OR REPLACE TABLE support_tickets (
    ticket_id    INT AUTOINCREMENT,
    customer_id  INT,
    subject      VARCHAR(500),
    description  VARCHAR(5000),
    status       VARCHAR(20),
    priority     VARCHAR(20),
    created_date DATE
);

INSERT INTO support_tickets (customer_id, subject, description, status, priority, created_date) VALUES
(1, 'Hub not connecting to thermostat', 'My smart home hub stopped connecting to my Nest thermostat after the latest firmware update. I have tried resetting both devices multiple times.', 'Open', 'High', '2025-10-01'),
(2, 'Earbuds charging case defect', 'The charging case does not close properly and the earbuds fall out. I think the hinge is broken. I need a replacement case.', 'Open', 'Medium', '2025-10-05'),
(3, 'Refund request for coding tool', 'I subscribed to the AI Coding Assistant but it does not support Rust as advertised. I would like a full refund for the annual subscription.', 'In Progress', 'High', '2025-10-10'),
(4, 'Shipping damage on yoga mat', 'Received my yoga mat with a large tear on one side. The packaging was clearly damaged during shipping. Please send a replacement.', 'Resolved', 'Low', '2025-09-20'),
(5, 'Wrong product received', 'I ordered the Wireless Earbuds Pro but received a different brand. Order number WEB-2025-8821. Please rectify.', 'Open', 'High', '2025-10-12'),
(6, 'Espresso machine leaking', 'The espresso machine leaks water from the bottom after every use. It started after about 2 months of use. Concerned about electrical safety.', 'In Progress', 'Critical', '2025-10-15'),
(7, 'Course certificate not generated', 'I completed the Data Science Bootcamp but my certificate has not been generated. It has been 2 weeks since completion.', 'Resolved', 'Low', '2025-09-25'),
(8, 'Running shoes warranty claim', 'The sole of my Running Shoes X1 separated after only 2 weeks. I would like to claim warranty. I have photos of the defect.', 'Open', 'Medium', '2025-10-18');


-- -----------------------------------------------------------------
-- 1C. TIME TRAVEL — Query Historical Data
-- -----------------------------------------------------------------
-- First, let's make a change we can travel back from
SELECT COUNT(*) AS before_count FROM customers;

DELETE FROM customers WHERE tier = 'Silver';
SELECT COUNT(*) AS after_delete_count FROM customers;

-- Travel back 1 minute (adjust offset as needed)
SELECT COUNT(*) AS time_travel_count
FROM customers AT(OFFSET => -60);

-- Restore deleted rows using Time Travel
INSERT INTO customers
  SELECT * FROM customers AT(OFFSET => -60)
  WHERE tier = 'Silver';

SELECT COUNT(*) AS restored_count FROM customers;


-- -----------------------------------------------------------------
-- 1D. ZERO-COPY CLONING
-- -----------------------------------------------------------------
CREATE OR REPLACE TABLE customers_clone CLONE customers;

-- The clone is independent — changes here won't affect original
UPDATE customers_clone SET tier = 'Diamond' WHERE customer_id = 1;

-- Verify independence
SELECT name, tier FROM customers       WHERE customer_id = 1;  -- Still Gold
SELECT name, tier FROM customers_clone WHERE customer_id = 1;  -- Diamond

DROP TABLE customers_clone;


-- -----------------------------------------------------------------
-- 1E. RESULT CACHING DEMO
-- -----------------------------------------------------------------
-- Run this query twice — second run uses cache (check query profile)
SELECT c.name, p.product_name, r.rating, r.review_text
FROM reviews r
  JOIN customers c ON r.customer_id = c.customer_id
  JOIN products p  ON r.product_id  = p.product_id
ORDER BY r.rating DESC;

