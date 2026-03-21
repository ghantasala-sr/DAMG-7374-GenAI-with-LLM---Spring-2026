from langgraph.graph import StateGraph, START, END

from schemas import AgentState
from nodes import (
    supervisor_node,
    assign_researchers,
    researcher_node,
    generator_node,
    reflector_node,
    evaluator_node,
    finalizer_node,
)


def route_after_eval(state: AgentState) -> str:
    if state.get("eval_decision") == "revise":
        return "generator"
    return "finalizer"


def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("researcher", researcher_node)
    builder.add_node("generator", generator_node)
    builder.add_node("reflector", reflector_node)
    builder.add_node("evaluator", evaluator_node)
    builder.add_node("finalizer", finalizer_node)

    builder.add_edge(START, "supervisor")
    builder.add_conditional_edges("supervisor", assign_researchers, ["researcher"])
    builder.add_edge("researcher", "generator")
    builder.add_edge("generator", "reflector")
    builder.add_edge("reflector", "evaluator")
    builder.add_conditional_edges(
        "evaluator",
        route_after_eval,
        {
            "generator": "generator",
            "finalizer": "finalizer",
        },
    )
    builder.add_edge("finalizer", END)

    return builder.compile()
