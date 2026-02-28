import os
import json
from snowflake.core import Root
from snowflake.snowpark import Session
from dotenv import load_dotenv
from utils.snowflake_connection import get_snowflake_connection, run_cortex_complete

load_dotenv()

RAG_PROMPT = """You are a car reviews expert. Using the following car reviews retrieved
from a Snowflake Cortex Search Service, answer the user's question with specific
details, ratings, and insights.

Retrieved Reviews:
{context}

User Question: {query}

Provide a helpful, detailed answer based on the reviews above.
"""

def get_snowpark_session() -> Session:
    """Snowpark session — required for the Cortex Search Python API."""
    return Session.builder.configs({
        "user":      os.getenv("SNOWFLAKE_USER"),
        "password":  os.getenv("SNOWFLAKE_PASSWORD"),
        "account":   os.getenv("SNOWFLAKE_ACCOUNT"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database":  os.getenv("SNOWFLAKE_DATABASE"),
        "schema":    os.getenv("SNOWFLAKE_SCHEMA"),
        "role":      os.getenv("SNOWFLAKE_ROLE")
    }).create()

def run_rag_agent(query: str) -> str:
    # Step 1: Use Snowpark Root to access the Cortex Search Service
    session = get_snowpark_session()
    root = Root(session)

    svc = (
        root
        .databases[os.getenv("SNOWFLAKE_DATABASE")]
        .schemas[os.getenv("SNOWFLAKE_SCHEMA")]
        .cortex_search_services["CAR_REVIEW_SEARCH_SERVICE"]
    )

    # Step 2: Query the service — low latency, production-ready
    resp = svc.search(
        query=query,
        columns=["CAR_MAKE", "CAR_MODEL", "REVIEW_YEAR", "RATING", "REVIEW_TEXT"],
        limit=3
    )
    results = resp.results  # list of dicts

    # Step 3: Build context block
    context = ""
    for r in results:
        context += (
            f"[{r.get('CAR_MAKE')} {r.get('CAR_MODEL')} {r.get('REVIEW_YEAR')}]"
            f" Rating: {r.get('RATING')}/5\n"
            f"{r.get('REVIEW_TEXT')}\n\n"
        )
    session.close()

    if not context:
        return "No relevant car reviews found for this query."

    # Step 4: LLM synthesis over retrieved context
    conn = get_snowflake_connection()
    prompt = RAG_PROMPT.format(context=context, query=query)
    answer = run_cortex_complete("claude-3-5-sonnet", prompt, conn)
    conn.close()
    return answer