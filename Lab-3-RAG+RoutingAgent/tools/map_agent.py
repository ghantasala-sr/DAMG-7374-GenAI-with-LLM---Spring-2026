import googlemaps
import os
from dotenv import load_dotenv
from utils.snowflake_connection import get_snowflake_connection, run_cortex_complete

load_dotenv()

MAPS_PROMPT = """You are a helpful car dealership finder. Based on the following 
dealership search results, provide a clear, friendly answer to the user.

Search Results:
{places}

User Question: {query}
"""

def run_maps_agent(query: str) -> str:
    gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

    # Search for dealerships / service centers
    places = gmaps.places(f"car dealership {query}")
    results = places.get("results", [])[:4]

    places_text = ""
    for p in results:
        name = p.get("name")
        addr = p.get("formatted_address", "Address not available")
        rating = p.get("rating", "N/A")
        places_text += f"📍 {name}\n   Address: {addr}\n   Rating: {rating}/5\n\n"

    if not places_text:
        return "No dealerships found near that location."

    conn = get_snowflake_connection()
    prompt = MAPS_PROMPT.format(places=places_text, query=query)
    answer = run_cortex_complete("llama4-maverick", prompt, conn)
    conn.close()
    return answer