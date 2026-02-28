import streamlit as st
from routing_chain import run_routing_chain

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="🚗 Car Assistant",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 Intelligent Car Assistant")
st.caption("Powered by Snowflake Cortex · Routing Agent · RAG · News · Maps")

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.header("🔧 How It Works")
    st.markdown("""
    This assistant uses a **Routing Agent** to classify your question and 
    send it to the right specialized tool:

    | Query Type | Tool Used |
    |---|---|
    | Car reviews & ratings | 🔍 RAG Agent |
    | Latest auto news | 📰 News Agent |
    | Find a dealership | 📍 Maps Agent |
    """)
    st.divider()
    st.subheader("💡 Try These Queries")
    examples = [
        "Best EV for long road trips?",
        "What do people say about Tesla Model Y range?",
        "Latest news about Ford F-150 Lightning",
        "Toyota dealership near Boston",
        "Compare RAV4 Hybrid vs CR-V fuel economy reviews"
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state["example_query"] = ex

# ── Chat History ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("metadata"):
            with st.expander("🔍 Agent Details", expanded=False):
                st.json(msg["metadata"])

# ── Input ─────────────────────────────────────────────────────
default_input = st.session_state.pop("example_query", "")
user_input = st.chat_input("Ask me anything about cars...", key="chat_input")
query = user_input or default_input

if query:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Run routing chain with live status
    with st.chat_message("assistant"):
        with st.status("🤖 Agent is thinking...", expanded=True) as status:
            st.write("🧭 Routing query to the right tool...")
            result = run_routing_chain(query)

            tool_icons = {
                "rag_agent":   "🔍 RAG Agent (Car Reviews)",
                "news_agent":  "📰 News Agent (SerpAPI)",
                "maps_agent":  "📍 Maps Agent (Google Maps)"
            }
            tool_label = tool_icons.get(result["tool_used"], result["tool_used"])
            st.write(f"✅ Routed to: **{tool_label}**")
            st.write("✍️ Synthesizing response...")
            status.update(label=f"Done — used {tool_label}", state="complete")

        st.markdown(result["final_response"])

        metadata = {
            "tool_selected": result["tool_used"],
            "refined_query": result["refined_query"]
        }
        with st.expander("🔍 Agent Details", expanded=False):
            st.json(metadata)

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["final_response"],
        "metadata": metadata
    })