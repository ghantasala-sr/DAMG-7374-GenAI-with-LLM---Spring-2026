import os
import json
import uuid
import time
from datetime import datetime
from typing import Annotated, Optional
from typing_extensions import TypedDict

import streamlit as st
from dotenv import load_dotenv

from langchain_core.messages import (
    HumanMessage, AIMessage, SystemMessage, RemoveMessage, trim_messages,
)
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from snowflake.snowpark import Session
from langchain_snowflake import ChatSnowflake

load_dotenv()

st.set_page_config(
    page_title="Lab 6: Memory Management",
    page_icon=":material/psychology:",
    layout="wide",
)

FACT_EXTRACTION_PROMPT = """You are a memory extraction assistant.
Given a user message, extract any personal facts worth remembering.
Return ONLY a valid JSON array of strings. No markdown. Empty array if nothing notable.

Examples:
  Input : "I'm a data scientist at Google working on NLP"
  Output: ["Works as data scientist at Google", "Specializes in NLP"]
  Input : "What's the weather like?"
  Output: []
"""

EPISODE_SUMMARY_PROMPT = """You are a memory logging assistant.
Summarize the following conversation as a single-line episode entry.
Format: "<1-sentence summary>"
Return ONLY the formatted line, nothing else."""

PROCEDURE_UPDATE_PROMPT = """Analyze the user message for explicit behavior preferences.
If found, return: {"update": true, "rule": "<new rule>"}
Otherwise return: {"update": false}
Return ONLY valid JSON."""

DEFAULT_PROCEDURES = [
    "Be concise and technical.",
    "Use code examples when explaining technical concepts.",
    "Mention Snowflake-specific alternatives when relevant.",
]

MEMORY_DESCRIPTIONS = {
    "No Memory": "Agent has **zero recall**. Every message starts fresh — it cannot remember anything from previous turns.",
    "Full History": "**All messages** are stored in a checkpoint. The agent sees the entire conversation history every turn. Best for short sessions.",
    "Sliding Window": "Only the **last N tokens** of conversation are kept. Older messages are dropped to control token costs. Best for long chats.",
    "Summarization": "Old messages are **compressed into a summary**. Recent messages + summary are sent to the LLM. Best for very long sessions.",
    "Semantic Memory": "**Facts about the user** are extracted and stored in a persistent store. Facts survive across threads/sessions. (Long-term)",
    "Episodic Memory": "**Past session events** are logged as episode summaries. The agent recalls what happened in previous conversations. (Long-term)",
    "Procedural Memory": "**Behavioral rules** are detected and saved. The agent adapts HOW it responds based on user preferences. (Long-term)",
}

SUGGESTED_PROMPTS = {
    "No Memory": [
        "Hi, I'm Rithik, a data engineer at Snowflake.",
        "What's my name and what do I do?",
    ],
    "Full History": [
        "Hi, I'm Priya. I study ML engineering.",
        "I love NLP, especially summarization.",
        "What are my interests?",
    ],
    "Sliding Window": [
        "My name is Arjun and I know Python.",
        "I also know PyTorch and TensorFlow.",
        "I built a pipeline for 10M tweets.",
        "What are all my skills?",
    ],
    "Summarization": [
        "I'm Rohan, a cloud architect at a fintech.",
        "We use AWS and Snowflake for data.",
        "I'm building real-time fraud detection.",
        "The pipeline handles 50k txns/sec.",
        "We use Kafka and Flink.",
        "We integrated LLMs for anomaly explanation.",
        "What have we talked about?",
    ],
    "Semantic Memory": [
        "Hi, I'm Kavya, a senior ML engineer focusing on LLMOps.",
        "I use Snowflake Cortex, MLflow, and LangGraph.",
    ],
    "Episodic Memory": [
        "I fixed a Cortex Search bug — CHANGE_TRACKING wasn't enabled.",
        "ALTER TABLE SET CHANGE_TRACKING = TRUE fixed it!",
    ],
    "Procedural Memory": [
        "Explain what a vector database is.",
        "Please always respond in simple plain English, no jargon.",
        "Now explain embeddings.",
    ],
}


@st.cache_resource
def init_snowflake():
    params = {
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": os.getenv("SNOWFLAKE_DATABASE"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA"),
        "role": os.getenv("SNOWFLAKE_ROLE"),
    }
    sf_session = Session.builder.configs(params).create()
    llm = ChatSnowflake(
        model="llama4-maverick",
        snowflake_session=sf_session,
        max_tokens=1024,
        temperature=0.3,
    )
    return sf_session, llm


sf_session, llm = init_snowflake()


def init_session_state():
    st.session_state.setdefault("messages_no_memory", [])
    st.session_state.setdefault("messages_with_memory", [])
    st.session_state.setdefault("memory_type", "No Memory")
    st.session_state.setdefault("thread_id", f"thread_{uuid.uuid4().hex[:8]}")
    st.session_state.setdefault("user_id", "student")
    st.session_state.setdefault("memory_events", [])
    st.session_state.setdefault("memory_state_info", {})
    st.session_state.setdefault("checkpointer", MemorySaver())
    st.session_state.setdefault("long_term_store", InMemoryStore())
    st.session_state.setdefault("summary_text", "")
    st.session_state.setdefault("window_stats", "")
    st.session_state.setdefault("thread_counter", 1)


init_session_state()


def build_stateless_graph():
    def agent(state: MessagesState):
        return {"messages": [llm.invoke(state["messages"])]}

    builder = StateGraph(MessagesState)
    builder.add_node("agent", agent)
    builder.add_edge(START, "agent")
    builder.add_edge("agent", END)
    return builder.compile()


def build_full_history_graph():
    def agent(state: MessagesState):
        return {"messages": [llm.invoke(state["messages"])]}

    builder = StateGraph(MessagesState)
    builder.add_node("agent", agent)
    builder.add_edge(START, "agent")
    builder.add_edge("agent", END)
    return builder.compile(checkpointer=st.session_state.checkpointer)


def build_sliding_window_graph():
    def agent(state: MessagesState):
        trimmed = trim_messages(
            state["messages"],
            max_tokens=800,
            strategy="last",
            token_counter=llm,
            include_system=True,
            allow_partial=False,
        )
        st.session_state.window_stats = f"{len(trimmed)}/{len(state['messages'])}"
        return {"messages": [llm.invoke(trimmed)]}

    builder = StateGraph(MessagesState)
    builder.add_node("agent", agent)
    builder.add_edge(START, "agent")
    builder.add_edge("agent", END)
    return builder.compile(checkpointer=st.session_state.checkpointer)


class SummaryState(TypedDict):
    messages: Annotated[list, add_messages]
    summary: str


SUMMARIZE_AFTER = 6


def build_summarization_graph():
    def summarize_node(state: SummaryState):
        summary = state.get("summary", "")
        messages = state["messages"]
        prior = f"Existing summary:\n{summary}\n\n" if summary else ""
        history_text = "\n".join(
            f"{'User' if isinstance(m, HumanMessage) else 'AI'}: {m.content}"
            for m in messages[:-2]
        )
        prompt = HumanMessage(
            f"{prior}Summarize the following conversation in 3-4 bullet points:\n\n{history_text}"
        )
        new_summary = llm.invoke([prompt]).content
        st.session_state.summary_text = new_summary
        st.session_state.memory_events.append(
            f"Compressed {len(messages) - 2} msgs into summary"
        )
        to_delete = [RemoveMessage(id=m.id) for m in messages[:-2]]
        return {"summary": new_summary, "messages": to_delete}

    def agent_node(state: SummaryState):
        summary = state.get("summary", "")
        messages = state["messages"]
        if summary:
            messages = [SystemMessage(f"Prior conversation summary:\n{summary}")] + messages
        return {"messages": [llm.invoke(messages)]}

    def should_summarize(state: SummaryState):
        return "summarize" if len(state["messages"]) > SUMMARIZE_AFTER else END

    builder = StateGraph(SummaryState)
    builder.add_node("agent", agent_node)
    builder.add_node("summarize", summarize_node)
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_summarize, {"summarize": "summarize", END: END})
    builder.add_edge("summarize", END)
    return builder.compile(checkpointer=st.session_state.checkpointer)


def extract_facts(user_message):
    resp = llm.invoke([SystemMessage(FACT_EXTRACTION_PROMPT), HumanMessage(user_message)])
    try:
        facts = json.loads(resp.content.strip())
        return facts if isinstance(facts, list) else []
    except json.JSONDecodeError:
        return []


def build_semantic_graph():
    def agent(state: MessagesState, config: RunnableConfig):
        store = st.session_state.long_term_store
        user_id = config["configurable"].get("user_id", "anonymous")
        namespace = ("memory", user_id, "semantic")

        existing = store.search(namespace)
        facts_text = ""
        if existing:
            facts_text = "\n".join(f"  - {i.value['fact']}" for i in existing)
            st.session_state.memory_events.append(f"Loaded {len(existing)} facts")

        sys_content = "You are a helpful assistant."
        if facts_text:
            sys_content += f"\n\nWhat you know about this user:\n{facts_text}"
        response = llm.invoke([SystemMessage(sys_content)] + state["messages"])

        last_human = next(
            (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), None
        )
        if last_human:
            for fact in extract_facts(last_human):
                store.put(namespace, f"fact_{uuid.uuid4().hex[:8]}",
                          {"fact": fact, "ts": str(datetime.now())})
                st.session_state.memory_events.append(f"Saved fact: {fact}")

        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("agent", agent)
    builder.add_edge(START, "agent")
    builder.add_edge("agent", END)
    return builder.compile(checkpointer=st.session_state.checkpointer)


def build_episodic_graph():
    def agent(state: MessagesState, config: RunnableConfig):
        store = st.session_state.long_term_store
        user_id = config["configurable"].get("user_id", "anonymous")
        namespace = ("memory", user_id, "episodic")

        past = store.search(namespace)
        ep_ctx = ""
        if past:
            lines = [f"  - {e.value['summary']}" for e in past[-5:]]
            ep_ctx = "\nYour past sessions with this user:\n" + "\n".join(lines)
            st.session_state.memory_events.append(f"Loaded {len(past)} episode(s)")

        messages = [SystemMessage(f"You are a helpful assistant.{ep_ctx}")] + state["messages"]
        response = llm.invoke(messages)
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("agent", agent)
    builder.add_edge(START, "agent")
    builder.add_edge("agent", END)
    return builder.compile(checkpointer=st.session_state.checkpointer)


def save_episode_to_store(messages, thread_id, user_id):
    store = st.session_state.long_term_store
    convo = "\n".join(
        f"{'User' if isinstance(m, HumanMessage) else 'AI'}: {m.content}"
        for m in messages
    )
    summary = llm.invoke(
        [SystemMessage(EPISODE_SUMMARY_PROMPT), HumanMessage(convo)]
    ).content.strip()
    ep = {"session_id": thread_id, "summary": summary,
          "timestamp": str(datetime.now()), "turns": len(messages)}
    store.put(("memory", user_id, "episodic"), thread_id, ep)
    st.session_state.memory_events.append(f"Episode saved: {summary[:60]}...")


def build_procedural_graph():
    def agent(state: MessagesState, config: RunnableConfig):
        store = st.session_state.long_term_store
        user_id = config["configurable"].get("user_id", "anonymous")
        namespace = ("memory", user_id, "procedural")

        saved = store.search(namespace)
        rules = DEFAULT_PROCEDURES + [i.value["rule"] for i in saved]
        st.session_state.memory_events.append(f"{len(rules)} active rules")

        sys_content = "You are a helpful assistant. Follow these rules:\n" + \
                      "\n".join(f"  {i + 1}. {r}" for i, r in enumerate(rules))
        response = llm.invoke([SystemMessage(sys_content)] + state["messages"])

        last_human = next(
            (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), None
        )
        if last_human:
            try:
                chk = llm.invoke([SystemMessage(PROCEDURE_UPDATE_PROMPT), HumanMessage(last_human)])
                res = json.loads(chk.content.strip())
                if res.get("update"):
                    store.put(namespace, f"rule_{uuid.uuid4().hex[:8]}",
                              {"rule": res["rule"], "ts": str(datetime.now())})
                    st.session_state.memory_events.append(f"New rule: {res['rule']}")
            except Exception:
                pass

        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("agent", agent)
    builder.add_edge(START, "agent")
    builder.add_edge("agent", END)
    return builder.compile(checkpointer=st.session_state.checkpointer)


GRAPH_BUILDERS = {
    "No Memory": build_stateless_graph,
    "Full History": build_full_history_graph,
    "Sliding Window": build_sliding_window_graph,
    "Summarization": build_summarization_graph,
    "Semantic Memory": build_semantic_graph,
    "Episodic Memory": build_episodic_graph,
    "Procedural Memory": build_procedural_graph,
}


def get_memory_state_display():
    mem_type = st.session_state.memory_type
    store = st.session_state.long_term_store
    uid = st.session_state.user_id
    info = {}

    if mem_type == "Full History":
        try:
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            graph = build_full_history_graph()
            snap = graph.get_state(config)
            msgs = snap.values.get("messages", [])
            info["Messages in checkpoint"] = len(msgs)
            info["Preview"] = [
                f"{'Human' if isinstance(m, HumanMessage) else 'AI'}: {m.content[:60]}..."
                for m in msgs[-4:]
            ]
        except Exception:
            info["Messages in checkpoint"] = 0

    elif mem_type == "Sliding Window":
        info["Window stats (kept/total)"] = st.session_state.window_stats or "N/A"

    elif mem_type == "Summarization":
        info["Running summary"] = st.session_state.summary_text or "No summary yet"

    elif mem_type == "Semantic Memory":
        items = store.search(("memory", uid, "semantic"))
        info["Facts stored"] = len(items)
        info["Facts"] = [i.value.get("fact", "") for i in items]

    elif mem_type == "Episodic Memory":
        items = store.search(("memory", uid, "episodic"))
        info["Episodes stored"] = len(items)
        info["Episodes"] = [i.value.get("summary", "") for i in items]

    elif mem_type == "Procedural Memory":
        items = store.search(("memory", uid, "procedural"))
        user_rules = [i.value.get("rule", "") for i in items]
        info["Default rules"] = DEFAULT_PROCEDURES
        info["User-added rules"] = user_rules if user_rules else ["None yet"]

    return info


def render_sidebar():
    with st.sidebar:
        st.title(":material/psychology: Memory Lab")
        st.caption("DAMG 7374 — Lab 6")

        prev_type = st.session_state.memory_type
        mem_type = st.radio(
            "Select memory type",
            list(MEMORY_DESCRIPTIONS.keys()),
            key="memory_type_radio",
            index=list(MEMORY_DESCRIPTIONS.keys()).index(st.session_state.memory_type),
        )
        if mem_type != prev_type:
            st.session_state.memory_type = mem_type
            st.session_state.messages_with_memory = []
            st.session_state.messages_no_memory = []
            st.session_state.memory_events = []
            st.session_state.summary_text = ""
            st.session_state.window_stats = ""
            st.session_state.checkpointer = MemorySaver()
            st.session_state.thread_id = f"thread_{uuid.uuid4().hex[:8]}"
            st.session_state.thread_counter = 1
            st.rerun()

        with st.expander(":material/info: Why memory matters", expanded=False):
            st.markdown("""
Without memory, LLMs are **stateless** — every call starts from scratch.
The agent cannot remember your name, preferences, or what you discussed 10 seconds ago.

**Try it:** Send "Hi, I'm [name]" then ask "What's my name?" — the left column (no memory) will always forget.
""")

        with st.expander(":material/account_tree: Architecture overview", expanded=False):
            st.code("""
┌──────────────────────────────────────┐
│          AGENT MEMORY                │
│                                      │
│  SHORT-TERM (Thread)                 │
│  ├─ Full History                     │
│  ├─ Sliding Window                   │
│  └─ Summarization                    │
│  Stored in: Checkpointer             │
│                                      │
│  LONG-TERM (Cross-Thread)            │
│  ├─ Semantic Memory (facts)          │
│  ├─ Episodic Memory (events)         │
│  └─ Procedural Memory (rules)        │
│  Stored in: Store                    │
└──────────────────────────────────────┘
""", language=None)

        with st.expander(":material/compare: Comparison table", expanded=False):
            st.markdown("""
| Type | Stores | Scope |
|------|--------|-------|
| **Full History** | Every message | Thread |
| **Sliding Window** | Last N tokens | Thread |
| **Summarization** | Summary + recent | Thread |
| **Semantic** | Facts/knowledge | Cross-thread |
| **Episodic** | Past events | Cross-thread |
| **Procedural** | Behavior rules | Cross-thread |
""")

        with st.expander(":material/decision: Decision tree", expanded=False):
            st.code("""
Need memory?
│
├── This session only? → SHORT-TERM
│   ├── Short chat      → Full History
│   ├── Long / tokens   → Sliding Window
│   └── Very long       → Summarization
│
└── Across sessions?   → LONG-TERM
    ├── User facts      → Semantic
    ├── Past events     → Episodic
    └── Agent behavior  → Procedural
""", language=None)

        st.markdown("---")

        with st.container(border=True):
            st.markdown(f":material/tag: **Thread:** `{st.session_state.thread_id[-8:]}`")
            col_t1, col_t2 = st.columns(2)
            if col_t1.button("New thread", use_container_width=True, icon=":material/refresh:"):
                st.session_state.thread_counter += 1
                st.session_state.thread_id = f"thread_{uuid.uuid4().hex[:8]}"
                st.session_state.messages_with_memory = []
                st.session_state.messages_no_memory = []
                st.session_state.memory_events = []
                st.session_state.summary_text = ""
                st.session_state.window_stats = ""
                st.session_state.checkpointer = MemorySaver()
                is_long_term = mem_type in ("Semantic Memory", "Episodic Memory", "Procedural Memory")
                if is_long_term:
                    st.toast("New thread — long-term memory persists!", icon=":material/memory:")
                else:
                    st.toast("New thread — short-term memory reset!", icon=":material/delete:")
                st.rerun()
            if col_t2.button("Clear all", use_container_width=True, icon=":material/delete_forever:"):
                st.session_state.messages_with_memory = []
                st.session_state.messages_no_memory = []
                st.session_state.memory_events = []
                st.session_state.summary_text = ""
                st.session_state.window_stats = ""
                st.session_state.checkpointer = MemorySaver()
                st.session_state.long_term_store = InMemoryStore()
                st.session_state.thread_id = f"thread_{uuid.uuid4().hex[:8]}"
                st.toast("All memory cleared!", icon=":material/delete_forever:")
                st.rerun()

        st.markdown("---")
        st.markdown("#### :material/monitoring: Live memory state")
        mem_info = get_memory_state_display()
        if mem_type == "No Memory":
            st.caption("No memory — nothing to inspect.")
        else:
            with st.container(border=True):
                for key, val in mem_info.items():
                    if isinstance(val, list):
                        st.markdown(f"**{key}:**")
                        for item in val:
                            if key == "User-added rules":
                                st.markdown(f":green-badge[+] {item}")
                            elif key == "Default rules":
                                st.caption(f"  {item}")
                            else:
                                st.caption(f"  - {item}")
                    elif key == "Running summary" and val != "No summary yet":
                        st.markdown(f"**{key}:**")
                        st.info(val[:300], icon=":material/summarize:")
                    else:
                        st.markdown(f"**{key}:** `{val}`")

        if st.session_state.memory_events:
            st.markdown("---")
            st.markdown("#### :material/history: Recent events")
            for ev in st.session_state.memory_events[-6:]:
                st.caption(f":material/arrow_right: {ev}")


def invoke_with_animation(graph, messages, config, mem_type, status_container):
    st.session_state.memory_events = []

    with status_container.status("Memory pipeline running...", expanded=True) as status:
        is_long_term = mem_type in ("Semantic Memory", "Episodic Memory", "Procedural Memory")

        if mem_type == "No Memory":
            status.update(label="Processing (no memory)...", state="running")
            st.write(":material/block: No memory loaded")
            result = graph.invoke({"messages": [HumanMessage(messages[-1]["content"])]})
            response = result["messages"][-1].content
            status.update(label="Done (stateless)", state="complete", expanded=False)
            return response

        if is_long_term:
            st.write(":material/download: Loading from memory store...")
            time.sleep(0.3)

        st.write(":material/smart_toy: Calling LLM with context...")
        result = graph.invoke(
            {"messages": [HumanMessage(messages[-1]["content"])]},
            config,
        )
        response = result["messages"][-1].content

        if is_long_term:
            st.write(":material/search: Extracting new memories...")
            time.sleep(0.3)

        events = st.session_state.memory_events
        if events:
            st.write(":material/save: Updating memory store...")
            for ev in events:
                st.write(f"  :material/check_circle: {ev}")
            time.sleep(0.2)

        if mem_type == "Sliding Window" and st.session_state.window_stats:
            st.write(f":material/content_cut: Window: {st.session_state.window_stats} messages kept")
        elif mem_type == "Summarization" and st.session_state.summary_text:
            st.write(":material/summarize: Summary updated")

        status.update(label="Pipeline complete", state="complete", expanded=False)

    for ev in events:
        if "Saved fact" in ev:
            st.toast(ev, icon=":material/lightbulb:")
        elif "Compressed" in ev:
            st.toast(ev, icon=":material/compress:")
        elif "New rule" in ev:
            st.toast(ev, icon=":material/rule:")
        elif "Episode saved" in ev:
            st.toast(ev, icon=":material/history:")

    return response


def main():
    render_sidebar()

    mem_type = st.session_state.memory_type

    st.markdown(f"### :material/psychology: Lab 6: Memory management — **{mem_type}**")
    st.info(MEMORY_DESCRIPTIONS[mem_type], icon=":material/info:")

    prompts = SUGGESTED_PROMPTS.get(mem_type, [])
    if prompts and not st.session_state.messages_with_memory:
        st.caption("Suggested prompts to try (click to send):")
        cols = st.columns(min(len(prompts), 4))
        for i, p in enumerate(prompts):
            if cols[i % len(cols)].button(
                p[:50] + ("..." if len(p) > 50 else ""),
                key=f"suggest_{i}",
                use_container_width=True,
            ):
                st.session_state["_pending_prompt"] = p
                st.rerun()

    col_no_mem, col_with_mem = st.columns(2)

    with col_no_mem:
        st.markdown("#### :material/block: Without memory")
        st.caption("Stateless — forgets everything each turn")
        with st.container(height=450, border=True):
            for msg in st.session_state.messages_no_memory:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

    with col_with_mem:
        st.markdown(f"#### :material/memory: With {mem_type}")
        scope = "Thread-scoped" if mem_type in ("Full History", "Sliding Window", "Summarization") else "Cross-thread" if mem_type != "No Memory" else "None"
        st.caption(f"{scope} memory active")
        with st.container(height=450, border=True):
            for msg in st.session_state.messages_with_memory:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    if msg["role"] == "assistant" and msg.get("memory_changes"):
                        with st.expander(":material/difference: Memory changes", expanded=False):
                            for change in msg["memory_changes"]:
                                st.caption(f":material/arrow_right: {change}")

    pending = st.session_state.pop("_pending_prompt", None)
    prompt = st.chat_input("Send a message to both agents...")
    user_input = pending or prompt

    if user_input:
        st.session_state.messages_no_memory.append({"role": "user", "content": user_input})
        st.session_state.messages_with_memory.append({"role": "user", "content": user_input})

        stateless_graph = build_stateless_graph()
        no_mem_result = stateless_graph.invoke({"messages": [HumanMessage(user_input)]})
        no_mem_response = no_mem_result["messages"][-1].content
        st.session_state.messages_no_memory.append({"role": "assistant", "content": no_mem_response})

        if mem_type == "No Memory":
            mem_graph = build_stateless_graph()
        else:
            mem_graph = GRAPH_BUILDERS[mem_type]()

        config = {
            "configurable": {
                "thread_id": st.session_state.thread_id,
                "user_id": st.session_state.user_id,
            }
        }

        st.session_state.memory_events = []

        if mem_type == "No Memory":
            result = mem_graph.invoke({"messages": [HumanMessage(user_input)]})
            mem_response = result["messages"][-1].content
        else:
            result = mem_graph.invoke(
                {"messages": [HumanMessage(user_input)]},
                config,
            )
            mem_response = result["messages"][-1].content

        if mem_type == "Episodic Memory":
            all_msgs = []
            for m in st.session_state.messages_with_memory:
                if m["role"] == "user":
                    all_msgs.append(HumanMessage(m["content"]))
                else:
                    all_msgs.append(AIMessage(m["content"]))
            all_msgs.append(AIMessage(mem_response))
            if len(all_msgs) >= 4:
                save_episode_to_store(
                    all_msgs, st.session_state.thread_id, st.session_state.user_id
                )

        events = list(st.session_state.memory_events)
        st.session_state.messages_with_memory.append({
            "role": "assistant",
            "content": mem_response,
            "memory_changes": events if events else None,
        })

        for ev in events:
            if "Saved fact" in ev or "fact" in ev.lower():
                st.toast(ev, icon=":material/lightbulb:")
            elif "Compressed" in ev or "summary" in ev.lower():
                st.toast(ev, icon=":material/compress:")
            elif "New rule" in ev:
                st.toast(ev, icon=":material/rule:")
            elif "Episode saved" in ev:
                st.toast(ev, icon=":material/history:")
            elif "Loaded" in ev:
                st.toast(ev, icon=":material/download:")

        st.rerun()


main()
