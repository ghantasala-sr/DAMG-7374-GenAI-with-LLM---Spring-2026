import json
from utils.snowflake_connection import get_snowflake_connection, run_cortex_complete

ROUTER_PROMPT = """You are a routing agent for a Car Assistant application.
Analyze the user query and decide which ONE tool to use.

Available tools:
- rag_agent     : For questions about car reviews, ratings, owner experiences, comparisons
- news_agent    : For latest automotive news, new model announcements, industry updates
- maps_agent    : For finding car dealerships, service centers, nearby locations

Respond ONLY with a valid JSON object in this exact format:
{{"tool": "<tool_name>", "query": "<refined_query_for_the_tool>"}}

User query: {query}
"""

def route_query(user_query: str) -> dict:
    conn = get_snowflake_connection()
    prompt = ROUTER_PROMPT.format(query=user_query)
    response = run_cortex_complete("claude-3-5-sonnet", prompt, conn)
    conn.close()

    # Strip markdown fences if present
    clean = response.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        # Fallback to RAG if parsing fails
        return {"tool": "rag_agent", "query": user_query}