# DAMG 7374: Data Engineering : Impact of Generative AI with LLMs — Spring 2026

[![Northeastern University](https://img.shields.io/badge/Northeastern%20University-red?style=for-the-badge)](https://www.northeastern.edu/)
[![Course](https://img.shields.io/badge/DAMG%207374-Spring%202026-blue?style=for-the-badge)]()

## 📋 Course Overview

This repository contains lab materials and resources for **DAMG 7374: Data Engineering : Impact of Generative AI with LLMs**, offered during the Spring 2026 semester at Northeastern University.

The course explores the intersection of Generative AI, Large Language Models, and modern data engineering practices — covering tools and frameworks essential to building scalable, AI-driven data pipelines.

**Instructor:** Professor Kishore Aaradhya  
**Teaching Assistant:** Srinivasa Rithik Ghantasala

---

## 🗂️ Repository Structure

```
DAMG-7374-GenAI-with-LLM---Spring-2026/
│
├── Lab_1_Snowflake/                    # Lab 1 – Introduction to Snowflake
│   ├── Worksheet 1.sql
│   ├── Worksheet 2.sql
│   ├── Worksheet 3.sql
│   ├── Worksheet 4.sql
│   └── Worksheet 5.sql
│
├── Lab-2-dbt-tutorial/                 # Lab 2 – dbt (Data Build Tool) Tutorial
│   ├── my_dbt_project/                 # dbt project with models, tests & seeds
│   │   ├── models/
│   │   ├── seeds/
│   │   ├── tests/
│   │   ├── macros/
│   │   ├── analyses/
│   │   ├── snapshots/
│   │   └── dbt_project.yml
│   ├── setup_snowflake.sql
│   ├── cleanup_dbt_objects.sql
│   └── requirements.txt
│
├── Lab-3-RAG+RoutingAgent/             # Lab 3 – RAG & Routing Agent
│   ├── tools/                          # Specialized agent tools
│   │   ├── map_agent.py
│   │   ├── news_agent.py
│   │   └── rag_agent.py
│   ├── utils/
│   │   └── snowflake_connection.py
│   ├── app.py
│   ├── router_agent.py
│   ├── routing_chain.py
│   ├── requirements.txt
│   └── README.md
│
├── Lab-4-Parallelization/              # Lab 4 – Parallelization with LLM Agents
│   ├── analysts/                       # Analyst agent modules
│   │   ├── base_analyst.py
│   │   ├── market_analyst.py
│   │   ├── purchase_analyst.py
│   │   └── review_analyst.py
│   ├── orchestrator/                   # Orchestration logic
│   │   ├── parallel_executor.py
│   │   ├── planner.py
│   │   └── synthesizer.py
│   ├── utils/
│   │   └── session.py
│   ├── agent_app.py
│   ├── app.py
│   ├── requirements.txt
│   └── README.md
│
└── README.md
```

---

## 🧪 Lab Sessions

| Lab | Topic | Status |
|-----|-------|--------|
| Lab 1 | Snowflake — Cloud Data Warehousing | ✅ Available |
| Lab 2 | dbt — Data Build Tool Tutorial | ✅ Available |
| Lab 3 | RAG + Routing Agent with LLMs | ✅ Available |
| Lab 4 | Parallelization with LLM Agents | ✅ Available |

---

## 🛠️ Technologies & Tools

- **Snowflake** — Cloud data platform & warehousing
- **dbt (Data Build Tool)** — SQL-based data transformation framework
- **Large Language Models (LLMs)** — Generative AI foundations
- **RAG (Retrieval-Augmented Generation)** — Knowledge-grounded LLM pipelines
- **LangChain / LangGraph** — LLM orchestration and routing agent framework
- **Python** — Scripting and data pipeline development
- **SQL** — Database querying and stored procedures

---

## 🚀 Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ghantasala-sr/DAMG-7374-GenAI-with-LLM---Spring-2026.git
   cd DAMG-7374-GenAI-with-LLM---Spring-2026
   ```

2. **Navigate to the lab folder** you want to work on and follow the instructions in the respective directory.

3. **Prerequisites:**
   - A Snowflake account
   - Python 3.9+ installed
   - dbt CLI installed (`pip install dbt-snowflake`)
   - A code editor (VS Code recommended)

---

## 📌 Important Notes

- All lab materials are intended for enrolled students of DAMG 7374 — Spring 2026.
- New labs will be pushed to this repository as the semester progresses.
- For questions or issues, please reach out during office hours or raise an issue on this repository.

---

## 📄 License

This repository is for academic use as part of the Northeastern University curriculum.
