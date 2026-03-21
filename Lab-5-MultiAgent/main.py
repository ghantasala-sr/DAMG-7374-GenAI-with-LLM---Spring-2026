from graph import build_graph


def main():
    print("\n" + "#" * 60)
    print("# MULTI-AGENT REFLECTION PIPELINE")
    print("# Snowflake LLMs + LangGraph")
    print("#" * 60)
    print()
    print("Architecture:")
    print("  Supervisor -> [Researchers x3 (parallel)] -> Generator <-> Reflector <-> Evaluator -> Finalizer")
    print()
    print("Patterns demonstrated:")
    print("  1. Sequential Handoffs (Supervisor -> Researchers -> Generator -> ...)")
    print("  2. Parallel Processing (Fan-out via Send API to 3 researchers)")
    print("  3. Reflection Loop (Generator <-> Reflector <-> Evaluator cycle)")
    print("  4. Hierarchical Supervisor (Topic decomposition)")
    print("  5. Critic-Reviewer (Reflector scores and critiques)")
    print("  6. Structured Output (JSON-based scoring and decisions)")
    print()

    graph = build_graph()

    topic = "The Impact of Artificial Intelligence on Healthcare"

    result = graph.invoke({
        "topic": topic,
        "sub_topics": [],
        "research_results": [],
        "draft": "",
        "critique": "",
        "score": 0.0,
        "eval_decision": "",
        "revision_count": 0,
        "final_output": "",
    })

    print("\n\n")
    print(result["final_output"])

    print("\n\n" + "#" * 60)
    print("# EXECUTION SUMMARY")
    print("#" * 60)
    print(f"  Topic: {result['topic']}")
    print(f"  Sub-topics: {result['sub_topics']}")
    print(f"  Research pieces: {len(result['research_results'])}")
    print(f"  Total revisions: {result['revision_count']}")
    print(f"  Final score: {result['score']}/10")
    print(f"  Decision: {result['eval_decision']}")
    print("#" * 60)


if __name__ == "__main__":
    main()
