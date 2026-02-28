# Lab 3: Intelligent Car Assistant with RAG & Routing Agent

Welcome to Lab 3! In this lab, we build an **Intelligent Car Assistant** that demonstrates how to combine **Retrieval-Augmented Generation (RAG)** with a **Routing Agent**. 

Instead of a single monolithic prompt, this application uses a "Router" Large Language Model (LLM) to intelligently classify a user's question and dynamically route it to one of three specialized sub-agents:
1. **RAG Agent**: Searches a Snowflake database for car reviews and owner opinions.
2. **News Agent**: Uses SerpAPI to search the live web for the latest automotive news and press releases.
3. **Maps Agent**: Uses the Google Maps API to locate nearby car dealerships and service centers.

---

## 🏗️ Architecture Overview

When a user submits a query via the Streamlit interface, the following sequence occurs:

1. **Routing (`router_agent.py`)**: The query is sent to a Cortex LLM (`claude-3-5-sonnet`) with instructions to classify the intent. It outputs a JSON payload deciding which of the three tools is best suited for the task.
2. **Execution (`routing_chain.py`)**: The application dynamically executes the chosen tool's specific Python script (e.g., `tools/rag_agent.py`, `tools/news_agent.py`, or `tools/map_agent.py`).
3. **Synthesis (`routing_chain.py`)**: The raw technical output from the selected tool is passed *back* to Cortex to be synthesized into a friendly, conversational response.
4. **UI Display (`app.py`)**: The final conversational response is returned to the user in the Streamlit chat interface, along with an expandable "Agent Details" section showing the exact tool the router selected.

---

## 📋 Prerequisites & Setup

To run this application, you need to configure your environment variables securely.

1. Ensure your Python virtual environment is activated:
   ```bash
   source .venv/bin/activate
   ```

2. Create a `.env` file in the root of the `Lab-3-RAG+RoutingAgent` directory (if it doesn't exist) and populate it with the following keys:

   ```env
   # Snowflake Credentials (for the RAG Agent and Cortex LLMs)
   SNOWFLAKE_ACCOUNT=your_account_identifier
   SNOWFLAKE_USER=your_username
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_ROLE=your_role
   SNOWFLAKE_WAREHOUSE=your_warehouse
   SNOWFLAKE_DATABASE=your_database
   SNOWFLAKE_SCHEMA=your_schema

   # External API Keys (for the Routing Tools)
   SERPAPI_API_KEY=your_serpapi_key
   GOOGLE_MAPS_API_KEY=your_google_maps_key
   ```
   *Note: `SERPAPI_API_KEY` is required for the News Agent. `GOOGLE_MAPS_API_KEY` is required for the Maps Agent.*

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Running the Application

Once your environment is configured, start the Streamlit server:

```bash
streamlit run app.py
```

The application will open in your default web browser (usually at `http://localhost:8501`).

### Try These Example Queries:

Test the Routing Agent's logic by asking different types of questions:

* **Trigger the RAG Agent**: *"What do owners think about the reliability of the Toyota Camry?"*
* **Trigger the News Agent**: *"Are there any recent news articles or recalls for the Rivian R1S?"*
* **Trigger the Maps Agent**: *"Find me a Honda dealership near Seattle, Washington."*

Watch the Streamlit UI! The status expander will show you exactly which tool the Router decided to use in real-time.
