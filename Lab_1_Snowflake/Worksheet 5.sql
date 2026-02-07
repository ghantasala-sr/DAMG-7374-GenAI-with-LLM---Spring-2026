-- =====================================================================
-- WORKSHEET 5 : CORTEX SEARCH, CORTEX ANALYST & CORTEX AGENTS
-- =====================================================================
-- Objective: Deep dive into Snowflake's three pillars of intelligent
--            data access:
--   Part A — Cortex Search  (semantic search over unstructured data)
--   Part B — Cortex Analyst (natural language → SQL via Semantic Views)
--   Part C — Cortex Agents  (orchestrating Search + Analyst + tools)
--
-- Prerequisites: Run Worksheet 1 first (creates lab_db, tables, data).
-- =====================================================================

USE ROLE ACCOUNTADMIN;   -- or a role with SNOWFLAKE.CORTEX_USER
USE WAREHOUSE lab_wh;
USE SCHEMA lab_db.lab_schema;


-- ╔══════════════════════════════════════════════════════════════════╗
-- ║  PART A — CORTEX SEARCH                                        ║
-- ║  Fully managed hybrid (semantic + keyword) search service       ║
-- ╚══════════════════════════════════════════════════════════════════╝

-- -----------------------------------------------------------------
-- A1. Prepare Source Data — Knowledge Base Articles
-- -----------------------------------------------------------------
-- Simulate a company knowledge base for support / FAQ articles

CREATE OR REPLACE TABLE knowledge_articles (
    article_id   INT AUTOINCREMENT,
    title        VARCHAR(500),
    content      VARCHAR(10000),
    category     VARCHAR(100),
    author       VARCHAR(100),
    publish_date DATE
);

INSERT INTO knowledge_articles (title, content, category, author, publish_date) VALUES
('Getting Started with Smart Home Hub',
 'Welcome to the Smart Home Hub setup guide. First, download the SmartHome app from the App Store or Google Play. Plug in your hub and wait for the LED to turn blue. Open the app, tap "Add Device" and follow the pairing steps. The hub supports Wi-Fi 6 and Bluetooth 5.0. You can connect up to 50 devices including lights, thermostats, cameras, and door locks. For Nest thermostat integration, go to Settings > Integrations > Nest and sign in with your Google account. If the LED turns red, perform a factory reset by holding the button for 10 seconds.',
 'Setup Guide', 'Tech Support', '2025-01-15'),

('Troubleshooting Hub Connectivity Issues',
 'If your Smart Home Hub loses connection to devices, try these steps: 1) Restart the hub by unplugging for 30 seconds. 2) Check your Wi-Fi signal strength — the hub needs at least 2 bars. 3) Move the hub away from microwaves and cordless phones which cause interference. 4) Update firmware via the app under Settings > Firmware > Check for Updates. 5) If the Nest thermostat specifically disconnects, ensure the Nest is on firmware version 6.2 or later. 6) For persistent issues, enable debug logging: Settings > Advanced > Debug Mode, and contact support with the generated log file.',
 'Troubleshooting', 'Tech Support', '2025-02-20'),

('Wireless Earbuds Pro — User Manual',
 'Your Wireless Earbuds Pro feature active noise cancellation (ANC), transparency mode, and spatial audio. To pair: open the charging case near your phone and tap "Connect" in the notification. Battery life is 8 hours per charge with ANC on, 12 hours with ANC off, and the case provides 3 additional charges. To customize EQ settings, download the AudioPro companion app. Ear tip sizes included: XS, S, M, L. For best fit during workouts, try the wing tips included in the box. IP54 water resistance means they handle sweat and light rain but should not be submerged.',
 'User Manual', 'Product Team', '2025-03-10'),

('Return and Refund Policy',
 'We offer a 30-day return policy for all products purchased directly from our store. Items must be in original packaging with all accessories. Refunds are processed within 5-7 business days to your original payment method. For defective products, we offer free return shipping — contact support to get a prepaid label. Warranty claims can be filed within 1 year of purchase for manufacturing defects. Software subscriptions like the AI Coding Assistant have a 14-day money-back guarantee. After 14 days, you can cancel anytime but refunds are prorated. International orders have a 45-day return window due to shipping times.',
 'Policy', 'Customer Service', '2025-01-05'),

('AI Coding Assistant — Quick Start Guide',
 'The AI Coding Assistant supports 40+ programming languages including Python, JavaScript, TypeScript, Go, Rust, Java, and C++. Install the extension from VS Code Marketplace or JetBrains Plugin Repository. After installation, sign in with your license key. Key features: 1) Inline code completion — suggestions appear as you type. 2) Chat mode — ask coding questions in the sidebar. 3) Code review — select code and press Ctrl+Shift+R for AI review. 4) Test generation — right-click a function and select "Generate Tests". The tool currently does NOT support Dart, Haskell, or Zig. For Rust support, ensure you have version 2.3+ of the extension.',
 'User Manual', 'Product Team', '2025-04-01'),

('Espresso Machine Maintenance Guide',
 'Regular maintenance keeps your espresso machine performing at its best. Daily: rinse the portafilter and group head after each use. Weekly: run a cleaning cycle using the included cleaning tablets — insert a tablet into the portafilter, select "Clean" from the menu, and let it run for 5 minutes. Monthly: descale using citric acid solution. Fill the water tank with descaling solution, press "Descale" and follow the prompts. This takes about 20 minutes. The built-in grinder should be calibrated every 3 months — use the calibration tool included in the box. Replace the water filter every 6 months (part number ESM-FILTER-200). Warning: never use vinegar for descaling as it can damage internal seals.',
 'Maintenance', 'Product Team', '2025-05-15'),

('Running Shoes X1 — Warranty and Care',
 'The Running Shoes X1 come with a 6-month warranty against manufacturing defects including sole separation, stitching failure, and material delamination. Normal wear and tear is not covered. To file a warranty claim, submit photos of the defect through our support portal along with your order number. Expected lifespan is 400-500 miles of running. To extend shoe life: rotate between two pairs, let shoes dry naturally (never use a dryer), and clean with mild soap and cold water. The carbon plate is designed to maintain its energy return properties for the full lifespan of the shoe.',
 'Warranty', 'Customer Service', '2025-06-01'),

('Data Science Bootcamp — Curriculum Overview',
 'The 12-week Data Science Bootcamp is structured in 4 modules. Module 1 (Weeks 1-3): Python Fundamentals — variables, data structures, functions, OOP, pandas, and numpy. Module 2 (Weeks 4-6): Data Analysis & Visualization — matplotlib, seaborn, statistical analysis, hypothesis testing. Module 3 (Weeks 7-9): Machine Learning — scikit-learn, regression, classification, clustering, model evaluation. Module 4 (Weeks 10-12): Advanced Topics — deep learning basics with PyTorch, NLP fundamentals, and a capstone project. Each week includes 5 hours of video content, 2 coding assignments, and 1 quiz. Certificates are generated automatically upon completing all modules with a score of 70% or higher.',
 'Education', 'Education Team', '2025-07-01'),

('Shipping and Delivery Information',
 'Domestic orders (US): Standard shipping is free for orders over $50 and takes 5-7 business days. Express shipping ($12.99) delivers in 2-3 business days. Next-day shipping ($24.99) is available for orders placed before 2 PM EST. International shipping: Available to 40+ countries. Shipping costs and times vary by destination — typically 7-14 business days. Customs duties and import taxes are the responsibility of the buyer. All orders include tracking. For large items like the Espresso Machine, white glove delivery ($49.99) is available in select metro areas. We ship from warehouses in New Jersey, Texas, and California.',
 'Policy', 'Operations', '2025-01-20'),

('How to Contact Support',
 'Our support team is available Monday-Friday 8 AM to 8 PM EST, and Saturday 10 AM to 4 PM EST. Contact options: 1) Live Chat — fastest response, available on our website and app. Average wait time is under 2 minutes. 2) Email — support@example.com, response within 24 hours. 3) Phone — 1-800-555-0199, average hold time 5 minutes. 4) Community Forum — post questions and get help from other users and moderators. For critical issues like product safety concerns, use phone support and select option 3 for priority routing. Include your order number in all communications for faster resolution.',
 'Support', 'Customer Service', '2025-02-01');


-- -----------------------------------------------------------------
-- A2. Enable Change Tracking (required for Cortex Search refresh)
-- -----------------------------------------------------------------
ALTER TABLE knowledge_articles SET CHANGE_TRACKING = TRUE;
ALTER TABLE support_tickets    SET CHANGE_TRACKING = TRUE;
ALTER TABLE reviews            SET CHANGE_TRACKING = TRUE;


-- -----------------------------------------------------------------
-- A3. Create Cortex Search Service — Knowledge Base
-- -----------------------------------------------------------------
-- This creates a fully managed semantic search index over the articles.
-- Snowflake handles embedding generation, indexing, and auto-refresh.

CREATE OR REPLACE CORTEX SEARCH SERVICE kb_search_service
  ON content                          -- primary column to search
  ATTRIBUTES category, author         -- filterable columns
  WAREHOUSE = lab_wh
  TARGET_LAG = '1 hour'               -- auto-refresh lag
  EMBEDDING_MODEL = 'snowflake-arctic-embed-l-v2.0'
AS (
    SELECT
        article_id,
        title,
        content,
        category,
        author,
        publish_date
    FROM knowledge_articles
);


-- -----------------------------------------------------------------
-- A4. Create Cortex Search Service — Customer Reviews
-- -----------------------------------------------------------------
CREATE OR REPLACE CORTEX SEARCH SERVICE review_search_service
  ON review_text
  ATTRIBUTES product_id
  WAREHOUSE = lab_wh
  TARGET_LAG = '1 hour'
  EMBEDDING_MODEL = 'snowflake-arctic-embed-l-v2.0'
AS (
    SELECT
        r.review_id,
        r.review_text,
        r.rating,
        r.review_date,
        r.product_id,
        p.product_name,
        p.category AS product_category
    FROM reviews r
      JOIN products p ON r.product_id = p.product_id
);


-- -----------------------------------------------------------------
-- A5. Create Cortex Search Service — Support Tickets
-- -----------------------------------------------------------------
CREATE OR REPLACE CORTEX SEARCH SERVICE ticket_search_service
  ON description
  ATTRIBUTES status, priority
  WAREHOUSE = lab_wh
  TARGET_LAG = '1 hour'
  EMBEDDING_MODEL = 'snowflake-arctic-embed-l-v2.0'
AS (
    SELECT
        ticket_id,
        subject,
        description,
        status,
        priority,
        created_date,
        customer_id
    FROM support_tickets
);


-- -----------------------------------------------------------------
-- A6. Verify Search Services
-- -----------------------------------------------------------------
SHOW CORTEX SEARCH SERVICES IN SCHEMA lab_db.lab_schema;

-- Detailed info on a specific service
DESCRIBE CORTEX SEARCH SERVICE kb_search_service;


-- -----------------------------------------------------------------
-- A7. Query Search Services using SEARCH_PREVIEW (SQL)
-- -----------------------------------------------------------------
-- SEARCH_PREVIEW is for testing/validation from SQL worksheets.
-- Production apps use the REST API or Python SDK.

-- Semantic search: "Hub won't connect to thermostat"
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'lab_db.lab_schema.kb_search_service',            -- service name
    '{
        "query": "hub not connecting to thermostat",
        "columns": ["title", "content", "category"],
        "limit": 3
    }'
) AS search_results;

-- Search with attribute filter: only Troubleshooting articles
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'lab_db.lab_schema.kb_search_service',
    '{
        "query": "firmware update connectivity",
        "columns": ["title", "content"],
        "filter": {"@eq": {"category": "Troubleshooting"}},
        "limit": 3
    }'
) AS filtered_results;

-- Search reviews for quality issues
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'lab_db.lab_schema.review_search_service',
    '{
        "query": "product defect broke after short use",
        "columns": ["review_text", "product_name", "rating"],
        "limit": 5
    }'
) AS review_results;

-- Search support tickets by priority
SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
    'lab_db.lab_schema.ticket_search_service',
    '{
        "query": "safety concern leaking",
        "columns": ["subject", "description", "priority"],
        "filter": {"@eq": {"priority": "Critical"}},
        "limit": 3
    }'
) AS critical_tickets;


-- -----------------------------------------------------------------
-- A8. RAG Pattern — Search + AI_COMPLETE
-- -----------------------------------------------------------------
-- Use Cortex Search to find relevant context, then feed it to an LLM.
-- This is the Retrieval-Augmented Generation (RAG) pattern.

-- Step 1: Get search results (simulated — in production use Python SDK)
-- Step 2: Pass the context to AI_COMPLETE

-- For a SQL-only RAG demo, we can combine AI_SIMILARITY + AI_COMPLETE:
WITH user_question AS (
    SELECT 'How do I reset my Smart Home Hub and reconnect my Nest thermostat?' AS question
),
question_embedding AS (
    SELECT 
        uq.question,
        SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', uq.question) AS q_embedding
    FROM user_question uq
),
relevant_articles AS (
    SELECT
        ka.title,
        ka.content,
        VECTOR_COSINE_SIMILARITY(
            qe.q_embedding,
            SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', ka.content)
        ) AS relevance
    FROM knowledge_articles ka
    CROSS JOIN question_embedding qe
    ORDER BY relevance DESC
    LIMIT 2
),
context_text AS (
    SELECT 
        LISTAGG('--- ' || title || ' ---\n' || content, '\n\n') 
        WITHIN GROUP (ORDER BY relevance DESC) AS context
    FROM relevant_articles
)
SELECT AI_COMPLETE(
    'claude-4-sonnet',
    'You are a helpful support assistant. Answer the question based ONLY on the ' ||
    'provided context. If the context does not contain the answer, say so.\n\n' ||
    'CONTEXT:\n' ||
    ct.context || '\n\n' ||
    'QUESTION: ' || uq.question
) AS rag_answer
FROM user_question uq
CROSS JOIN context_text ct;


-- -----------------------------------------------------------------
-- A9. Auto-Refresh Demo — Insert New Article and Search for It
-- -----------------------------------------------------------------
INSERT INTO knowledge_articles (title, content, category, author, publish_date) VALUES
('Smart Home Hub — Voice Command Reference',
 'The Smart Home Hub supports the following voice commands: "Hey Hub, turn on the lights" — controls all connected lights. "Hey Hub, set thermostat to 72" — adjusts Nest or Ecobee thermostat. "Hey Hub, lock the front door" — locks compatible smart locks. "Hey Hub, play music in the kitchen" — streams to connected speakers. "Hey Hub, what is the weather" — gives local weather forecast. "Hey Hub, arm the security system" — activates home security. For a full list, say "Hey Hub, list all commands" or visit the commands page in the app.',
 'User Manual', 'Product Team', '2025-11-01');

-- After TARGET_LAG (1 hour), this article will appear in search results.
-- For demo purposes, you can recreate the service to force immediate refresh.



-- ╔══════════════════════════════════════════════════════════════════╗
-- ║  PART B — CORTEX ANALYST                                       ║
-- ║  Natural language → SQL via Semantic Views                      ║
-- ╚══════════════════════════════════════════════════════════════════╝

-- -----------------------------------------------------------------
-- B1. Prepare Structured Data — Sales & Orders Tables
-- -----------------------------------------------------------------

CREATE OR REPLACE TABLE orders (
    order_id     INT AUTOINCREMENT,
    customer_id  INT,
    product_id   INT,
    order_date   DATE,
    quantity     INT,
    unit_price   DECIMAL(10,2),
    discount     DECIMAL(5,2) DEFAULT 0.00,
    status       VARCHAR(20)
);

INSERT INTO orders (customer_id, product_id, order_date, quantity, unit_price, discount, status) VALUES
(1, 1, '2025-01-20', 1, 149.99, 0.00,  'Delivered'),
(1, 4, '2025-03-10', 2,  45.00, 0.10,  'Delivered'),
(2, 2, '2025-02-15', 1,  89.99, 0.00,  'Delivered'),
(2, 8, '2025-04-01', 1, 499.00, 0.15,  'Delivered'),
(3, 6, '2025-05-05', 1, 299.00, 0.00,  'Delivered'),
(3, 1, '2025-05-20', 1, 149.99, 0.05,  'Delivered'),
(4, 5, '2025-06-10', 1, 129.99, 0.00,  'Delivered'),
(4, 3, '2025-06-10', 3,  12.50, 0.00,  'Delivered'),
(5, 2, '2025-07-01', 2,  89.99, 0.00,  'Delivered'),
(5, 7, '2025-07-15', 1, 599.00, 0.10,  'Delivered'),
(6, 7, '2025-08-01', 1, 599.00, 0.00,  'Delivered'),
(6, 3, '2025-08-01', 5,  12.50, 0.00,  'Delivered'),
(7, 5, '2025-08-15', 2, 129.99, 0.05,  'Delivered'),
(7, 6, '2025-09-01', 1, 299.00, 0.00,  'Delivered'),
(8, 8, '2025-09-10', 1, 499.00, 0.20,  'Delivered'),
(8, 4, '2025-09-10', 1,  45.00, 0.00,  'Delivered'),
(1, 3, '2025-10-01', 2,  12.50, 0.00,  'Shipped'),
(2, 1, '2025-10-05', 1, 149.99, 0.10,  'Shipped'),
(3, 7, '2025-10-10', 1, 599.00, 0.00,  'Processing'),
(4, 6, '2025-10-15', 1, 299.00, 0.00,  'Processing'),
(5, 5, '2025-10-20', 1, 129.99, 0.00,  'Processing'),
(6, 2, '2025-10-25', 3,  89.99, 0.05,  'Pending'),
(7, 8, '2025-11-01', 1, 499.00, 0.10,  'Pending'),
(8, 1, '2025-11-05', 2, 149.99, 0.00,  'Pending');


-- -----------------------------------------------------------------
-- B2. Create Semantic View — The Core of Cortex Analyst
-- -----------------------------------------------------------------
-- Semantic Views define business logic, relationships, metrics, and
-- verified queries. Cortex Analyst uses them to generate accurate SQL.



CREATE OR REPLACE SEMANTIC VIEW ecommerce_analytics

  -- ---- Logical Tables ----
  TABLES (
    customers AS lab_db.lab_schema.customers PRIMARY KEY (customer_id),
    products  AS lab_db.lab_schema.products  PRIMARY KEY (product_id),
    orders    AS lab_db.lab_schema.orders    PRIMARY KEY (order_id),
    reviews   AS lab_db.lab_schema.reviews   PRIMARY KEY (review_id)
  )

  -- ---- Relationships ----
  RELATIONSHIPS (
    orders_cust AS orders  (customer_id) REFERENCES customers,
    orders_prod AS orders  (product_id)  REFERENCES products,
    reviews_cust AS reviews (customer_id) REFERENCES customers,
    reviews_prod AS reviews (product_id)  REFERENCES products
  )

  -- ---- Facts (row-level computed values) ----
  FACTS (
    orders.line_total           AS quantity * unit_price,
    orders.line_discount_amount AS quantity * unit_price * discount,
    orders.line_net_total       AS quantity * unit_price * (1 - discount),
    reviews.review_rating       AS rating
  )

  -- ---- Dimensions (groupable attributes) ----
  DIMENSIONS (
    customers.customer_name  AS name,
    customers.customer_email AS email,
    customers.customer_city  AS city,
    customers.customer_tier  AS tier,
    customers.customer_signup_date AS signup_date,
    products.prod_name       AS product_name,
    products.prod_category   AS category,
    products.prod_price      AS price,
    orders.order_date        AS order_date,
    orders.order_status      AS status,
    reviews.review_date      AS review_date
  )

  -- ---- Metrics (aggregated KPIs) ----
  METRICS (
    orders.gross_revenue    AS SUM(orders.line_total),
    orders.net_revenue      AS SUM(orders.line_net_total),
    orders.total_orders     AS COUNT(orders.order_id),
    orders.avg_order_value  AS AVG(orders.line_net_total),
    orders.total_discount   AS SUM(orders.line_discount_amount),
    orders.unique_customers AS COUNT(DISTINCT orders.customer_id),
    reviews.avg_rating      AS AVG(reviews.review_rating),
    reviews.review_count    AS COUNT(reviews.review_id)
  )

  COMMENT = 'E-commerce analytics semantic model for Cortex Analyst'
;


-- -----------------------------------------------------------------
-- B3. Verify the Semantic View
-- -----------------------------------------------------------------
SHOW SEMANTIC VIEWS IN SCHEMA lab_db.lab_schema;
DESCRIBE SEMANTIC VIEW ecommerce_analytics;

-- Another example: revenue by customer tier
SELECT * FROM SEMANTIC_VIEW(
    ecommerce_analytics
    DIMENSIONS customers.customer_tier
    METRICS orders.net_revenue, orders.unique_customers, orders.avg_order_value
)
ORDER BY net_revenue DESC;



-- -----------------------------------------------------------------
-- B4. Grant Access to Analyst Users
-- -----------------------------------------------------------------
-- GRANT REFERENCES, SELECT ON SEMANTIC VIEW ecommerce_analytics
--   TO ROLE analyst_role;


-- -----------------------------------------------------------------
-- B5. Test Cortex Analyst — Via Snowsight UI
-- -----------------------------------------------------------------
-- In Snowsight:
--   1. Navigate to AI & ML » Cortex Analyst
--   2. Select the "ecommerce_analytics" semantic view
--   3. Try these natural language questions:
--
--   "What is our total revenue?"
--   "Top 5 products by net revenue"
--   "Show monthly revenue trend"
--   "Which customer tier generates the most revenue?"
--   "What is the average order value by product category?"
--   "Which products have the lowest ratings?"
--   "How many orders are still pending or processing?"
--   "Compare revenue between Gold and Platinum customers"
--   "What is the total discount we have given?"
--   "Show me customers from Tokyo with their order history"
--
-- Cortex Analyst will:
--   • Generate SQL using your semantic view definitions
--   • Execute it and return results
--   • Show the SQL so you can verify correctness


-- -----------------------------------------------------------------
-- B6. Cortex Analyst — Monitoring & Debugging
-- -----------------------------------------------------------------
-- Monitor how Cortex Analyst interprets questions and generates SQL

-- View Cortex Analyst request history (requires ACCOUNTADMIN or SNOWFLAKE.USAGE_VIEWER role)
-- USE ROLE ACCOUNTADMIN;  -- Uncomment if you have access
-- SELECT *
-- FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_ANALYST_USAGE
-- ORDER BY QUERY_TIMESTAMP DESC
-- LIMIT 20;

-- Alternatively use Information Schema
-- SELECT * FROM TABLE(INFORMATION_SCHEMA.CORTEX_ANALYST_USAGE(
--   DATE_RANGE_START => DATEADD('hour', -24, CURRENT_TIMESTAMP())
-- ));



-- ╔══════════════════════════════════════════════════════════════════╗
-- ║  PART C — CORTEX AGENTS                                        ║
-- ║  Orchestration layer combining Search + Analyst + Custom Tools  ║
-- ╚══════════════════════════════════════════════════════════════════╝

-- -----------------------------------------------------------------
-- C1. Understanding Cortex Agents Architecture
-- -----------------------------------------------------------------
-- Cortex Agents orchestrate across:
--   • Cortex Analyst  → structured data (SQL generation)
--   • Cortex Search   → unstructured data (semantic search)
--   • Custom Tools    → stored procedures / UDFs
--   • Web Search      → external information
--
-- The Agent:
--   1. PLANS: breaks user request into sub-tasks
--   2. USES TOOLS: selects the right tool for each sub-task
--   3. REFLECTS: evaluates results, iterates if needed
--   4. RESPONDS: synthesizes a final answer


-- -----------------------------------------------------------------
-- C2. Create a Custom Tool (Stored Procedure)
-- -----------------------------------------------------------------
-- Custom tools let the Agent call your business logic

CREATE OR REPLACE FUNCTION get_customer_lifetime_value(cust_id INT)
  RETURNS TABLE (
      customer_name VARCHAR,
      total_orders INT,
      lifetime_revenue DECIMAL(12,2),
      avg_order_value DECIMAL(10,2),
      first_order DATE,
      last_order DATE,
      tier VARCHAR
  )
  LANGUAGE SQL
AS
$$
    SELECT
        c.name AS customer_name,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(o.quantity * o.unit_price * (1 - o.discount)) AS lifetime_revenue,
        AVG(o.quantity * o.unit_price * (1 - o.discount)) AS avg_order_value,
        MIN(o.order_date) AS first_order,
        MAX(o.order_date) AS last_order,
        c.tier
    FROM customers c
      LEFT JOIN orders o ON c.customer_id = o.customer_id
    WHERE c.customer_id = cust_id
    GROUP BY c.name, c.tier
$$;

-- Test the function
SELECT * FROM TABLE(get_customer_lifetime_value(1));
SELECT * FROM TABLE(get_customer_lifetime_value(3));


-- -----------------------------------------------------------------
-- C3. Create Cortex Agent — SQL (CREATE AGENT)
-- -----------------------------------------------------------------
-- The Agent combines Cortex Analyst (structured) + Cortex Search
-- (unstructured) + custom tools into a single conversational interface.

CREATE OR REPLACE AGENT ecommerce_support_agent
  COMMENT = 'E-commerce support agent combining sales analytics and knowledge base search'
  PROFILE = '{"display_name": "E-Commerce Support Assistant", "color": "blue"}'
  FROM SPECIFICATION
$$
models:
  orchestration: auto

orchestration:
  budget:
    seconds: 30
    tokens: 16000

instructions:
  system: >
    You are a helpful e-commerce support assistant. You help users with
    sales analytics, product questions, and support inquiries. Be concise,
    friendly, and data-driven.
  orchestration: >
    For questions about revenue, orders, sales metrics, or customer data,
    use the Analyst tool to query structured data.
    For questions about product guides, troubleshooting, policies, or
    how-to instructions, use the Search tool to find relevant articles.
    For customer lifetime value calculations, use the custom CLV tool.
  response: >
    Always provide clear, actionable answers. When showing data, summarize
    key insights. Cite your sources when using search results.

tools:
  - tool_spec:
      type: cortex_analyst_text_to_sql
      name: SalesAnalyst
      description: >
        Converts natural language questions about sales, orders, revenue,
        customers, and products into SQL queries using the e-commerce
        semantic model.
  - tool_spec:
      type: cortex_search
      name: KnowledgeBase
      description: >
        Searches the company knowledge base for product guides,
        troubleshooting articles, policies, and support documentation.
  - tool_spec:
      type: cortex_search
      name: ReviewSearch
      description: >
        Searches customer reviews to find feedback about specific
        products or issues.
  - tool_spec:
      type: sql_exec
      name: SQLExec
  - tool_spec:
      type: data_to_chart
      name: ChartGenerator

tool_resources:
  SalesAnalyst:
    semantic_view: "lab_db.lab_schema.ecommerce_analytics"
  KnowledgeBase:
    name: "lab_db.lab_schema.kb_search_service"
    max_results: 3
  ReviewSearch:
    name: "lab_db.lab_schema.review_search_service"
    max_results: 5
$$;


-- -----------------------------------------------------------------
-- C4. Verify Agent Creation
-- -----------------------------------------------------------------
SHOW AGENTS IN SCHEMA lab_db.lab_schema;
DESCRIBE AGENT ecommerce_support_agent;

-- Grant access to other roles
-- GRANT USAGE ON AGENT ecommerce_support_agent TO ROLE analyst_role;


-- -----------------------------------------------------------------
-- C5. Interact with the Agent — Snowsight UI
-- -----------------------------------------------------------------
-- In Snowsight:
--   1. Navigate to AI & ML » Agents
--   2. Select "ecommerce_support_agent"
--   3. Try these conversations:
--
-- === Structured Data (uses Cortex Analyst) ===
--   "What is our total net revenue?"
--   "Show me the top 5 products by revenue"
--   "Which customer tier has the highest average order value?"
--   "Plot a chart of monthly revenue trend"
--   "How many orders are pending?"
--
-- === Unstructured Data (uses Cortex Search) ===
--   "How do I set up the Smart Home Hub?"
--   "My hub won't connect to my Nest thermostat"
--   "What is the return policy for software subscriptions?"
--   "How do I descale the espresso machine?"
--   "What voice commands does the hub support?"
--
-- === Mixed Queries (Agent orchestrates multiple tools) ===
--   "Which product has the most revenue but lowest ratings?"
--   "Show me running shoe revenue and what customers say about durability"
--   "Are there any support articles related to our lowest-rated products?"
--
-- === Review Search ===
--   "What are customers saying about the earbuds during workouts?"
--   "Find reviews mentioning product defects"


-- -----------------------------------------------------------------
-- C6. Interact with Agent — REST API (Reference)
-- -----------------------------------------------------------------
-- For programmatic access, use the Agent Run API:
--
-- POST /api/v2/databases/LAB_DB/schemas/LAB_SCHEMA/agents/ECOMMERCE_SUPPORT_AGENT:run
-- Headers:
--   Authorization: Bearer <token>
--   Content-Type: application/json
--
-- Body:
-- {
--   "messages": [
--     {
--       "role": "user",
--       "content": [
--         {"type": "text", "text": "What was our total revenue last month?"}
--       ]
--     }
--   ],
--   "stream": true
-- }
--
-- The response streams Server-Sent Events (SSE) including:
--   - thinking events (agent reasoning)
--   - tool_use events (which tools are called)
--   - tool_result events (tool outputs)
--   - text events (final response with citations)


-- -----------------------------------------------------------------
-- C7. Agent Observability — Monitor Agent Performance
-- -----------------------------------------------------------------
-- View agent interactions and tool usage patterns

-- Check agent usage (requires ACCOUNTADMIN or SNOWFLAKE.USAGE_VIEWER role)
-- USE ROLE ACCOUNTADMIN;  -- Uncomment if you have access
-- SELECT *
-- FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AGENTS_USAGE
-- ORDER BY QUERY_TIMESTAMP DESC
-- LIMIT 20;


-- -----------------------------------------------------------------
-- C8. Advanced: Multi-Turn Conversation Pattern
-- -----------------------------------------------------------------
-- The Agent supports multi-turn conversations via the API.
-- Each subsequent request includes the full message history:
--
-- Request 1: "What is our top product by revenue?"
-- Response 1: "The Espresso Machine leads with $1,137.10 in net revenue."
--
-- Request 2 (includes history):
-- {
--   "messages": [
--     {"role": "user", "content": [{"type": "text",
--        "text": "What is our top product by revenue?"}]},
--     {"role": "assistant", "content": [{"type": "text",
--        "text": "The Espresso Machine leads with $1,137.10..."}]},
--     {"role": "user", "content": [{"type": "text",
--        "text": "What do customer reviews say about it?"}]}
--   ]
-- }
--
-- The Agent will use context from turn 1 to understand "it" refers
-- to the Espresso Machine, then use Cortex Search to find reviews.



-- ╔══════════════════════════════════════════════════════════════════╗
-- ║  PART D — PUTTING IT ALL TOGETHER: Architecture Summary         ║
-- ╚══════════════════════════════════════════════════════════════════╝
--
--  ┌──────────────────────────────────────────────────────────┐
--  │                    CORTEX AGENT                          │
--  │       (Orchestration · Planning · Reflection)            │
--  │                                                          │
--  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
--  │   │   CORTEX      │  │   CORTEX      │  │   CUSTOM     │  │
--  │   │   ANALYST     │  │   SEARCH      │  │   TOOLS      │  │
--  │   │              │  │              │  │              │  │
--  │   │ Semantic View │  │ Search Index  │  │ UDFs / SPs   │  │
--  │   │ → SQL Gen     │  │ → Semantic    │  │ → Business   │  │
--  │   │ → Execute     │  │   Retrieval   │  │   Logic      │  │
--  │   │              │  │              │  │              │  │
--  │   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
--  │          │                 │                  │          │
--  │   ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐  │
--  │   │  Structured   │  │ Unstructured  │  │  Functions   │  │
--  │   │  Tables       │  │  Text/Docs    │  │  & Procs     │  │
--  │   └──────────────┘  └──────────────┘  └──────────────┘  │
--  └──────────────────────────────────────────────────────────┘
--
--  Key Takeaways:
--  • Cortex Search  = Semantic search, auto-indexed, auto-refreshed
--  • Cortex Analyst = NL-to-SQL with Semantic Views for accuracy
--  • Cortex Agent   = Orchestration layer combining all tools
--  • Everything runs within Snowflake's security boundary (RBAC)
--  • No data leaves Snowflake — LLMs run inside Cortex


-- -----------------------------------------------------------------
-- CLEANUP (Optional)
-- -----------------------------------------------------------------
-- DROP AGENT ecommerce_support_agent;
-- DROP CORTEX SEARCH SERVICE kb_search_service;
-- DROP CORTEX SEARCH SERVICE review_search_service;
-- DROP CORTEX SEARCH SERVICE ticket_search_service;
-- DROP SEMANTIC VIEW ecommerce_analytics;
-- DROP TABLE knowledge_articles;
-- DROP TABLE orders;