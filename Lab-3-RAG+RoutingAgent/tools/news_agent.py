import requests
import os
from dotenv import load_dotenv
from utils.snowflake_connection import get_snowflake_connection, run_cortex_complete

load_dotenv()

NEWS_PROMPT = """You are an automotive news analyst. Summarize the following 
news results about cars in a concise, helpful way for a car buyer.

News Results:
{news}

User Question: {query}
"""

def run_news_agent(query: str) -> str:
    api_key = os.getenv("SERPAPI_API_KEY")
    params = {
        "q": f"automotive cars {query}",
        "api_key": api_key,
        "num": 5,
        "tbm": "nws"
    }
    response = requests.get("https://serpapi.com/search", params=params)
    results = response.json().get("news_results", [])

    news_text = ""
    for item in results:
        news_text += f"Title: {item.get('title')}\n"
        news_text += f"Snippet: {item.get('snippet')}\n"
        news_text += f"Source: {item.get('source')} | Date: {item.get('date')}\n\n"

    if not news_text:
        return "No recent news found for this query."

    conn = get_snowflake_connection()
    prompt = NEWS_PROMPT.format(news=news_text, query=query)
    answer = run_cortex_complete("mixtral-8x7b", prompt, conn)
    conn.close()
    return answer