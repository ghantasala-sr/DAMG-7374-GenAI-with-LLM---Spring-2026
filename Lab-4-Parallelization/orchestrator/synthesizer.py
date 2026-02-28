"""
Synthesizer - Result Aggregation & Report Generation.

Combines results from multiple parallel analysts into a unified,
comprehensive report using LLM synthesis.
"""

import time
from typing import Dict, Any, Optional
from snowflake.snowpark import Session
from langchain_snowflake import ChatSnowflake
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from analysts.base_analyst import AnalystResult
from .parallel_executor import ParallelExecutionResult


SYNTHESIS_PROMPT = """You are a senior automotive analyst creating a comprehensive report
by combining insights from multiple specialist analysts.

=== ANALYST REPORTS ===

{analyst_reports}

=======================

Original User Query: {query}

Synthesis Focus: {synthesis_focus}

Create a unified analyst report with the following structure:

# 🚗 Car Analyst Report

## Executive Summary
[2-3 sentence high-level summary answering the user's main question]

## Key Findings

### From Reviews Analysis
[Key insights from review analyst, if available]

### From Market Analysis  
[Key insights from market analyst, if available]

### From Purchase Analysis
[Key insights from purchase analyst, if available]

## Data Highlights
| Metric | Value |
|--------|-------|
[Include 3-5 key data points from across all analyses]

## Recommendation
[Clear, actionable recommendation based on combined analysis]

## Confidence Assessment
[How confident are we in these findings? What limitations exist?]

---
*Report generated from {analyst_count} parallel analyst(s) in {execution_time}ms*

Make the report cohesive, avoid redundancy, and highlight the most important insights.
Cross-reference between analysts where their findings support or contradict each other.
"""


class Synthesizer:
    """
    Synthesizes results from multiple analysts into a unified report.
    
    Features:
    - Combines parallel analyst outputs
    - Generates executive summaries
    - Highlights key data points
    - Provides unified recommendations
    - Assesses confidence levels
    """
    
    def __init__(
        self,
        session: Session,
        model: str = "claude-3-5-sonnet",
        temperature: float = 0.7
    ):
        """
        Initialize the Synthesizer.
        
        Args:
            session: Active Snowflake session
            model: Cortex model for synthesis
            temperature: LLM temperature
        """
        self.session = session
        self.model = model
        
        self.llm = ChatSnowflake(
            session=session,
            model=model,
            temperature=temperature
        )
        
        self.prompt = ChatPromptTemplate.from_template(SYNTHESIS_PROMPT)
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def _format_analyst_reports(
        self,
        results: Dict[str, AnalystResult]
    ) -> str:
        """
        Format analyst results into a structured text block.
        
        Args:
            results: Dictionary of analyst results
            
        Returns:
            Formatted string of all analyst reports
        """
        formatted_reports = []
        
        for analyst_name, result in results.items():
            # Create header for each analyst
            header = self._get_analyst_header(analyst_name)
            
            report = f"""
### {header}
**Query:** {result.query}
**Confidence:** {result.confidence:.0%}
**Execution Time:** {result.execution_time_ms:.0f}ms

**Analysis:**
{result.analysis}

**Key Data:**
{self._format_data(result.data)}

**Sources:** {len(result.sources)} source(s) consulted
"""
            formatted_reports.append(report)
        
        return "\n---\n".join(formatted_reports)
    
    def _get_analyst_header(self, analyst_name: str) -> str:
        """Get display header for analyst."""
        headers = {
            "review_analyst": "📊 Review Analyst Report",
            "market_analyst": "📈 Market Analyst Report",
            "purchase_analyst": "💰 Purchase Analyst Report"
        }
        return headers.get(analyst_name, f"📋 {analyst_name} Report")
    
    def _format_data(self, data: Dict[str, Any]) -> str:
        """Format data dictionary into readable bullet points."""
        if not data:
            return "No additional data"
        
        lines = []
        for key, value in data.items():
            # Format key nicely
            formatted_key = key.replace("_", " ").title()
            
            # Format value
            if isinstance(value, list):
                value_str = ", ".join(str(v) for v in value) if value else "None"
            elif isinstance(value, float):
                value_str = f"{value:.2f}"
            else:
                value_str = str(value) if value else "N/A"
            
            lines.append(f"- {formatted_key}: {value_str}")
        
        return "\n".join(lines)
    
    def synthesize(
        self,
        execution_result: ParallelExecutionResult,
        original_query: str,
        synthesis_focus: str = "Provide comprehensive analysis"
    ) -> Dict[str, Any]:
        """
        Synthesize parallel execution results into a unified report.
        
        Args:
            execution_result: Results from parallel analyst execution
            original_query: The user's original question
            synthesis_focus: Guidance on how to combine results
            
        Returns:
            Dictionary with synthesized report and metadata
        """
        start_time = time.time()
        
        # Get successful results
        successful_results = execution_result.successful_results
        
        if not successful_results:
            return {
                "report": "❌ No analyst results available. All analysts failed to execute.",
                "execution_time_ms": (time.time() - start_time) * 1000,
                "analyst_count": 0,
                "success": False
            }
        
        # Format analyst reports
        analyst_reports = self._format_analyst_reports(successful_results)
        
        # Generate synthesized report
        report = self.chain.invoke({
            "analyst_reports": analyst_reports,
            "query": original_query,
            "synthesis_focus": synthesis_focus,
            "analyst_count": len(successful_results),
            "execution_time": f"{execution_result.total_time_ms:.0f}"
        })
        
        synthesis_time = (time.time() - start_time) * 1000
        
        return {
            "report": report,
            "execution_time_ms": synthesis_time,
            "analyst_count": len(successful_results),
            "failed_analysts": execution_result.failed_analysts,
            "total_pipeline_time_ms": execution_result.total_time_ms + synthesis_time,
            "success": True,
            "metadata": {
                "analysts_used": list(successful_results.keys()),
                "model": self.model,
                "original_query": original_query
            }
        }
    
    async def synthesize_async(
        self,
        execution_result: ParallelExecutionResult,
        original_query: str,
        synthesis_focus: str = "Provide comprehensive analysis"
    ) -> Dict[str, Any]:
        """
        Asynchronously synthesize parallel execution results.
        
        Args:
            execution_result: Results from parallel analyst execution
            original_query: The user's original question
            synthesis_focus: Guidance on how to combine results
            
        Returns:
            Dictionary with synthesized report and metadata
        """
        start_time = time.time()
        
        successful_results = execution_result.successful_results
        
        if not successful_results:
            return {
                "report": "❌ No analyst results available. All analysts failed to execute.",
                "execution_time_ms": (time.time() - start_time) * 1000,
                "analyst_count": 0,
                "success": False
            }
        
        analyst_reports = self._format_analyst_reports(successful_results)
        
        # Async synthesis
        report = await self.chain.ainvoke({
            "analyst_reports": analyst_reports,
            "query": original_query,
            "synthesis_focus": synthesis_focus,
            "analyst_count": len(successful_results),
            "execution_time": f"{execution_result.total_time_ms:.0f}"
        })
        
        synthesis_time = (time.time() - start_time) * 1000
        
        return {
            "report": report,
            "execution_time_ms": synthesis_time,
            "analyst_count": len(successful_results),
            "failed_analysts": execution_result.failed_analysts,
            "total_pipeline_time_ms": execution_result.total_time_ms + synthesis_time,
            "success": True,
            "metadata": {
                "analysts_used": list(successful_results.keys()),
                "model": self.model,
                "original_query": original_query
            }
        }


def create_quick_summary(results: Dict[str, AnalystResult]) -> str:
    """
    Create a quick text summary without LLM synthesis.
    
    Useful for debugging or when LLM synthesis is not needed.
    
    Args:
        results: Dictionary of analyst results
        
    Returns:
        Quick summary string
    """
    if not results:
        return "No results available."
    
    lines = ["## Quick Summary\n"]
    
    for name, result in results.items():
        lines.append(f"### {name}")
        lines.append(f"- Confidence: {result.confidence:.0%}")
        lines.append(f"- Time: {result.execution_time_ms:.0f}ms")
        lines.append(f"- Sources: {len(result.sources)}")
        lines.append("")
    
    return "\n".join(lines)
