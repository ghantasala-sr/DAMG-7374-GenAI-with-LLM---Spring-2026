# Multi-Agent Reflection Pipeline

A multi-agent research and article-writing pipeline built with **Snowflake Cortex LLMs** and **LangGraph**. The system decomposes a topic, researches it in parallel, writes an article, and iteratively refines it through a reflection loop until quality thresholds are met.

## Architecture

```
Supervisor
   -> Researcher x3 (parallel via Send API)
      -> Generator
         <-> Reflector
         <-> Evaluator (score >= 8.0 or max 3 revisions)
            -> Finalizer
```

### Agents

| Agent | Role | LLM Config |
|---|---|---|
| **Supervisor** | Decomposes the topic into 3 sub-topics | mistral-large2, temp=0.2 |
| **Researcher** (x3) | Researches each sub-topic in parallel | mistral-large2, temp=0.7 |
| **Generator** | Writes/revises the article draft | mistral-large2, temp=0.7 |
| **Reflector** | Critiques the draft with structured scoring | mistral-large2, temp=0.2 |
| **Evaluator** | Decides accept or revise based on score | Rule-based (no LLM) |
| **Finalizer** | Formats the final output | Rule-based (no LLM) |

### Multi-Agent Patterns Demonstrated

1. **Sequential Handoffs** — Supervisor → Researchers → Generator → Reflector → Evaluator → Finalizer
2. **Parallel Processing** — Fan-out to 3 researchers via LangGraph `Send` API with `Annotated[list, operator.add]` reducer
3. **Reflection Loop** — Generator ↔ Reflector ↔ Evaluator iterative refinement cycle
4. **Hierarchical Supervisor** — Topic decomposition and task delegation
5. **Critic-Reviewer** — Structured critique with score, strengths, weaknesses, suggestions
6. **Structured Output** — JSON-based scoring and decision parsing with fallback handling

## Project Structure

```
Lab-5-MultiAgent/
├── .env              # Snowflake credentials (fill in before running)
├── config.py         # Snowflake session & LLM initialization
├── schemas.py        # Pydantic models and TypedDict state definitions
├── nodes.py          # All agent node functions
├── graph.py          # LangGraph StateGraph assembly and routing
├── main.py           # CLI entry point
├── app.py            # Streamlit frontend
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
pip install langchain-snowflake langgraph langchain-core python-dotenv streamlit
```

### 2. Configure Environment Variables

Fill in your Snowflake credentials in the `.env` file:

```
SNOWFLAKE_ACCOUNT=<your_account>
SNOWFLAKE_USER=<your_username>
SNOWFLAKE_PASSWORD=<your_password>
SNOWFLAKE_WAREHOUSE=<your_warehouse>
SNOWFLAKE_DATABASE=<your_database>
SNOWFLAKE_SCHEMA=<your_schema>
```

## Running

### CLI

```bash
python main.py
```

### Streamlit UI

```bash
streamlit run app.py
```

The Streamlit app provides:
- Sidebar with architecture diagram and patterns list
- Text input for custom research topics
- Live progress updates as each agent executes
- Metrics display (quality score, revision count, research pieces)
- Final article, expandable research materials, and critique details

## Key Technologies

- **langchain-snowflake** — `ChatSnowflake` and `create_session_from_env()` for Snowflake Cortex LLM access
- **LangGraph** — `StateGraph`, `Send` API, conditional edges for stateful multi-agent orchestration
- **Pydantic** — Structured output schemas (`SubTopics`, `Critique`, `EvalDecision`)
- **Streamlit** — Interactive frontend with `st.status` for live pipeline progress
