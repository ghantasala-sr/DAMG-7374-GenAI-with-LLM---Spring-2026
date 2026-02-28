"""
Snowflake Session Factory for LangChain Integration.

Provides utility functions to create Snowflake sessions and
LangChain ChatSnowflake instances for the Car Analyst application.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from snowflake.snowpark import Session
from langchain_snowflake import ChatSnowflake, create_session_from_env

load_dotenv()


def get_snowflake_session() -> Session:
    """
    Create a Snowflake session from environment variables.
    
    Uses langchain-snowflake's built-in session factory which reads:
    - SNOWFLAKE_ACCOUNT
    - SNOWFLAKE_USER
    - SNOWFLAKE_PASSWORD
    - SNOWFLAKE_WAREHOUSE (optional)
    - SNOWFLAKE_DATABASE (optional)
    - SNOWFLAKE_SCHEMA (optional)
    
    Returns:
        Session: Configured Snowflake Snowpark session
    """
    return create_session_from_env()


def get_chat_model(
    model: str = "claude-3-5-sonnet",
    temperature: float = 0.7,
    session: Optional[Session] = None
) -> ChatSnowflake:
    """
    Create a ChatSnowflake instance for LLM inference via Cortex.
    
    Args:
        model: Cortex model name (claude-3-5-sonnet, mixtral-8x7b, llama3.1-70b, etc.)
        temperature: Sampling temperature (0.0 to 1.0)
        session: Optional existing Snowflake session. Creates new if not provided.
    
    Returns:
        ChatSnowflake: Configured LangChain chat model
    
    Available Models:
        - claude-3-5-sonnet: Best for complex reasoning and analysis
        - mixtral-8x7b: Fast, good for summarization
        - llama3.1-70b: Strong general purpose
        - llama3.1-8b: Lightweight, fast responses
        - llama4-maverick: Latest Llama model
    """
    if session is None:
        session = get_snowflake_session()
    
    return ChatSnowflake(
        session=session,
        model=model,
        temperature=temperature
    )


def get_snowflake_config() -> dict:
    """
    Get Snowflake configuration from environment variables.
    
    Returns:
        dict: Configuration dictionary with database, schema, warehouse info
    """
    return {
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "user": os.getenv("SNOWFLAKE_USER"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": os.getenv("SNOWFLAKE_DATABASE"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA"),
        "role": os.getenv("SNOWFLAKE_ROLE")
    }
