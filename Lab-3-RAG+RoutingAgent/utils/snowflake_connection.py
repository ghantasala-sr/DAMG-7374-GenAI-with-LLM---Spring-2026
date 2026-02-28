import snowflake.connector
from dotenv import load_dotenv
import os

load_dotenv()

def get_snowflake_connection():
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE")
    )

def run_cortex_complete(model: str, prompt: str, conn) -> str:
    """Call Snowflake Cortex Complete for LLM inference.

    Uses Snowflake $$ dollar-quoting to embed the prompt as a string literal,
    avoiding the pyformat TypeError that occurs when the prompt contains
    % characters (common in JSON-structured router prompts).
    """
    cur = conn.cursor()
    # Dollar-quote the prompt to safely handle %, ', \, and other special chars.
    # If the prompt itself contains $$, escape it — extremely rare in practice.
    safe_prompt = prompt.replace("$$", "\\$\\$")
    sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', $${safe_prompt}$$) AS RESPONSE"
    cur.execute(sql)
    row = cur.fetchone()
    cur.close()
    return row[0] if row else ""