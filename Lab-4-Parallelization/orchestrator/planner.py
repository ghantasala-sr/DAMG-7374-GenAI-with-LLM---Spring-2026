"""
Planner Agent - Query Decomposition & Analyst Routing.

Analyzes user queries and determines which specialist analysts to engage
in parallel, generating focused sub-queries for each analyst.
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from snowflake.snowpark import Session
from langchain_snowflake import ChatSnowflake
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field


class PlannerOutput(BaseModel):
    """Structured output from the planner agent."""
    analysts: List[str] = Field(
        description="List of analyst names to engage (review_analyst, market_analyst, purchase_analyst)"
    )
    sub_queries: Dict[str, str] = Field(
        description="Focused sub-query for each selected analyst"
    )
    synthesis_focus: str = Field(
        description="Brief description of how to combine analyst results"
    )
    priority_analyst: Optional[str] = Field(
        default=None,
        description="The most important analyst for this query"
    )


PLANNER_PROMPT = """You are an analyst coordination system for a Full-Stack Car Analyst platform.
Your job is to analyze user queries and determine which specialist analysts should be engaged.

Available Analysts:
1. review_analyst: Specializes in car reviews, owner experiences, ratings, sentiment analysis,
   reliability data, and common issues. Uses RAG over a database of owner reviews.
   Best for: "What do owners say about X?", "Is X reliable?", "Common problems with X?"

2. market_analyst: Specializes in market trends, pricing analysis, competitive landscape,
   industry news, and market sentiment. Fetches real-time automotive news.
   Best for: "What's the market like for X?", "Pricing trends for X?", "News about X?"

3. purchase_analyst: Specializes in purchase recommendations, budget analysis, feature matching,
   dealer locations, and total cost of ownership. Integrates with Google Maps.
   Best for: "Should I buy X?", "Best X under $Y?", "Dealers near Z?", "X vs Y which to buy?"

Rules for analyst selection:
- Select 1-3 analysts based on query complexity
- For simple queries (single topic), use 1 analyst
- For comparison queries, use 2-3 analysts
- For "analyze everything about X", use all 3 analysts
- Always include purchase_analyst if budget/price is mentioned
- Always include review_analyst if reliability/issues/owner experiences are mentioned
- Always include market_analyst if news/trends/market conditions are mentioned

User Query: {query}

Respond with a JSON object containing:
- analysts: List of analyst names to engage
- sub_queries: A focused sub-query for each analyst (key=analyst name, value=query)
- synthesis_focus: How to combine the results (1 sentence)
- priority_analyst: The most important analyst for this query

{format_instructions}
"""


class PlannerAgent:
    """
    Agent responsible for query decomposition and analyst routing.
    
    Analyzes incoming queries to determine:
    1. Which analysts should be engaged
    2. What focused sub-query each analyst should receive
    3. How to prioritize and combine results
    """
    
    def __init__(
        self,
        session: Session,
        model: str = "claude-3-5-sonnet",
        temperature: float = 0.3  # Lower temperature for more deterministic routing
    ):
        """
        Initialize the Planner Agent.
        
        Args:
            session: Active Snowflake session
            model: Cortex model for planning
            temperature: LLM temperature (lower = more deterministic)
        """
        self.session = session
        self.model = model
        
        self.llm = ChatSnowflake(
            session=session,
            model=model,
            temperature=temperature
        )
        
        self.parser = JsonOutputParser(pydantic_object=PlannerOutput)
        
        self.prompt = ChatPromptTemplate.from_template(PLANNER_PROMPT)
        
        self.chain = self.prompt | self.llm | self.parser
    
    def plan(self, query: str) -> PlannerOutput:
        """
        Generate an execution plan for the given query.
        
        Args:
            query: User's question/request
            
        Returns:
            PlannerOutput: Structured plan with analyst assignments
        """
        try:
            result = self.chain.invoke({
                "query": query,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # Validate analysts
            valid_analysts = {"review_analyst", "market_analyst", "purchase_analyst"}
            result["analysts"] = [a for a in result.get("analysts", []) if a in valid_analysts]
            
            # Ensure at least one analyst
            if not result["analysts"]:
                result["analysts"] = ["review_analyst"]
                result["sub_queries"] = {"review_analyst": query}
            
            # Ensure sub_queries has all selected analysts
            for analyst in result["analysts"]:
                if analyst not in result.get("sub_queries", {}):
                    result["sub_queries"][analyst] = query
            
            return PlannerOutput(**result)
            
        except Exception as e:
            # Fallback: use all analysts with original query
            return PlannerOutput(
                analysts=["review_analyst", "market_analyst", "purchase_analyst"],
                sub_queries={
                    "review_analyst": query,
                    "market_analyst": query,
                    "purchase_analyst": query
                },
                synthesis_focus="Provide comprehensive analysis combining all perspectives",
                priority_analyst="review_analyst"
            )
    
    async def plan_async(self, query: str) -> PlannerOutput:
        """
        Generate an execution plan asynchronously.
        
        Args:
            query: User's question/request
            
        Returns:
            PlannerOutput: Structured plan with analyst assignments
        """
        try:
            result = await self.chain.ainvoke({
                "query": query,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # Validate analysts
            valid_analysts = {"review_analyst", "market_analyst", "purchase_analyst"}
            result["analysts"] = [a for a in result.get("analysts", []) if a in valid_analysts]
            
            if not result["analysts"]:
                result["analysts"] = ["review_analyst"]
                result["sub_queries"] = {"review_analyst": query}
            
            for analyst in result["analysts"]:
                if analyst not in result.get("sub_queries", {}):
                    result["sub_queries"][analyst] = query
            
            return PlannerOutput(**result)
            
        except Exception as e:
            return PlannerOutput(
                analysts=["review_analyst", "market_analyst", "purchase_analyst"],
                sub_queries={
                    "review_analyst": query,
                    "market_analyst": query,
                    "purchase_analyst": query
                },
                synthesis_focus="Provide comprehensive analysis combining all perspectives",
                priority_analyst="review_analyst"
            )
    
    def get_analyst_description(self, analyst_name: str) -> str:
        """Get description for an analyst."""
        descriptions = {
            "review_analyst": "Car Reviews & Ratings Expert",
            "market_analyst": "Market Trends & Competitive Intelligence",
            "purchase_analyst": "Purchase Recommendations & Dealer Finder"
        }
        return descriptions.get(analyst_name, "Unknown Analyst")
