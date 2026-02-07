-- =====================================================================
-- WORKSHEET 2 : CORTEX AI — TEXT INTELLIGENCE (AI SQL FUNCTIONS)
-- =====================================================================
-- Objective: Use Snowflake Cortex AISQL functions to perform sentiment
--            analysis, summarization, classification, filtering, and
--            text generation directly in SQL.
-- =====================================================================

USE SCHEMA lab_db.lab_schema;
USE WAREHOUSE lab_wh;

-- -----------------------------------------------------------------
-- 2A. AI_COMPLETE — Free-form LLM Prompts in SQL
-- -----------------------------------------------------------------

-- Simple prompt completion
SELECT AI_COMPLETE('snowflake-arctic', 'What are large language models?');

SELECT AI_COMPLETE(
    model => 'deepseek-r1',
    prompt => 'how does a snowflake get its unique pattern?',
    model_parameters => {
        'temperature': 0.7,
        'max_tokens': 10
    }
);

-- Use AI_COMPLETE on table data: generate response suggestions for tickets
SELECT
    t.ticket_id,
    t.subject,
    t.description,
    AI_COMPLETE(
        'claude-4-sonnet',
        'You are a customer support agent. Write a helpful, empathetic response ' ||
        'to this support ticket in 2-3 sentences. Ticket: ' || t.description
    ) AS suggested_response
FROM support_tickets t
WHERE t.status = 'Open'
LIMIT 5;

SELECT SNOWFLAKE.CORTEX.COUNT_TOKENS( 'llama3.1-70b', 'what is a large language model?' );

-- -----------------------------------------------------------------
-- 2B. AI_SENTIMENT — Sentiment Analysis on Reviews
-- -----------------------------------------------------------------
SELECT
    r.review_id,
    r.review_text,
    r.rating,
    AI_SENTIMENT(r.review_text) AS sentiment_score
FROM reviews r
ORDER BY sentiment_score ASC;

-- -----------------------------------------------------------------
-- 2C. AI_CLASSIFY — Categorize Text Into Labels
-- -----------------------------------------------------------------

-- Classify support tickets by department
SELECT
    t.ticket_id,
    t.subject,
    AI_CLASSIFY(
        t.description,
        ['Hardware Defect', 'Software Bug', 'Shipping Issue',
         'Billing/Refund', 'General Inquiry']
    ) AS department
FROM support_tickets t;

-- Classify review sentiment into categories
SELECT
    r.review_id,
    LEFT(r.review_text, 60) AS review_preview,
    AI_CLASSIFY(
        r.review_text,
        ['Very Positive', 'Positive', 'Neutral', 'Negative', 'Very Negative']
    ) AS sentiment_category
FROM reviews r;


-- -----------------------------------------------------------------
-- 2D. AI_FILTER — Natural Language WHERE Clause
-- -----------------------------------------------------------------

-- Find reviews that mention product defects or quality issues
SELECT
    r.review_id,
    r.review_text,
    r.rating
FROM reviews r
WHERE AI_FILTER(
    'The review mentions a product defect, quality issue, or durability problem: '
    || r.review_text
);

-- Filter support tickets about safety concerns
SELECT
    t.ticket_id,
    t.subject,
    t.priority
FROM support_tickets t
WHERE AI_FILTER(
    'This ticket describes a potential safety concern or hazard: '
    || t.description
);


-- -----------------------------------------------------------------
-- 2E. AI_SUMMARIZE — Summarize Text
-- -----------------------------------------------------------------

-- Summarize individual reviews
SELECT
    r.review_id,
    SNOWFLAKE.CORTEX.SUMMARIZE(r.review_text) AS summary
FROM reviews r
WHERE LENGTH(r.review_text) > 80;

-- Aggregate summarization: summarize ALL reviews per product
SELECT
    p.product_name,
    AI_SUMMARIZE_AGG(r.review_text) AS all_reviews_summary
FROM reviews r
  JOIN products p ON r.product_id = p.product_id
GROUP BY p.product_name;


-- -----------------------------------------------------------------
-- 2F. AI_TRANSLATE — Multi-language Support
-- -----------------------------------------------------------------

-- Translate product descriptions to Spanish and Japanese
SELECT
    product_name,
    AI_TRANSLATE(description, 'en', 'es') AS description_es,
    AI_TRANSLATE(description, 'en', 'ja') AS description_ja
FROM products
LIMIT 4;


-- -----------------------------------------------------------------
-- 2G. AI_EXTRACT — Extract Structured Info from Text
-- -----------------------------------------------------------------
SELECT
    t.ticket_id,
    AI_EXTRACT(
        t.description,
        {'product_mentioned': 'product name if any',
         'issue_type':        'type of issue in one word',
         'urgency':           'low, medium, or high',
         'action_requested':  'what the customer wants'}
    ) AS extracted_info
FROM support_tickets t;


-- -----------------------------------------------------------------
-- 2H. AI_AGG — Aggregate Insights Across Multiple Rows
-- -----------------------------------------------------------------

-- Aggregate insights from all support tickets
SELECT
    AI_AGG(
        description,
        'Identify the top 3 recurring themes across these support tickets '
        || 'and suggest process improvements for each.'
    ) AS ticket_insights
FROM support_tickets;

-- Per-product review insights
SELECT
    p.product_name,
    COUNT(r.review_id) AS review_count,
    AI_AGG(
        r.review_text,
        'Summarize the key strengths and weaknesses mentioned in these reviews.'
    ) AS strengths_and_weaknesses
FROM reviews r
  JOIN products p ON r.product_id = p.product_id
GROUP BY p.product_name
HAVING COUNT(r.review_id) >= 2;



