"""
Market Analyst - Automotive Market Trends & Competitive Analysis.

Analyzes market trends, pricing data, news sentiment, and competitive
landscape using external news APIs and Cortex sentiment analysis.
"""

import os
import time
import aiohttp
import requests
from typing import Dict, Any, List, Optional
from snowflake.snowpark import Session
from langchain_snowflake import ChatSnowflake, CortexSentimentTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

from .base_analyst import BaseAnalyst, AnalystResult

load_dotenv()


MARKET_ANALYST_PROMPT = """You are an automotive market analyst specializing in industry trends,
pricing analysis, and competitive intelligence.

Based on the following market data and news, provide a comprehensive market analysis:

=== MARKET NEWS & DATA ===
{news_data}
==========================

=== SENTIMENT ANALYSIS ===
{sentiment_data}
==========================

User Query: {query}

Provide your analysis in the following structure:

## Market Overview
[Current state of the market segment relevant to the query]

## Pricing Trends
[Price movements, MSRP changes, incentives, market value trends]

## Competitive Landscape
[How this vehicle/brand compares to competitors]

## Industry News Highlights
[Key recent developments affecting this segment]

## Market Sentiment
[Overall market sentiment - bullish/bearish with explanation]

## Investment/Purchase Timing
[Is this a good time to buy? Market timing insights]

Be data-driven and cite specific news sources where applicable.
"""


class MarketAnalyst(BaseAnalyst):
    """
    Analyst specializing in automotive market trends and competitive analysis.
    
    Features:
    - Real-time automotive news retrieval via SerpAPI
    - Sentiment analysis using Cortex AI
    - Pricing trend analysis
    - Competitive landscape assessment
    - Market timing recommendations
    """
    
    def __init__(
        self,
        session: Session,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        model: str = "mixtral-8x7b",
        temperature: float = 0.7,
        news_limit: int = 5
    ):
        """
        Initialize the Market Analyst.
        
        Args:
            session: Active Snowflake session
            database: Snowflake database (defaults to env SNOWFLAKE_DATABASE)
            schema: Snowflake schema (defaults to env SNOWFLAKE_SCHEMA)
            model: Cortex model for analysis (mixtral recommended for speed)
            temperature: LLM temperature
            news_limit: Number of news articles to fetch
        """
        super().__init__(session, model, temperature)
        
        self.news_limit = news_limit
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        
        # Get database/schema from env if not provided
        self.database = database or os.getenv("SNOWFLAKE_DATABASE")
        self.schema = schema or os.getenv("SNOWFLAKE_SCHEMA")
        
        # Initialize Cortex Sentiment Tool with required schema
        self.sentiment_tool = CortexSentimentTool(
            session=session,
            database=self.database,
            schema=self.schema
        )
        
        # Build the analysis prompt
        self.prompt = ChatPromptTemplate.from_template(MARKET_ANALYST_PROMPT)
        
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    @property
    def name(self) -> str:
        return "market_analyst"
    
    @property
    def description(self) -> str:
        return "Analyzes market trends, pricing, competitive landscape, and industry news"
    
    def _fetch_automotive_news(self, query: str) -> List[Dict[str, Any]]:
        """
        Fetch automotive news from SerpAPI.
        
        Args:
            query: Search query for news
            
        Returns:
            List of news article dictionaries
        """
        if not self.serpapi_key:
            return [{"title": "News API not configured", "snippet": "Set SERPAPI_API_KEY"}]
        
        params = {
            "q": f"automotive cars {query}",
            "api_key": self.serpapi_key,
            "num": self.news_limit,
            "tbm": "nws"  # News search
        }
        
        try:
            response = requests.get(
                "https://serpapi.com/search",
                params=params,
                timeout=10
            )
            results = response.json().get("news_results", [])
            return results[:self.news_limit]
        except Exception as e:
            return [{"title": "News fetch failed", "snippet": str(e)}]
    
    async def _fetch_automotive_news_async(self, query: str) -> List[Dict[str, Any]]:
        """
        Fetch automotive news asynchronously.
        
        Args:
            query: Search query for news
            
        Returns:
            List of news article dictionaries
        """
        if not self.serpapi_key:
            return [{"title": "News API not configured", "snippet": "Set SERPAPI_API_KEY"}]
        
        params = {
            "q": f"automotive cars {query}",
            "api_key": self.serpapi_key,
            "num": self.news_limit,
            "tbm": "nws"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://serpapi.com/search",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    data = await response.json()
                    return data.get("news_results", [])[:self.news_limit]
        except Exception as e:
            return [{"title": "News fetch failed", "snippet": str(e)}]
    
    def _format_news_data(self, news_items: List[Dict[str, Any]]) -> str:
        """Format news items into readable text."""
        if not news_items:
            return "No recent news available for this query."
        
        formatted = []
        for item in news_items:
            title = item.get("title", "No title")
            snippet = item.get("snippet", "No description")
            source = item.get("source", "Unknown")
            date = item.get("date", "Unknown date")
            formatted.append(f"📰 {title}\n   Source: {source} | {date}\n   {snippet}\n")
        
        return "\n".join(formatted)
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text using Cortex.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis result
        """
        try:
            result = self.sentiment_tool.invoke(text)
            return {"sentiment": result, "analyzed": True}
        except Exception as e:
            return {"sentiment": "neutral", "analyzed": False, "error": str(e)}
    
    def analyze(self, query: str) -> AnalystResult:
        """
        Perform synchronous market analysis.
        
        Args:
            query: User's market-related question
            
        Returns:
            AnalystResult: Comprehensive market analysis
        """
        start_time = time.time()
        
        # Fetch news data
        news_items = self._fetch_automotive_news(query)
        news_text = self._format_news_data(news_items)
        
        # Analyze sentiment of news headlines
        headlines = " ".join([item.get("title", "") for item in news_items])
        sentiment_result = self._analyze_sentiment(headlines) if headlines else {"sentiment": "neutral"}
        
        # Generate analysis
        analysis = self.chain.invoke({
            "news_data": news_text,
            "sentiment_data": f"Overall news sentiment: {sentiment_result.get('sentiment', 'neutral')}",
            "query": query
        })
        
        execution_time = (time.time() - start_time) * 1000
        
        # Compile sources
        sources = [
            {
                "title": item.get("title", "Unknown"),
                "source": item.get("source", "Unknown"),
                "date": item.get("date", "Unknown"),
                "link": item.get("link", "")
            }
            for item in news_items
        ]
        
        return self._create_result(
            query=query,
            analysis=analysis,
            data={
                "news_count": len(news_items),
                "overall_sentiment": sentiment_result.get("sentiment", "neutral"),
                "market_segment": self._extract_segment(query)
            },
            confidence=0.75 if len(news_items) >= 3 else 0.5,
            sources=sources,
            execution_time_ms=execution_time
        )
    
    async def analyze_async(self, query: str) -> AnalystResult:
        """
        Perform asynchronous market analysis.
        
        Args:
            query: User's market-related question
            
        Returns:
            AnalystResult: Comprehensive market analysis
        """
        start_time = time.time()
        
        # Fetch news data asynchronously
        news_items = await self._fetch_automotive_news_async(query)
        news_text = self._format_news_data(news_items)
        
        # Analyze sentiment
        headlines = " ".join([item.get("title", "") for item in news_items])
        sentiment_result = self._analyze_sentiment(headlines) if headlines else {"sentiment": "neutral"}
        
        # Generate analysis asynchronously
        analysis = await self.chain.ainvoke({
            "news_data": news_text,
            "sentiment_data": f"Overall news sentiment: {sentiment_result.get('sentiment', 'neutral')}",
            "query": query
        })
        
        execution_time = (time.time() - start_time) * 1000
        
        sources = [
            {
                "title": item.get("title", "Unknown"),
                "source": item.get("source", "Unknown"),
                "date": item.get("date", "Unknown"),
                "link": item.get("link", "")
            }
            for item in news_items
        ]
        
        return self._create_result(
            query=query,
            analysis=analysis,
            data={
                "news_count": len(news_items),
                "overall_sentiment": sentiment_result.get("sentiment", "neutral"),
                "market_segment": self._extract_segment(query)
            },
            confidence=0.75 if len(news_items) >= 3 else 0.5,
            sources=sources,
            execution_time_ms=execution_time
        )
    
    def _extract_segment(self, query: str) -> str:
        """Extract market segment from query."""
        segments = {
            "suv": "SUV/Crossover",
            "sedan": "Sedan",
            "truck": "Pickup Truck",
            "ev": "Electric Vehicle",
            "electric": "Electric Vehicle",
            "hybrid": "Hybrid",
            "luxury": "Luxury",
            "compact": "Compact",
            "sports": "Sports Car"
        }
        query_lower = query.lower()
        for key, segment in segments.items():
            if key in query_lower:
                return segment
        return "General Automotive"
