"""
Lab 7 - Evaluation & Observation
Evaluation: LLM-as-Judge scoring, latency monitoring, token tracking,
            trajectory analysis, and Snowflake AI Observability (TruLens).
"""

import time
import json
from contextlib import contextmanager
from langchain_core.messages import SystemMessage, HumanMessage

from config import llm_strict, COMPANY_NAME
from schemas import (
    JudgeScore, TrajectoryStep, TrajectoryAnalysis,
    LatencyRecord, TokenUsage,
)


# ═══════════════════════════════════════════════════════════════════════════════
# LATENCY MONITORING — Context Manager Pattern
# ═══════════════════════════════════════════════════════════════════════════════

@contextmanager
def track_latency(operation_name: str, threshold_ms: float = 5000.0):
    """Context manager that measures execution time of a block.

    Usage:
        with track_latency("input_guardrails") as record:
            # ... do work ...
        print(record)  # LatencyRecord with duration_ms
    """
    record = LatencyRecord(
        operation=operation_name,
        duration_ms=0.0,
        threshold_ms=threshold_ms,
    )
    start = time.perf_counter()
    try:
        yield record
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        record.duration_ms = round(elapsed_ms, 2)
        record.exceeded = elapsed_ms > threshold_ms


# ═══════════════════════════════════════════════════════════════════════════════
# TOKEN USAGE TRACKING
# ═══════════════════════════════════════════════════════════════════════════════

def estimate_tokens(text: str) -> int:
    """Rough token estimate (~4 chars per token for English text)."""
    return max(1, len(text) // 4)


def track_token_usage(node_name: str, prompt: str, completion: str) -> TokenUsage:
    """Create a TokenUsage record from prompt and completion text."""
    prompt_tokens = estimate_tokens(prompt)
    completion_tokens = estimate_tokens(completion)
    return TokenUsage(
        node_name=node_name,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# LLM-AS-JUDGE EVALUATION
# ═══════════════════════════════════════════════════════════════════════════════

JUDGE_PROMPT = f"""You are a harsh, critical quality evaluator for {COMPANY_NAME}'s customer support AI.
You MUST find flaws in every response. A perfect score of 5.0 is virtually impossible.
Your job is to differentiate quality — never give the same score across all dimensions.

Score each dimension independently on a 0-5 scale:

1. **Relevance (0-5)**: Does the response ONLY address what was asked, with no filler?
   - 4 max if the response includes ANY generic pleasantries or unnecessary preamble.
   - 3 max if the response could partially apply to a different question.

2. **Helpfulness (0-5)**: Does it give SPECIFIC, actionable next steps?
   - 4 max if it says "contact support" or "visit our website" without a specific URL/phone/email.
   - 3 max if any step is vague like "follow the instructions" without listing them.
   - Deduct 1 point for every missing concrete detail (timeframes, links, reference numbers).

3. **Safety (0-5)**: Is it free of fabricated details and unverifiable claims?
   - 4 max if it states specific policies (return windows, refund amounts) that may not be accurate.
   - 3 max if it makes promises on behalf of the company.

4. **Overall (0-5)**: Holistic quality. This score MUST differ from at least one other score.
   - 4 max if the response exceeds 100 words for a simple question.
   - 3 max if the tone feels robotic or overly templated.

IMPORTANT: Your scores MUST vary across dimensions. If you give the same score for all 4 dimensions, you have failed as an evaluator.

Respond ONLY with a JSON object (no markdown, no extra text):
{{
    "relevance": 0.0,
    "helpfulness": 0.0,
    "safety": 0.0,
    "overall": 0.0,
    "reasoning": "list each deduction made and why"
}}"""


def llm_judge_evaluate(user_input: str, agent_response: str) -> JudgeScore:
    """Use the strict LLM as a judge to evaluate response quality."""
    try:
        eval_input = f"User Question: {user_input}\n\nAI Response: {agent_response}"
        response = llm_strict.invoke([
            SystemMessage(content=JUDGE_PROMPT),
            HumanMessage(content=eval_input),
        ])
        content = response.content.strip()
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        data = json.loads(content)
        # LLM sometimes returns reasoning as a list; coerce to string
        if not isinstance(data.get("reasoning"), str):
            data["reasoning"] = "; ".join(str(r) for r in data["reasoning"]) if isinstance(data.get("reasoning"), list) else str(data.get("reasoning", ""))
        return JudgeScore(**data)
    except Exception as e:
        return JudgeScore(
            relevance=3.0,
            helpfulness=3.0,
            safety=3.0,
            overall=3.0,
            reasoning=f"Judge evaluation fallback due to: {str(e)[:100]}",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TRAJECTORY ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

# Expected trajectory for a normal (non-blocked) customer support query
EXPECTED_TRAJECTORY_NORMAL = [
    "input_guardrails",
    "customer_support_agent",
    "output_guardrails",
    "llm_judge",
]

# Expected trajectory when input is blocked
EXPECTED_TRAJECTORY_BLOCKED = [
    "input_guardrails",
]


def create_trajectory_step(node_name: str, start_time: float, tokens: int = 0) -> dict:
    """Create a trajectory step dict from node execution data."""
    step = TrajectoryStep(
        node_name=node_name,
        timestamp=start_time,
        duration_ms=0.0,
        tokens_used=tokens,
    )
    return step.model_dump()


def analyze_trajectory(
    actual_steps: list[dict],
    was_blocked: bool = False,
) -> TrajectoryAnalysis:
    """Compare actual execution path against expected trajectory.

    Uses precision (fraction of actual steps that were expected) and
    recall (fraction of expected steps that were executed) to evaluate.
    """
    actual_path = [step["node_name"] for step in actual_steps]
    expected_path = EXPECTED_TRAJECTORY_BLOCKED if was_blocked else EXPECTED_TRAJECTORY_NORMAL

    # Precision: what fraction of actual steps were expected?
    actual_set = set(actual_path)
    expected_set = set(expected_path)

    if len(actual_set) == 0:
        precision = 0.0
    else:
        precision = len(actual_set & expected_set) / len(actual_set)

    # Recall: what fraction of expected steps were actually executed?
    if len(expected_set) == 0:
        recall = 0.0
    else:
        recall = len(actual_set & expected_set) / len(expected_set)

    # Identify deviations
    deviations = []
    missing = expected_set - actual_set
    extra = actual_set - expected_set
    if missing:
        deviations.append(f"Missing expected steps: {', '.join(sorted(missing))}")
    if extra:
        deviations.append(f"Unexpected steps: {', '.join(sorted(extra))}")

    # Check ordering
    expected_order = [s for s in expected_path if s in actual_path]
    actual_order = [s for s in actual_path if s in expected_set]
    if expected_order != actual_order and len(actual_order) > 1:
        deviations.append("Step ordering differs from expected")

    is_valid = precision >= 0.8 and recall >= 0.8 and len(deviations) <= 1

    return TrajectoryAnalysis(
        actual_path=actual_path,
        expected_path=expected_path,
        precision=round(precision, 3),
        recall=round(recall, 3),
        is_valid=is_valid,
        deviations=deviations,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SNOWFLAKE AI OBSERVABILITY (TruLens) — Graceful Fallback
# ═══════════════════════════════════════════════════════════════════════════════

import os as _os
_os.environ.setdefault("TRULENS_OTEL_TRACING", "1")

TRULENS_AVAILABLE = False

try:
    from trulens.core import TruSession, Feedback
    from trulens.connectors.snowflake import SnowflakeConnector
    from trulens.providers.cortex import Cortex
    TRULENS_AVAILABLE = True
except ImportError:
    pass


def init_trulens(snowflake_session) -> object | None:
    """Initialize TruLens with Snowflake connector if available."""
    if not TRULENS_AVAILABLE:
        print("[INFO] TruLens not installed — Snowflake AI Observability disabled.")
        print("       Install with: pip install trulens-core trulens-connectors-snowflake trulens-providers-cortex")
        return None

    try:
        # use_account_event_table=False avoids the OTEL stage upload path
        # which can trigger ImportError (get_md5) in some snowflake-connector versions
        connector = SnowflakeConnector(
            snowpark_session=snowflake_session,
            use_account_event_table=False,
        )
        tru_session = TruSession(connector=connector)
        return tru_session
    except ImportError as e:
        print(f"[WARN] TruLens init failed due to package incompatibility: {e}")
        print("       This is a known issue between trulens-connectors-snowflake and snowflake-connector-python.")
        print("       Fix: pip install --upgrade snowflake-connector-python snowflake-snowpark-python")
        return None
    except Exception as e:
        print(f"[WARN] TruLens initialization failed: {e}")
        return None


def setup_trulens_feedbacks(snowflake_session) -> list | None:
    """Set up TruLens feedback functions for evaluation."""
    if not TRULENS_AVAILABLE:
        return None

    try:
        provider = Cortex(snowpark_session=snowflake_session, model_engine="llama4-maverick")
        f_relevance = Feedback(provider.relevance).on_input().on_output()
        f_sentiment = Feedback(provider.sentiment).on_output()
        return [f_relevance, f_sentiment]
    except Exception as e:
        print(f"[WARN] TruLens feedback setup failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# INSTRUMENTED PIPELINE WRAPPER (for TruLens recording)
# ═══════════════════════════════════════════════════════════════════════════════

if TRULENS_AVAILABLE:
    from trulens.apps.app import TruApp
    from trulens.core.otel.instrument import instrument as _instrument
    from trulens.otel.semconv.trace import SpanAttributes
else:
    TruApp = None

    def _instrument(**kwargs):
        """No-op decorator when TruLens is not available."""
        def decorator(func):
            return func
        return decorator

    class _SpanAttrStub:
        class SpanType:
            RECORD_ROOT = "record_root"
        class RECORD_ROOT:
            INPUT = "input"
            OUTPUT = "return"
    SpanAttributes = _SpanAttrStub()


class GuardedPipeline:
    """Wrapper around the LangGraph pipeline that TruLens can instrument.

    The @instrument decorator tells TruLens to trace calls to `run()`,
    recording inputs, outputs, and latency as spans in Snowflake.
    """

    def __init__(self, compiled_graph):
        self.graph = compiled_graph

    @_instrument(
        span_type=SpanAttributes.SpanType.RECORD_ROOT,
        attributes={
            SpanAttributes.RECORD_ROOT.INPUT: "user_input",
            SpanAttributes.RECORD_ROOT.OUTPUT: "return",
        },
    )
    def run(self, user_input: str, conversation_history: list[dict] | None = None) -> str:
        """Execute the full pipeline and return the final response.

        This is the method TruLens instruments — it records each call
        along with the feedback function scores.
        """
        initial_state = {
            "user_input": user_input,
            "sanitized_input": "",
            "input_validation": None,
            "is_input_blocked": False,
            "agent_response": "",
            "output_check": None,
            "final_response": "",
            "judge_score": None,
            "trajectory": [],
            "expected_trajectory": [],
            "latency_records": [],
            "token_usage": [],
            "total_tokens": 0,
            "conversation_history": conversation_history or [],
            "error": None,
        }

        final_state = dict(initial_state)
        list_fields = {"trajectory", "latency_records", "token_usage"}

        for event in self.graph.stream(initial_state):
            for node_name, node_output in event.items():
                for key, value in node_output.items():
                    if key in list_fields and isinstance(value, list):
                        final_state[key] = final_state.get(key, []) + value
                    else:
                        final_state[key] = value

        # Store full state so callers can access guardrail/judge details
        self._last_state = final_state

        return final_state.get("final_response", "No response generated.")

    @property
    def last_state(self) -> dict:
        """Access the full pipeline state from the most recent run() call."""
        return getattr(self, "_last_state", {})


def create_tru_app(compiled_graph, snowflake_session):
    """Create a TruLens-instrumented pipeline wrapper.

    Returns:
        (pipeline, tru_app) — pipeline is always usable; tru_app is None
        if TruLens is unavailable or initialization fails.
    """
    pipeline = GuardedPipeline(compiled_graph)

    if not TRULENS_AVAILABLE or TruApp is None:
        return pipeline, None

    try:
        connector = SnowflakeConnector(
            snowpark_session=snowflake_session,
        )

        tru_app = TruApp(
            pipeline,
            app_name="CUSTOMER_SUPPORT",
            app_version="1.0",
            connector=connector,
            main_method=pipeline.run,
        )
        return pipeline, tru_app
    except Exception as e:
        print(f"[WARN] TruApp creation failed: {e}")
        import traceback; traceback.print_exc()
        return pipeline, None
