"""
Lab 7 - Evaluation & Observation
Configuration: Snowflake session initialization and LLM setup.
"""

import os
from dotenv import load_dotenv
from snowflake.snowpark import Session
from langchain_snowflake import ChatSnowflake

# ── Load environment variables ───────────────────────────────────────────────
load_dotenv()

# ── Snowflake Session ────────────────────────────────────────────────────────
sf_config = {
    "account":   os.getenv("SNOWFLAKE_ACCOUNT"),
    "user":      os.getenv("SNOWFLAKE_USER"),
    "password":  os.getenv("SNOWFLAKE_PASSWORD"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
    "database":  os.getenv("SNOWFLAKE_DATABASE"),
    "schema":    os.getenv("SNOWFLAKE_SCHEMA"),
    "role":      os.getenv("SNOWFLAKE_ROLE"),
}

session = Session.builder.configs(sf_config).create()

# ── LLM instances ────────────────────────────────────────────────────────────
# Primary LLM — higher temperature for natural responses
llm = ChatSnowflake(
    model="llama4-maverick",
    snowflake_session=session,
    temperature=0.7,
    max_tokens=2048,
)

# Strict LLM — low temperature for guardrail / evaluation judgments
llm_strict = ChatSnowflake(
    model="llama4-maverick",
    snowflake_session=session,
    temperature=0.1,
    max_tokens=1024,
)

# ── Constants ────────────────────────────────────────────────────────────────
COMPANY_NAME = "TechCorp"
COMPETITOR_NAMES = ["CompetitorA", "CompetitorB", "RivalCo"]
MAX_REVISIONS = 2
