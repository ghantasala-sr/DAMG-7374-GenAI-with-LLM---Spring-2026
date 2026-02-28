# Lab 4: Parallel Agent Architecture

A **Full-Stack Car Analyst** system demonstrating parallel agent execution using Snowflake Cortex LLMs and the `langchain-snowflake` package.

## Overview

This lab builds upon Lab 3's sequential routing agent by introducing **parallel execution** of multiple specialized AI analysts. Instead of routing to a single tool, the system decomposes complex queries and executes multiple analysts concurrently, providing comprehensive automotive intelligence in less time.

### Architecture Comparison

| Lab 3 (Sequential) | Lab 4 (Parallel) |
|-------------------|------------------|
| Router → 1 Tool → Response | Planner → N Tools (parallel) → Synthesized Report |
| Single data source | Multiple data sources combined |
| ~3-4s response time | ~1.5-2s response time |

## Architecture

```
                         ┌──────────────────┐
                         │   USER QUERY     │
                         └────────┬─────────┘
                                  ▼
                         ┌──────────────────┐
                         │  PLANNER AGENT   │
                         │  (Decomposition) │
                         └────────┬─────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
          ▼                       ▼                       ▼
   ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
   │   REVIEW    │        │   MARKET    │        │  PURCHASE   │
   │   ANALYST   │        │   ANALYST   │        │   ANALYST   │
   │  (Cortex    │        │  (News +    │        │  (Budget +  │
   │   Search)   │        │  Sentiment) │        │   Maps)     │
   └──────┬──────┘        └──────┬──────┘        └──────┬──────┘
          │     concurrent       │      concurrent      │
          └───────────────────────┼───────────────────────┘
                                  ▼
                         ┌──────────────────┐
                         │   SYNTHESIZER    │
                         │ (Combine Reports)│
                         └────────┬─────────┘
                                  ▼
                         ┌──────────────────┐
                         │  ANALYST REPORT  │
                         └──────────────────┘
```

## Features

### Specialized Analysts

| Analyst | Specialty | Data Sources | Cortex Model |
|---------|-----------|--------------|--------------|
| **Review Analyst** | Car reviews, ratings, sentiment, reliability | Cortex Search Service (RAG) | claude-3-5-sonnet |
| **Market Analyst** | Market trends, pricing, competitive analysis | SerpAPI News + Cortex Sentiment | mixtral-8x7b |
| **Purchase Analyst** | Budget recommendations, dealer locations | Google Maps API | claude-3-5-sonnet |

### Key Technologies

- **`langchain-snowflake`** - Native LangChain integration for Snowflake Cortex
- **`ChatSnowflake`** - LLM chat interface for Cortex models
- **`SnowflakeCortexSearchRetriever`** - RAG retrieval from Cortex Search
- **`CortexSentimentTool`** - Built-in sentiment analysis
- **`asyncio`** - True parallel execution with async/await
- **Streamlit** - Interactive dashboard with real-time progress

## Project Structure

```
Lab-4-Parallelization/
├── app.py                      # Streamlit dashboard
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── README.md                   # This file
│
├── analysts/                   # Specialized analyst agents
│   ├── __init__.py
│   ├── base_analyst.py         # Abstract base class
│   ├── review_analyst.py       # RAG-based review analysis
│   ├── market_analyst.py       # News & sentiment analysis
│   └── purchase_analyst.py     # Budget & dealer analysis
│
├── orchestrator/               # Parallel execution framework
│   ├── __init__.py
│   ├── planner.py              # Query decomposition
│   ├── parallel_executor.py    # Async parallel runner
│   └── synthesizer.py          # Result aggregation
│
└── utils/                      # Utilities
    ├── __init__.py
    └── session.py              # Snowflake session factory
```

## Setup

### Prerequisites

- Python 3.9 - 3.11 (langchain-snowflake requires <3.12)
- Snowflake account with Cortex enabled
- Cortex Search Service configured (for Review Analyst)
- API keys for SerpAPI and Google Maps (optional)

### Installation

1. **Navigate to the lab directory:**
   ```bash
   cd Lab-4-Parallelization
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```env
   # Snowflake Connection (Required)
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_USER=your_user
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_WAREHOUSE=your_warehouse
   SNOWFLAKE_DATABASE=your_database
   SNOWFLAKE_SCHEMA=your_schema
   SNOWFLAKE_ROLE=your_role

   # External APIs (Optional - for full functionality)
   SERPAPI_API_KEY=your_serpapi_key
   GOOGLE_MAPS_API_KEY=your_google_maps_key

   # LangSmith Tracing (Optional)
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_langsmith_key
   LANGCHAIN_PROJECT=car-analyst
   ```

### Cortex Search Service Setup

The Review Analyst requires a Cortex Search Service. Create one in Snowflake:

```sql
-- Create the search service on your car reviews table
CREATE OR REPLACE CORTEX SEARCH SERVICE CAR_REVIEW_SEARCH_SERVICE
  ON REVIEW_TEXT
  ATTRIBUTES CAR_MAKE, CAR_MODEL, REVIEW_YEAR, RATING
  WAREHOUSE = your_warehouse
  TARGET_LAG = '1 hour'
  AS (
    SELECT 
      CAR_MAKE,
      CAR_MODEL,
      REVIEW_YEAR,
      RATING,
      REVIEW_TEXT
    FROM your_car_reviews_table
  );
```

## Usage

### Run the Streamlit App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Example Queries

Try these queries to see the parallel analysis in action:

| Query | Analysts Engaged |
|-------|-----------------|
| "Compare Toyota RAV4 vs Honda CR-V for family use under $40k" | All 3 |
| "What do owners say about Tesla Model Y reliability?" | Review |
| "Latest news and market trends for electric SUVs" | Market |
| "Best hybrid sedan under $35k near Boston" | Purchase + Review |
| "Analyze Ford F-150 Lightning - reviews, pricing, and dealers" | All 3 |

### Programmatic Usage

```python
import asyncio
from utils.session import get_snowflake_session
from analysts import ReviewAnalyst, MarketAnalyst, PurchaseAnalyst
from orchestrator.planner import PlannerAgent
from orchestrator.parallel_executor import ParallelAnalystExecutor
from orchestrator.synthesizer import Synthesizer

# Initialize
session = get_snowflake_session()

# Create planner and get execution plan
planner = PlannerAgent(session=session)
plan = planner.plan("Compare RAV4 vs CR-V under $40k")

# Initialize selected analysts
analysts = {
    "review_analyst": ReviewAnalyst(session=session),
    "market_analyst": MarketAnalyst(session=session),
    "purchase_analyst": PurchaseAnalyst(session=session)
}

# Execute in parallel
executor = ParallelAnalystExecutor(timeout_seconds=60)
results = asyncio.run(executor.execute_parallel(
    analysts={k: analysts[k] for k in plan.analysts},
    queries=plan.sub_queries
))

# Synthesize results
synthesizer = Synthesizer(session=session)
report = synthesizer.synthesize(results, "Compare RAV4 vs CR-V", plan.synthesis_focus)
print(report["report"])
```

## How It Works

### 1. Query Planning

The **Planner Agent** analyzes incoming queries and determines:
- Which analysts to engage (1-3)
- Focused sub-queries for each analyst
- How to synthesize the results

```python
# Example planner output
{
    "analysts": ["review_analyst", "market_analyst", "purchase_analyst"],
    "sub_queries": {
        "review_analyst": "Toyota RAV4 vs Honda CR-V owner reviews and ratings",
        "market_analyst": "RAV4 CR-V market pricing trends 2024",
        "purchase_analyst": "Best family SUV under $40k near user location"
    },
    "synthesis_focus": "Compare both vehicles across reviews, market value, and purchase recommendations"
}
```

### 2. Parallel Execution

The **Parallel Executor** runs selected analysts concurrently using `asyncio.gather()`:

```python
async def execute_parallel(self, analysts, queries):
    tasks = [
        self._execute_single_analyst(analyst, query)
        for name, analyst in analysts.items()
    ]
    await asyncio.gather(*tasks)  # True parallel execution
```

### 3. Result Synthesis

The **Synthesizer** combines all analyst reports into a unified response:
- Executive summary
- Key findings from each analyst
- Data highlights table
- Final recommendation
- Confidence assessment

## Performance

| Metric | Sequential (Lab 3) | Parallel (Lab 4) | Improvement |
|--------|-------------------|------------------|-------------|
| Single analyst | ~1.5s | ~1.5s | - |
| Two analysts | ~3.0s | ~1.7s | **1.8x faster** |
| Three analysts | ~4.5s | ~2.0s | **2.3x faster** |

## Troubleshooting

### Common Issues

1. **`schema Field required` error**
   - Ensure `SNOWFLAKE_DATABASE` and `SNOWFLAKE_SCHEMA` are set in `.env`

2. **`langchain-snowflake` installation fails**
   - Use Python 3.11 or earlier (not 3.12+)
   - Run: `python3.11 -m venv .venv`

3. **Cortex Search Service not found**
   - Verify the service exists: `SHOW CORTEX SEARCH SERVICES`
   - Check database/schema match your `.env` settings

4. **News/Maps features not working**
   - These require `SERPAPI_API_KEY` and `GOOGLE_MAPS_API_KEY`
   - The system gracefully handles missing API keys

### Debug Mode

Enable LangSmith tracing for detailed execution logs:

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your_key
```

## References

- [langchain-snowflake GitHub](https://github.com/langchain-ai/langchain-snowflake)
- [Snowflake Cortex Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex)
- [Cortex Search Service](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search)
- [LangChain Documentation](https://python.langchain.com/docs/)

## License

Educational use - DAMG 7374 Lab Session
