-- =====================================================================
-- WORKSHEET 3 : CORTEX AI — EMBEDDINGS, SIMILARITY & SEARCH
-- =====================================================================
-- Objective: Use vector embeddings for semantic search, similarity
--            matching, and build a basic RAG-style pipeline.
-- =====================================================================
USE SCHEMA lab_db.lab_schema;
USE WAREHOUSE lab_wh;
-- -----------------------------------------------------------------
-- 3A. AI_EMBED — Generate Vector Embeddings
-- -----------------------------------------------------------------

-- Create a table with product embeddings
CREATE OR REPLACE TABLE product_embeddings AS
SELECT
    product_id,
    product_name,
    description,
    AI_EMBED('e5-base-v2', description) AS embedding
FROM products;

-- View the embedding (it's a high-dimensional vector)
SELECT 
    product_name,
    embedding
FROM product_embeddings
LIMIT 3;


-- -----------------------------------------------------------------
-- 3B. AI_SIMILARITY — Semantic Similarity Between Texts
-- -----------------------------------------------------------------

-- Find products similar to a user query using AI_SIMILARITY
SELECT
    product_name,
    description,
    AI_SIMILARITY(
        'I need something to help me with coding and programming',
        description
    ) AS similarity_score
FROM products
ORDER BY similarity_score DESC
LIMIT 5;

-- Find products similar to another product
SELECT
    a.product_name AS source_product,
    b.product_name AS similar_product,
    AI_SIMILARITY(a.description, b.description) AS similarity
FROM products a
  CROSS JOIN products b
WHERE a.product_id = 1  -- Smart Home Hub
  AND a.product_id != b.product_id
ORDER BY similarity DESC;


-- -----------------------------------------------------------------
-- 3C. VECTOR COSINE SIMILARITY (Manual Approach)
-- -----------------------------------------------------------------
-- Compare two embeddings using VECTOR_COSINE_SIMILARITY
SELECT
    a.product_name AS product_a,
    b.product_name AS product_b,
    VECTOR_COSINE_SIMILARITY(a.embedding, b.embedding) AS cosine_sim
FROM product_embeddings a
  CROSS JOIN product_embeddings b
WHERE a.product_id < b.product_id
ORDER BY cosine_sim DESC;


-- -----------------------------------------------------------------
-- 3D. SEMANTIC SEARCH — Find Relevant Reviews for a Question
-- -----------------------------------------------------------------

-- "RAG-lite": Embed a question, find relevant reviews, then answer
-- Step 1: Find most relevant reviews to the question
SET search_query = 'Are there any durability or quality issues?';

SELECT
    r.review_id,
    p.product_name,
    r.review_text,
    AI_SIMILARITY($search_query, r.review_text) AS relevance
FROM reviews r
  JOIN products p ON r.product_id = p.product_id
ORDER BY relevance DESC
LIMIT 3;

-- Step 2: Use the top results as context for AI_COMPLETE
WITH relevant_reviews AS (
    SELECT
        p.product_name,
        r.review_text,
        AI_SIMILARITY($search_query, r.review_text) AS relevance
    FROM reviews r
      JOIN products p ON r.product_id = p.product_id
    ORDER BY relevance DESC
    LIMIT 3
)
SELECT AI_COMPLETE(
    'claude-4-sonnet',
    'Based on the following customer reviews, answer the question: "' || $search_query || '"' ||
    CHR(10) || CHR(10) ||
    'Reviews:' || CHR(10) ||
    LISTAGG(product_name || ': ' || review_text, '\n') WITHIN GROUP (ORDER BY relevance DESC)
) AS ai_answer
FROM relevant_reviews;


-- -----------------------------------------------------------------
-- 3E. CORTEX SEARCH SERVICE (Enterprise Semantic Search)
-- -----------------------------------------------------------------
-- Create a Cortex Search Service for natural language queries
-- over your review data

CREATE OR REPLACE CORTEX SEARCH SERVICE review_search_service
  ON review_text
  ATTRIBUTES product_id
  WAREHOUSE = lab_wh
  TARGET_LAG = '1 hour'
  AS (
    SELECT
        r.review_id,
        r.review_text,
        r.product_id,
        r.rating,
        p.product_name
    FROM reviews r
      JOIN products p ON r.product_id = p.product_id
  );

-- Note: Query Cortex Search via the REST API or Snowflake Intelligence.
-- Example query pattern (via Python / API):
-- POST /api/v2/databases/LAB_DB/schemas/LAB_SCHEMA/cortex-search-services/REVIEW_SEARCH_SERVICE:query
-- { "query": "product quality issues", "columns": ["review_text","product_name"], "limit": 5 }


