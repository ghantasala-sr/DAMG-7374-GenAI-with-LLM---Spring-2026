from dotenv import load_dotenv
from langchain_snowflake import ChatSnowflake, create_session_from_env

load_dotenv()

session = create_session_from_env()

llm = ChatSnowflake(
    session=session,
    model="mistral-large2",
    temperature=0.7,
    max_tokens=2048,
)

llm_low_temp = ChatSnowflake(
    session=session,
    model="mistral-large2",
    temperature=0.2,
    max_tokens=1024,
)
