from router_agent import route_query
from tools.rag_agent import run_rag_agent
from tools.news_agent import run_news_agent
from tools.map_agent import run_maps_agent
from utils.snowflake_connection import get_snowflake_connection, run_cortex_complete

SYNTHESIZER_PROMPT = """You are a friendly, knowledgeable car assistant.
Convert the following technical tool output into a natural, engaging response for the user.
Keep it concise, helpful, and conversational.

Tool Used: {tool}
Tool Output: {tool_output}
Original User Question: {user_query}
"""

TOOL_MAP = {
    "rag_agent":   run_rag_agent,
    "news_agent":  run_news_agent,
    "maps_agent":  run_maps_agent
}

def run_routing_chain(user_query: str) -> dict:
    # Step 1: Route the query
    routing_decision = route_query(user_query)
    tool_name = routing_decision.get("tool", "rag_agent")
    refined_query = routing_decision.get("query", user_query)

    # Step 2: Execute the selected tool
    tool_fn = TOOL_MAP.get(tool_name, run_rag_agent)
    tool_output = tool_fn(refined_query)

    # Step 3: Synthesize final response
    conn = get_snowflake_connection()
    prompt = SYNTHESIZER_PROMPT.format(
        tool=tool_name,
        tool_output=tool_output,
        user_query=user_query
    )
    final_response = run_cortex_complete("claude-3-5-sonnet", prompt, conn)
    conn.close()

    return {
        "tool_used": tool_name,
        "refined_query": refined_query,
        "tool_output": tool_output,
        "final_response": final_response
    }