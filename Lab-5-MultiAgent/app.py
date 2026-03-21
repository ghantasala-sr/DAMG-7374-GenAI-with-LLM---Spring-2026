import json as json_lib

import streamlit as st
from graph import build_graph

st.set_page_config(page_title="Multi-Agent Reflection Pipeline", layout="wide")

NODES_ORDER = ["supervisor", "researcher", "generator", "reflector", "evaluator", "finalizer"]

NODE_LABELS = {
    "supervisor": "Supervisor",
    "researcher": "Researcher (x3)",
    "generator": "Generator",
    "reflector": "Reflector",
    "evaluator": "Evaluator",
    "finalizer": "Finalizer",
}

NODE_DESCRIPTIONS = {
    "supervisor": "Decomposes topic into sub-topics",
    "researcher": "Parallel research on each sub-topic",
    "generator": "Writes / revises the article draft",
    "reflector": "Critiques draft with structured scoring",
    "evaluator": "Decides accept or revise",
    "finalizer": "Formats final output",
}

STATE_FIELDS = [
    "topic", "sub_topics", "research_results", "draft",
    "critique", "score", "eval_decision", "revision_count", "final_output",
]


def build_flow_dot(completed, active):
    colors = {}
    for n in NODES_ORDER:
        if n == active:
            colors[n] = "#FFA726"
        elif n in completed:
            colors[n] = "#66BB6A"
        else:
            colors[n] = "#E0E0E0"

    font_colors = {}
    for n in NODES_ORDER:
        font_colors[n] = "white" if n in completed or n == active else "#333333"

    dot = "digraph G {\n"
    dot += '  rankdir=TB;\n'
    dot += '  node [shape=box, style="filled,rounded", fontname="Helvetica", fontsize=11, margin="0.2,0.1"];\n'
    dot += '  edge [color="#999999", penwidth=1.5];\n'

    for n in NODES_ORDER:
        label = NODE_LABELS[n]
        dot += f'  {n} [label="{label}", fillcolor="{colors[n]}", fontcolor="{font_colors[n]}"];\n'

    dot += '  supervisor -> researcher;\n'
    dot += '  researcher -> generator;\n'
    dot += '  generator -> reflector;\n'
    dot += '  reflector -> evaluator;\n'
    dot += '  evaluator -> generator [label="revise", style=dashed, color="#EF5350"];\n'
    dot += '  evaluator -> finalizer [label="accept", color="#66BB6A"];\n'
    dot += "}\n"
    return dot


def format_state_display(state):
    lines = []
    for key in STATE_FIELDS:
        val = state.get(key, "")
        if key == "research_results":
            count = len(val) if isinstance(val, list) else 0
            lines.append(f"research_results: [{count} item(s)]")
        elif key == "draft":
            length = len(val) if isinstance(val, str) else 0
            preview = val[:80].replace("\n", " ") + "..." if length > 80 else val
            lines.append(f'draft: "{preview}" ({length} chars)')
        elif key == "critique":
            length = len(val) if isinstance(val, str) else 0
            first_line = val.split("\n")[0] if val else ""
            lines.append(f'critique: "{first_line}" ({length} chars)')
        elif key == "final_output":
            length = len(val) if isinstance(val, str) else 0
            lines.append(f"final_output: ({length} chars)")
        elif key == "sub_topics":
            lines.append(f"sub_topics: {val}")
        else:
            lines.append(f"{key}: {val}")
    return "\n".join(lines)


def render_node_output(node_name, node_output, accumulated_state, container):
    with container:
        if node_name == "supervisor":
            subs = node_output.get("sub_topics", [])
            st.markdown("**Read:** `topic`  **Wrote:** `sub_topics`")
            for i, s in enumerate(subs, 1):
                st.markdown(f"{i}. {s}")

        elif node_name == "researcher":
            results = node_output.get("research_results", [])
            st.markdown("**Read:** `sub_topic`  **Wrote:** `research_results`")
            for piece in results:
                st.markdown(piece[:300] + "..." if len(piece) > 300 else piece)

        elif node_name == "generator":
            rev = node_output.get("revision_count", 0)
            draft = node_output.get("draft", "")
            st.markdown(f"**Read:** `research_results, critique`  **Wrote:** `draft, revision_count`")
            st.markdown(f"Revision **#{rev}** | Length: **{len(draft)}** chars")
            with st.expander("View Draft", expanded=False):
                st.markdown(draft)

        elif node_name == "reflector":
            score = node_output.get("score", 0)
            critique = node_output.get("critique", "")
            st.markdown("**Read:** `draft`  **Wrote:** `critique, score`")
            st.progress(min(score / 10.0, 1.0), text=f"Score: {score}/10")

            for line in critique.split("\n"):
                line = line.strip()
                if line.startswith("+ "):
                    st.markdown(f":green[{line}]")
                elif line.startswith("- "):
                    st.markdown(f":red[{line}]")
                elif line.startswith("* "):
                    st.markdown(f":blue[{line}]")
                elif line:
                    st.markdown(line)

        elif node_name == "evaluator":
            decision = node_output.get("eval_decision", "?")
            rev = accumulated_state.get("revision_count", 0)
            score = accumulated_state.get("score", 0)
            st.markdown("**Read:** `score, revision_count`  **Wrote:** `eval_decision`")
            if decision == "accept":
                st.success(f"ACCEPT — Score {score}/10 meets threshold or max revisions reached")
            else:
                st.warning(f"REVISE — Score {score}/10 below 8.0, sending back (revision {rev})")

        elif node_name == "finalizer":
            st.markdown("**Read:** `draft, score, sub_topics, revision_count`  **Wrote:** `final_output`")
            st.success("Final output prepared")


@st.cache_resource
def get_graph():
    return build_graph()


st.title("Multi-Agent Reflection Pipeline")
st.caption("Snowflake LLMs + LangGraph")

with st.sidebar:
    st.subheader("Pipeline Flow")
    sidebar_graph_placeholder = st.empty()
    sidebar_graph_placeholder.graphviz_chart(build_flow_dot(set(), None))

    st.divider()
    st.subheader("Patterns Demonstrated")
    st.markdown(
        "1. **Sequential Handoffs**\n"
        "2. **Parallel Processing** (Send API)\n"
        "3. **Reflection Loop**\n"
        "4. **Hierarchical Supervisor**\n"
        "5. **Critic-Reviewer**\n"
        "6. **Structured Output**"
    )
    st.divider()
    st.subheader("Model Config")
    st.code("Model: mistral-large2\nGenerator temp: 0.7\nReflector temp: 0.2\nMax revisions: 3", language=None)

topic = st.text_input("Research Topic", value="The Impact of Artificial Intelligence on Healthcare")

if st.button("Run Pipeline", type="primary", disabled=not topic.strip()):
    graph = get_graph()

    initial_state = {
        "topic": topic,
        "sub_topics": [],
        "research_results": [],
        "draft": "",
        "critique": "",
        "score": 0.0,
        "eval_decision": "",
        "revision_count": 0,
        "final_output": "",
    }

    accumulated_state = dict(initial_state)
    completed_nodes = set()
    score_history = []
    node_log = []

    col_left, col_right = st.columns([3, 2])

    with col_right:
        st.subheader("Live State")
        state_placeholder = st.empty()
        state_placeholder.code(format_state_display(accumulated_state), language=None)

        st.subheader("Score Progression")
        score_chart_placeholder = st.empty()

    with col_left:
        st.subheader("Node Execution")

    for event in graph.stream(initial_state, stream_mode="updates"):
        for node_name, node_output in event.items():
            sidebar_graph_placeholder.graphviz_chart(
                build_flow_dot(completed_nodes, node_name)
            )

            accumulated_state.update(node_output)
            state_placeholder.code(format_state_display(accumulated_state), language=None)

            if node_name == "reflector":
                s = node_output.get("score", 0)
                score_history.append({"Iteration": len(score_history) + 1, "Score": s})
                score_chart_placeholder.line_chart(
                    data=score_history,
                    x="Iteration",
                    y="Score",
                    y_label="Score (out of 10)",
                )

            with col_left:
                status_icon = "running"
                label = f"{NODE_LABELS.get(node_name, node_name)}"
                desc = NODE_DESCRIPTIONS.get(node_name, "")
                with st.status(f"{label} — {desc}", expanded=True, state=status_icon) as node_status:
                    render_node_output(node_name, node_output, accumulated_state, node_status)
                    node_status.update(label=f"{label} — Done", state="complete", expanded=False)

            completed_nodes.add(node_name)

            node_log.append({
                "node": node_name,
                "output_keys": list(node_output.keys()),
                "output_summary": {
                    k: (f"[{len(v)} items]" if isinstance(v, list)
                        else f"({len(v)} chars)" if isinstance(v, str) and len(v) > 100
                        else v)
                    for k, v in node_output.items()
                },
            })

    sidebar_graph_placeholder.graphviz_chart(build_flow_dot(completed_nodes, None))

    st.divider()
    st.subheader("Results")

    col1, col2, col3 = st.columns(3)
    col1.metric("Quality Score", f"{accumulated_state.get('score', 0)}/10")
    col2.metric("Revisions", accumulated_state.get("revision_count", 0))
    col3.metric("Research Pieces", len(accumulated_state.get("research_results", [])))

    tab_article, tab_research, tab_revisions, tab_state = st.tabs([
        "Final Article", "Research Materials", "Revision History", "Full State"
    ])

    with tab_article:
        st.markdown(accumulated_state.get("draft", "No draft available"))

    with tab_research:
        for piece in accumulated_state.get("research_results", []):
            st.markdown(piece)
            st.divider()

    with tab_revisions:
        if score_history:
            for entry in score_history:
                iteration = entry["Iteration"]
                score = entry["Score"]
                icon = "✅" if score >= 8.0 else "🔄"
                st.markdown(f"**Iteration {iteration}:** Score {score}/10 {icon}")
            st.markdown(f"\n**Final decision:** `{accumulated_state.get('eval_decision', 'N/A').upper()}`")
        else:
            st.info("No reflection iterations recorded")

        st.subheader("Last Critique")
        st.text(accumulated_state.get("critique", "N/A"))

    with tab_state:
        display_state = {}
        for k, v in accumulated_state.items():
            if isinstance(v, str) and len(v) > 500:
                display_state[k] = v[:500] + f"... ({len(v)} chars total)"
            elif isinstance(v, list) and len(v) > 3:
                display_state[k] = [f"[{len(v)} items]"]
            else:
                display_state[k] = v
        st.json(display_state)

        st.subheader("Pipeline Log")
        for entry in node_log:
            st.code(json_lib.dumps(entry, indent=2, default=str), language="json")
