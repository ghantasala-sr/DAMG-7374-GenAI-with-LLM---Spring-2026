"""
Review Analyst - Car Reviews & Ratings Analysis.

Uses Snowflake Cortex Search Service for RAG-based review analysis.
Specializes in sentiment analysis, rating aggregation, and identifying
common issues and strengths from owner reviews.
"""

import os
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from snowflake.snowpark import Session
from langchain_snowflake import (
    ChatSnowflake,
    SnowflakeCortexSearchRetriever,
    format_cortex_search_documents
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from .base_analyst import BaseAnalyst, AnalystResult

load_dotenv()


REVIEW_ANALYST_PROMPT = """You are a car reviews expert analyst. Your role is to analyze 
owner reviews and provide detailed insights about vehicles.

Based on the following car reviews retrieved from our database, provide a comprehensive analysis:

=== RETRIEVED REVIEWS ===
{context}
=========================

User Query: {query}

Provide your analysis in the following structure:

## Overall Sentiment
[Positive/Negative/Mixed - with brief explanation]

## Rating Summary
[Average rating and distribution insights]

## Key Strengths
- [Bullet points of commonly praised features]

## Common Issues
- [Bullet points of frequently mentioned problems]

## Reliability Insights
[Assessment of long-term reliability based on reviews]

## Recommendation
[Your expert recommendation based on the review analysis]

Be specific, cite actual reviews where relevant, and maintain objectivity.
"""


class ReviewAnalyst(BaseAnalyst):
    """
    Analyst specializing in car reviews and ratings analysis.
    
    Uses Snowflake Cortex Search Service for semantic retrieval of relevant
    car reviews and synthesizes insights using LLM analysis.
    
    Features:
    - RAG-based review retrieval
    - Sentiment analysis
    - Rating aggregation
    - Issue identification
    - Reliability assessment
    """
    
    def __init__(
        self,
        session: Session,
        service_name: str = "review_search_service",
        database: Optional[str] = None,
        schema: Optional[str] = None,
        model: str = "claude-3-5-sonnet",
        temperature: float = 0.7,
        retrieval_limit: int = 5
    ):
        """
        Initialize the Review Analyst.
        
        Args:
            session: Active Snowflake session
            service_name: Name of Cortex Search Service for reviews
            database: Snowflake database (defaults to env SNOWFLAKE_DATABASE)
            schema: Snowflake schema (defaults to env SNOWFLAKE_SCHEMA)
            model: Cortex model for analysis
            temperature: LLM temperature
            retrieval_limit: Number of reviews to retrieve per query
        """
        super().__init__(session, model, temperature)
        
        self.service_name = service_name
        self.retrieval_limit = retrieval_limit
        
        # Get database/schema from env if not provided
        self.database = database or os.getenv("SNOWFLAKE_DATABASE")
        self.schema = schema or os.getenv("SNOWFLAKE_SCHEMA")
        # Force uppercase for Snowflake Object Identifiers
        db_upper = self.database.upper() if self.database else ""
        schema_upper = self.schema.upper() if self.schema else ""
        service_upper = service_name.upper()
        
        # Construct fully qualified service name (database.schema.service)
        fully_qualified_service = f"{db_upper}.{schema_upper}.{service_upper}"
        
        # Initialize Cortex Search Retriever with correct parameters
        self.retriever = SnowflakeCortexSearchRetriever(
            session=session,
            database=db_upper,
            schema=schema_upper,
            service_name=fully_qualified_service,
            content_field="REVIEW_TEXT",
            k=retrieval_limit
        )
        
        # Build the RAG chain
        self.prompt = ChatPromptTemplate.from_template(REVIEW_ANALYST_PROMPT)
        
        self.chain = (
            {
                "context": self.retriever | format_cortex_search_documents,
                "query": RunnablePassthrough()
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
    
    @property
    def name(self) -> str:
        return "review_analyst"
    
    @property
    def description(self) -> str:
        return "Analyzes car reviews, ratings, sentiment, reliability, and owner experiences"
    
    def analyze(self, query: str) -> AnalystResult:
        """
        Perform synchronous review analysis.
        
        Args:
            query: User's question about car reviews
            
        Returns:
            AnalystResult: Structured analysis with sentiment, ratings, issues
        """
        start_time = time.time()
        
        # Retrieve relevant reviews first (for metadata)
        retrieved_docs = self.retriever.invoke(query)
        
        # Run the full RAG chain
        analysis = self.chain.invoke(query)
        
        execution_time = (time.time() - start_time) * 1000
        
        # Extract metadata from retrieved documents
        sources = []
        ratings = []
        for doc in retrieved_docs:
            meta = doc.metadata
            sources.append({
                "make": meta.get("CAR_MAKE", "Unknown"),
                "model": meta.get("CAR_MODEL", "Unknown"),
                "year": meta.get("REVIEW_YEAR", "N/A"),
                "rating": meta.get("RATING", 0)
            })
            if meta.get("RATING"):
                ratings.append(float(meta.get("RATING", 0)))
        
        # Calculate average rating
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        return self._create_result(
            query=query,
            analysis=analysis,
            data={
                "reviews_analyzed": len(retrieved_docs),
                "average_rating": round(avg_rating, 2),
                "rating_count": len(ratings),
                "cars_covered": list(set(f"{s['make']} {s['model']}" for s in sources))
            },
            confidence=0.85 if len(retrieved_docs) >= 3 else 0.6,
            sources=sources,
            execution_time_ms=execution_time
        )
    
    async def analyze_async(self, query: str) -> AnalystResult:
        """
        Perform asynchronous review analysis.
        
        Args:
            query: User's question about car reviews
            
        Returns:
            AnalystResult: Structured analysis with sentiment, ratings, issues
        """
        start_time = time.time()
        
        # Retrieve relevant reviews (async)
        retrieved_docs = await self.retriever.ainvoke(query)
        
        # Run the full RAG chain (async)
        analysis = await self.chain.ainvoke(query)
        
        execution_time = (time.time() - start_time) * 1000
        
        # Extract metadata from retrieved documents
        sources = []
        ratings = []
        for doc in retrieved_docs:
            meta = doc.metadata
            sources.append({
                "make": meta.get("CAR_MAKE", "Unknown"),
                "model": meta.get("CAR_MODEL", "Unknown"),
                "year": meta.get("REVIEW_YEAR", "N/A"),
                "rating": meta.get("RATING", 0)
            })
            if meta.get("RATING"):
                ratings.append(float(meta.get("RATING", 0)))
        
        # Calculate average rating
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        return self._create_result(
            query=query,
            analysis=analysis,
            data={
                "reviews_analyzed": len(retrieved_docs),
                "average_rating": round(avg_rating, 2),
                "rating_count": len(ratings),
                "cars_covered": list(set(f"{s['make']} {s['model']}" for s in sources))
            },
            confidence=0.85 if len(retrieved_docs) >= 3 else 0.6,
            sources=sources,
            execution_time_ms=execution_time
        )
