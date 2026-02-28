"""
Base Analyst Abstract Class.

Defines the interface for all specialized car analyst agents.
Each analyst must implement the analyze() method for both sync and async execution.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
from snowflake.snowpark import Session
from langchain_snowflake import ChatSnowflake


@dataclass
class AnalystResult:
    """Standardized result structure for analyst outputs."""
    analyst_name: str
    query: str
    analysis: str
    data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    sources: list = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "analyst_name": self.analyst_name,
            "query": self.query,
            "analysis": self.analysis,
            "data": self.data,
            "confidence": self.confidence,
            "sources": self.sources,
            "timestamp": self.timestamp,
            "execution_time_ms": self.execution_time_ms
        }


class BaseAnalyst(ABC):
    """
    Abstract base class for all car analyst agents.
    
    Each analyst specializes in a specific domain:
    - ReviewAnalyst: Car reviews, ratings, sentiment from Cortex Search
    - MarketAnalyst: Market trends, pricing, competitive analysis
    - PurchaseAnalyst: Budget recommendations, dealer locations
    
    Attributes:
        name: Unique identifier for the analyst
        description: Brief description of analyst capabilities
        session: Snowflake session for data access
        llm: ChatSnowflake instance for LLM inference
        model: Name of the Cortex model to use
    """
    
    def __init__(
        self,
        session: Session,
        model: str = "claude-3-5-sonnet",
        temperature: float = 0.7
    ):
        """
        Initialize the analyst with Snowflake session and LLM.
        
        Args:
            session: Active Snowflake Snowpark session
            model: Cortex model name for LLM inference
            temperature: Sampling temperature for response generation
        """
        self.session = session
        self.model = model
        self.temperature = temperature
        self.llm = ChatSnowflake(
            session=session,
            model=model,
            temperature=temperature
        )
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the analyst."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Brief description of analyst capabilities."""
        pass
    
    @abstractmethod
    def analyze(self, query: str) -> AnalystResult:
        """
        Perform synchronous analysis on the given query.
        
        Args:
            query: The analysis query/question
            
        Returns:
            AnalystResult: Structured analysis result
        """
        pass
    
    @abstractmethod
    async def analyze_async(self, query: str) -> AnalystResult:
        """
        Perform asynchronous analysis on the given query.
        
        Args:
            query: The analysis query/question
            
        Returns:
            AnalystResult: Structured analysis result
        """
        pass
    
    def _create_result(
        self,
        query: str,
        analysis: str,
        data: Optional[Dict[str, Any]] = None,
        confidence: float = 0.8,
        sources: Optional[list] = None,
        execution_time_ms: float = 0.0
    ) -> AnalystResult:
        """
        Helper method to create standardized analyst results.
        
        Args:
            query: Original query
            analysis: Generated analysis text
            data: Additional structured data
            confidence: Confidence score (0.0 to 1.0)
            sources: List of data sources used
            execution_time_ms: Execution time in milliseconds
            
        Returns:
            AnalystResult: Structured result object
        """
        return AnalystResult(
            analyst_name=self.name,
            query=query,
            analysis=analysis,
            data=data or {},
            confidence=confidence,
            sources=sources or [],
            execution_time_ms=execution_time_ms
        )
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', model='{self.model}')"
