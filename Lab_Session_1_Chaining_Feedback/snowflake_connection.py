import snowflake.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_snowflake_connection():
    """Get Snowflake connection using environment variables"""
    try:
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),  # This is your PAT token
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA")
        )
        return conn
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def call_cortex_complete(prompt: str, model: str = 'claude-3-5-sonnet') -> str:
    """
    Call Snowflake Cortex Complete function with specified model
    
    Args:
        prompt: The prompt to send to the model
        model: The model to use (default: claude-3-5-sonnet)
    
    Returns:
        Generated response from the model
    """
    conn = get_snowflake_connection()
    if not conn:
        return "Connection failed"
    
    try:
        cursor = conn.cursor()
        
        # Escape single quotes
        escaped_prompt = prompt.replace("'", "''")
        
        query = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            '{model}',
            '{escaped_prompt}'
        ) as result
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        return result[0] if result else "No result"
    except Exception as e:
        return f"Error with model {model}: {e}"
    finally:
        conn.close()