"""
Lab 7 - Evaluation & Observation
Nodes: LangGraph node functions for the guarded customer support pipeline.
"""

import time
from langchain_core.messages import SystemMessage, HumanMessage

from config import llm, COMPANY_NAME
from schemas import AgentState
from guardrails import validate_input, validate_output
from evaluation import (
    track_latency, track_token_usage, create_trajectory_step,
    llm_judge_evaluate, analyze_trajectory,
)


# ═══════════════════════════════════════════════════════════════════════════════
# NODE 1: Input Guardrails
# ═══════════════════════════════════════════════════════════════════════════════

def input_guardrails_node(state: AgentState) -> dict:
    """Validate user input through the guardrail pipeline.
    Decides whether to block or allow the message.
    """
    start_time = time.perf_counter()

    with track_latency("input_guardrails", threshold_ms=3000) as latency:
        validation = validate_input(state["user_input"])

    # Token usage for the LLM policy check
    token_record = track_token_usage(
        "input_guardrails",
        prompt=state["user_input"],
        completion=validation.blocked_reason or "compliant",
    )

    trajectory_step = create_trajectory_step(
        "input_guardrails", start_time, token_record.total_tokens,
    )
    trajectory_step["duration_ms"] = latency.duration_ms

    result = {
        "input_validation": validation.model_dump(),
        "sanitized_input": validation.sanitized_input,
        "is_input_blocked": not validation.is_valid,
        "trajectory": [trajectory_step],
        "latency_records": [latency.model_dump()],
        "token_usage": [token_record.model_dump()],
        "total_tokens": token_record.total_tokens,
    }

    if not validation.is_valid:
        result["final_response"] = (
            f"I'm sorry, I can't process that request. "
            f"Reason: {validation.blocked_reason}"
        )
        result["agent_response"] = ""

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# NODE 2: Customer Support Agent
# ═══════════════════════════════════════════════════════════════════════════════

SUPPORT_SYSTEM_PROMPT = f"""You are {COMPANY_NAME}'s helpful customer support assistant.
Your role:
- Help customers with product questions, billing, account issues, and technical support.
- Be polite, professional, and concise.
- If you don't know something, say so honestly rather than guessing.
- Never share personal information or make up account details.
- Always represent {COMPANY_NAME} positively without disparaging competitors.

Guidelines:
- Keep responses under 200 words unless the question requires detail.
- Offer to escalate to a human agent for complex issues.
- Provide step-by-step instructions when applicable."""


def customer_support_agent_node(state: AgentState) -> dict:
    """Generate a customer support response using the LLM."""
    start_time = time.perf_counter()

    # Build conversation context
    messages = [SystemMessage(content=SUPPORT_SYSTEM_PROMPT)]
    for msg in state.get("conversation_history", []):
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            from langchain_core.messages import AIMessage
            messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=state["sanitized_input"]))

    with track_latency("customer_support_agent", threshold_ms=5000) as latency:
        response = llm.invoke(messages)

    agent_response = response.content.strip()
    prompt_text = SUPPORT_SYSTEM_PROMPT + state["sanitized_input"]
    token_record = track_token_usage("customer_support_agent", prompt_text, agent_response)

    trajectory_step = create_trajectory_step(
        "customer_support_agent", start_time, token_record.total_tokens,
    )
    trajectory_step["duration_ms"] = latency.duration_ms

    return {
        "agent_response": agent_response,
        "trajectory": [trajectory_step],
        "latency_records": [latency.model_dump()],
        "token_usage": [token_record.model_dump()],
        "total_tokens": state.get("total_tokens", 0) + token_record.total_tokens,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# NODE 3: Output Guardrails
# ═══════════════════════════════════════════════════════════════════════════════

def output_guardrails_node(state: AgentState) -> dict:
    """Validate and filter the agent's output."""
    start_time = time.perf_counter()

    with track_latency("output_guardrails", threshold_ms=1000) as latency:
        check = validate_output(state["agent_response"])

    token_record = track_token_usage(
        "output_guardrails",
        prompt=state["agent_response"],
        completion=str(check.issues_found),
    )

    trajectory_step = create_trajectory_step(
        "output_guardrails", start_time, token_record.total_tokens,
    )
    trajectory_step["duration_ms"] = latency.duration_ms

    return {
        "output_check": check.model_dump(),
        "final_response": check.filtered_output,
        "trajectory": [trajectory_step],
        "latency_records": [latency.model_dump()],
        "token_usage": [token_record.model_dump()],
        "total_tokens": state.get("total_tokens", 0) + token_record.total_tokens,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# NODE 4: LLM-as-Judge Evaluation
# ═══════════════════════════════════════════════════════════════════════════════

def llm_judge_node(state: AgentState) -> dict:
    """Evaluate the final response quality using LLM-as-Judge."""
    start_time = time.perf_counter()

    with track_latency("llm_judge", threshold_ms=5000) as latency:
        score = llm_judge_evaluate(state["user_input"], state["final_response"])

    prompt_text = state["user_input"] + state["final_response"]
    token_record = track_token_usage("llm_judge", prompt_text, score.reasoning)

    trajectory_step = create_trajectory_step(
        "llm_judge", start_time, token_record.total_tokens,
    )
    trajectory_step["duration_ms"] = latency.duration_ms

    return {
        "judge_score": score.model_dump(),
        "trajectory": [trajectory_step],
        "latency_records": [latency.model_dump()],
        "token_usage": [token_record.model_dump()],
        "total_tokens": state.get("total_tokens", 0) + token_record.total_tokens,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTING FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def route_after_input_guardrails(state: AgentState) -> str:
    """Route based on input validation: blocked → END, allowed → agent."""
    if state.get("is_input_blocked", False):
        return "blocked"
    return "allowed"
