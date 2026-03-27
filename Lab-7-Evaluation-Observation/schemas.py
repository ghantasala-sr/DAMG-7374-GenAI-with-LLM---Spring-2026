"""
Lab 7 - Evaluation & Observation
Schemas: Pydantic validation models and LangGraph state definition.
"""

import operator
from typing import Annotated, Literal, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════════
# Pydantic Models — Input Guardrails
# ═══════════════════════════════════════════════════════════════════════════════

class PolicyEvaluation(BaseModel):
    """LLM-based content policy evaluation result."""
    is_compliant: bool = Field(description="Whether the input passes all policy checks")
    violated_policies: list[str] = Field(default_factory=list, description="List of violated policy names")
    explanation: str = Field(description="Brief explanation of the evaluation")
    risk_score: float = Field(ge=0.0, le=1.0, description="Risk score from 0.0 (safe) to 1.0 (dangerous)")


class InputValidation(BaseModel):
    """Combined result of all input guardrail checks."""
    is_valid: bool = Field(description="Whether input passes all checks")
    policy_eval: Optional[PolicyEvaluation] = Field(default=None, description="LLM policy evaluation")
    blocked_reason: Optional[str] = Field(default=None, description="Reason input was blocked")
    sanitized_input: str = Field(description="The sanitized/cleaned input text")


# ═══════════════════════════════════════════════════════════════════════════════
# Pydantic Models — Output Guardrails
# ═══════════════════════════════════════════════════════════════════════════════

class OutputCheck(BaseModel):
    """Output validation/filtering result."""
    is_safe: bool = Field(description="Whether the output passes safety checks")
    issues_found: list[str] = Field(default_factory=list, description="List of issues detected")
    filtered_output: str = Field(description="The filtered/cleaned output text")
    pii_detected: bool = Field(default=False, description="Whether PII was found")
    brand_safe: bool = Field(default=True, description="Whether output is brand-safe")


# ═══════════════════════════════════════════════════════════════════════════════
# Pydantic Models — Evaluation
# ═══════════════════════════════════════════════════════════════════════════════

class JudgeScore(BaseModel):
    """LLM-as-Judge evaluation score."""
    relevance: float = Field(ge=0.0, le=5.0, description="How relevant the response is (0-5)")
    helpfulness: float = Field(ge=0.0, le=5.0, description="How helpful the response is (0-5)")
    safety: float = Field(ge=0.0, le=5.0, description="How safe/appropriate the response is (0-5)")
    overall: float = Field(ge=0.0, le=5.0, description="Overall quality score (0-5)")
    reasoning: str = Field(description="Judge's reasoning for the scores")


class TrajectoryStep(BaseModel):
    """A single step in an agent trajectory."""
    node_name: str = Field(description="Name of the node executed")
    timestamp: float = Field(description="When the step occurred")
    duration_ms: float = Field(description="Duration in milliseconds")
    tokens_used: int = Field(default=0, description="Tokens consumed in this step")


class TrajectoryAnalysis(BaseModel):
    """Result of comparing actual vs expected trajectory."""
    actual_path: list[str] = Field(description="Actual sequence of nodes visited")
    expected_path: list[str] = Field(description="Expected sequence of nodes")
    precision: float = Field(ge=0.0, le=1.0, description="Fraction of actual steps that were expected")
    recall: float = Field(ge=0.0, le=1.0, description="Fraction of expected steps that were executed")
    is_valid: bool = Field(description="Whether the trajectory is acceptable")
    deviations: list[str] = Field(default_factory=list, description="Description of deviations")


# ═══════════════════════════════════════════════════════════════════════════════
# Pydantic Models — Monitoring
# ═══════════════════════════════════════════════════════════════════════════════

class LatencyRecord(BaseModel):
    """Latency measurement for a single operation."""
    operation: str = Field(description="Name of the operation measured")
    duration_ms: float = Field(description="Duration in milliseconds")
    threshold_ms: float = Field(default=5000.0, description="Acceptable threshold in ms")
    exceeded: bool = Field(default=False, description="Whether the threshold was exceeded")


class TokenUsage(BaseModel):
    """Token usage tracking for a single LLM call."""
    node_name: str = Field(description="Which node made the call")
    prompt_tokens: int = Field(default=0, description="Tokens in the prompt")
    completion_tokens: int = Field(default=0, description="Tokens in the completion")
    total_tokens: int = Field(default=0, description="Total tokens used")


# ═══════════════════════════════════════════════════════════════════════════════
# LangGraph State
# ═══════════════════════════════════════════════════════════════════════════════

class AgentState(TypedDict):
    """State that flows through the LangGraph pipeline."""
    # User input
    user_input: str
    sanitized_input: str

    # Guardrail results
    input_validation: Optional[dict]        # InputValidation as dict
    is_input_blocked: bool

    # Agent response
    agent_response: str
    output_check: Optional[dict]            # OutputCheck as dict
    final_response: str

    # Evaluation
    judge_score: Optional[dict]             # JudgeScore as dict

    # Trajectory tracking
    trajectory: Annotated[list[dict], operator.add]  # list of TrajectoryStep dicts
    expected_trajectory: list[str]

    # Monitoring
    latency_records: Annotated[list[dict], operator.add]  # list of LatencyRecord dicts
    token_usage: Annotated[list[dict], operator.add]       # list of TokenUsage dicts
    total_tokens: int

    # Metadata
    conversation_history: list[dict]
    error: Optional[str]
