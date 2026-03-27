"""
Lab 7 - Evaluation & Observation
Graph: LangGraph StateGraph assembly with conditional edges.
"""

from langgraph.graph import StateGraph, END

from schemas import AgentState
from nodes import (
    input_guardrails_node,
    customer_support_agent_node,
    output_guardrails_node,
    llm_judge_node,
    route_after_input_guardrails,
)


def build_graph() -> StateGraph:
    """Build and compile the guarded customer support pipeline.

    Flow:
        input_guardrails
            ├── [blocked] → END
            └── [allowed] → customer_support_agent
                                → output_guardrails
                                    → llm_judge
                                        → END
    """
    builder = StateGraph(AgentState)

    # ── Add nodes ────────────────────────────────────────────────────────────
    builder.add_node("input_guardrails", input_guardrails_node)
    builder.add_node("customer_support_agent", customer_support_agent_node)
    builder.add_node("output_guardrails", output_guardrails_node)
    builder.add_node("llm_judge", llm_judge_node)

    # ── Set entry point ──────────────────────────────────────────────────────
    builder.set_entry_point("input_guardrails")

    # ── Conditional edge: block or proceed after input guardrails ─────────
    builder.add_conditional_edges(
        "input_guardrails",
        route_after_input_guardrails,
        {
            "blocked": END,
            "allowed": "customer_support_agent",
        },
    )

    # ── Sequential edges: agent → output guardrails → judge → END ─────────
    builder.add_edge("customer_support_agent", "output_guardrails")
    builder.add_edge("output_guardrails", "llm_judge")
    builder.add_edge("llm_judge", END)

    return builder.compile()


# ── Pre-built graph instance ─────────────────────────────────────────────────
graph = build_graph()


# ── Graphviz DOT representation for visualization ────────────────────────────
GRAPH_DOT = """
digraph G {
    rankdir=TB;
    node [shape=box, style="rounded,filled", fontname="Helvetica"];

    start [label="START", shape=oval, fillcolor="#e8f5e9"];
    input_guardrails [label="Input Guardrails\\n(Policy Check)", fillcolor="#fff3e0"];
    customer_support_agent [label="Customer Support\\nAgent (LLM)", fillcolor="#e3f2fd"];
    output_guardrails [label="Output Guardrails\\n(PII/Brand/Halluc.)", fillcolor="#fff3e0"];
    llm_judge [label="LLM-as-Judge\\n(Quality Eval)", fillcolor="#f3e5f5"];
    end_node [label="END", shape=oval, fillcolor="#ffebee"];
    blocked [label="BLOCKED\\n(Input Rejected)", shape=oval, fillcolor="#ffcdd2"];

    start -> input_guardrails;
    input_guardrails -> customer_support_agent [label="allowed", color="green"];
    input_guardrails -> blocked [label="blocked", color="red", style="dashed"];
    customer_support_agent -> output_guardrails;
    output_guardrails -> llm_judge;
    llm_judge -> end_node;
    blocked -> end_node [style="dotted"];
}
"""
