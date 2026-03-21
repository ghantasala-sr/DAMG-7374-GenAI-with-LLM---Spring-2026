import operator
from typing import Annotated, Literal

from typing_extensions import TypedDict
from pydantic import BaseModel, Field


class SubTopics(BaseModel):
    sub_topics: list[str] = Field(
        description="A list of 3 sub-topics to research for the given topic"
    )


class Critique(BaseModel):
    score: float = Field(
        description="Quality score from 1.0 to 10.0"
    )
    strengths: list[str] = Field(
        description="List of strengths in the draft"
    )
    weaknesses: list[str] = Field(
        description="List of weaknesses and areas for improvement"
    )
    suggestions: list[str] = Field(
        description="Specific actionable suggestions to improve the draft"
    )


class EvalDecision(BaseModel):
    decision: Literal["accept", "revise"] = Field(
        description="Whether to accept the draft or send it back for revision"
    )
    reasoning: str = Field(
        description="Brief explanation of the decision"
    )


class AgentState(TypedDict):
    topic: str
    sub_topics: list[str]
    research_results: Annotated[list, operator.add]
    draft: str
    critique: str
    score: float
    eval_decision: str
    revision_count: int
    final_output: str


class ResearcherState(TypedDict):
    sub_topic: str
    research_results: Annotated[list, operator.add]
