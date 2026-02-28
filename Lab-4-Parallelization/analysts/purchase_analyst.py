"""
Purchase Analyst - Car Purchase Recommendations & Dealer Finder.

Provides purchase recommendations based on budget, features, and location.
Integrates Google Maps for dealer discovery and Cortex for analysis.
"""

import os
import time
import asyncio
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
from snowflake.snowpark import Session
from langchain_snowflake import ChatSnowflake
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

try:
    import googlemaps
    GOOGLEMAPS_AVAILABLE = True
except ImportError:
    GOOGLEMAPS_AVAILABLE = False

from .base_analyst import BaseAnalyst, AnalystResult

load_dotenv()


PURCHASE_ANALYST_PROMPT = """You are an automotive purchase advisor helping buyers make 
informed decisions based on their budget, needs, and preferences.

=== BUDGET & REQUIREMENTS ===
{requirements}
=============================

=== NEARBY DEALERS ===
{dealer_data}
======================

User Query: {query}

Provide your purchase recommendation in the following structure:

## Budget Analysis
[How the requested vehicle(s) fit within budget, including taxes, fees, insurance estimates]

## Feature Match Score
[How well the vehicle matches stated needs - rate as percentage]

## Top Recommendations
1. [Best match with price and key features]
2. [Alternative option with price and key features]
3. [Budget-friendly option if applicable]

## Dealer Options
[Summary of nearby dealers with ratings and notes]

## Negotiation Tips
[Specific tips for getting the best deal on this vehicle]

## Total Cost of Ownership
[Estimated 5-year costs: purchase, fuel, maintenance, insurance, depreciation]

## Final Recommendation
[Your expert recommendation with reasoning]

Be specific with numbers and provide actionable advice.
"""


class PurchaseAnalyst(BaseAnalyst):
    """
    Analyst specializing in purchase recommendations and dealer discovery.
    
    Features:
    - Budget analysis and affordability assessment
    - Feature matching against user requirements
    - Google Maps integration for dealer discovery
    - Total cost of ownership estimation
    - Negotiation guidance
    """
    
    def __init__(
        self,
        session: Session,
        model: str = "claude-3-5-sonnet",
        temperature: float = 0.7,
        dealer_limit: int = 5
    ):
        """
        Initialize the Purchase Analyst.
        
        Args:
            session: Active Snowflake session
            model: Cortex model for analysis
            temperature: LLM temperature
            dealer_limit: Number of dealers to find
        """
        super().__init__(session, model, temperature)
        
        self.dealer_limit = dealer_limit
        self.gmaps_key = os.getenv("GOOGLE_MAPS_API_KEY")
        
        # Initialize Google Maps client if available
        if GOOGLEMAPS_AVAILABLE and self.gmaps_key:
            self.gmaps = googlemaps.Client(key=self.gmaps_key)
        else:
            self.gmaps = None
        
        # Build the analysis prompt
        self.prompt = ChatPromptTemplate.from_template(PURCHASE_ANALYST_PROMPT)
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    @property
    def name(self) -> str:
        return "purchase_analyst"
    
    @property
    def description(self) -> str:
        return "Provides purchase recommendations, budget analysis, and dealer locations"
    
    def _find_dealers(self, query: str) -> List[Dict[str, Any]]:
        """
        Find nearby car dealerships using Google Maps.
        
        Args:
            query: Search query (e.g., "Toyota dealership near Boston")
            
        Returns:
            List of dealer information dictionaries
        """
        if not self.gmaps:
            return [{"name": "Dealer search unavailable", "address": "Configure GOOGLE_MAPS_API_KEY"}]
        
        try:
            # Search for dealerships
            places = self.gmaps.places(f"car dealership {query}")
            results = places.get("results", [])[:self.dealer_limit]
            
            dealers = []
            for place in results:
                dealers.append({
                    "name": place.get("name", "Unknown"),
                    "address": place.get("formatted_address", "Address not available"),
                    "rating": place.get("rating", "N/A"),
                    "total_ratings": place.get("user_ratings_total", 0),
                    "place_id": place.get("place_id", ""),
                    "open_now": place.get("opening_hours", {}).get("open_now", "Unknown")
                })
            
            return dealers if dealers else [{"name": "No dealers found", "address": "Try a different location"}]
            
        except Exception as e:
            return [{"name": "Dealer search failed", "address": str(e)}]
    
    async def _find_dealers_async(self, query: str) -> List[Dict[str, Any]]:
        """
        Find dealers asynchronously using thread executor.
        
        Google Maps client doesn't support async natively,
        so we run it in a thread pool.
        """
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(
                executor,
                self._find_dealers,
                query
            )
    
    def _format_dealer_data(self, dealers: List[Dict[str, Any]]) -> str:
        """Format dealer information into readable text."""
        if not dealers:
            return "No dealer information available."
        
        formatted = []
        for i, dealer in enumerate(dealers, 1):
            rating = dealer.get("rating", "N/A")
            rating_str = f"⭐ {rating}/5" if rating != "N/A" else "No rating"
            total = dealer.get("total_ratings", 0)
            
            formatted.append(
                f"{i}. 📍 {dealer['name']}\n"
                f"   Address: {dealer['address']}\n"
                f"   Rating: {rating_str} ({total} reviews)\n"
            )
        
        return "\n".join(formatted)
    
    def _extract_requirements(self, query: str) -> Dict[str, Any]:
        """
        Extract budget and requirements from query.
        
        Args:
            query: User's purchase query
            
        Returns:
            Dictionary of extracted requirements
        """
        requirements = {
            "budget": None,
            "vehicle_type": None,
            "must_have_features": [],
            "location": None
        }
        
        # Extract budget (look for $ amounts)
        import re
        budget_match = re.search(r'\$[\d,]+k?|\d+k|\d{4,}', query.lower())
        if budget_match:
            budget_str = budget_match.group()
            # Convert to number
            budget_str = budget_str.replace('$', '').replace(',', '').replace('k', '000')
            try:
                requirements["budget"] = int(budget_str)
            except ValueError:
                pass
        
        # Extract vehicle type
        vehicle_types = {
            "suv": "SUV",
            "sedan": "Sedan", 
            "truck": "Pickup Truck",
            "minivan": "Minivan",
            "coupe": "Coupe",
            "hatchback": "Hatchback",
            "convertible": "Convertible",
            "wagon": "Station Wagon"
        }
        query_lower = query.lower()
        for key, vtype in vehicle_types.items():
            if key in query_lower:
                requirements["vehicle_type"] = vtype
                break
        
        # Extract features
        features = ["awd", "4wd", "leather", "sunroof", "navigation", 
                   "hybrid", "electric", "ev", "safety", "carplay", "heated seats"]
        for feature in features:
            if feature in query_lower:
                requirements["must_have_features"].append(feature)
        
        # Extract location hints
        location_patterns = ["near", "in", "around", "close to"]
        for pattern in location_patterns:
            if pattern in query_lower:
                idx = query_lower.find(pattern)
                requirements["location"] = query[idx:idx+50].strip()
                break
        
        return requirements
    
    def _format_requirements(self, requirements: Dict[str, Any]) -> str:
        """Format requirements into readable text."""
        lines = []
        
        if requirements.get("budget"):
            lines.append(f"💰 Budget: ${requirements['budget']:,}")
        else:
            lines.append("💰 Budget: Not specified")
        
        if requirements.get("vehicle_type"):
            lines.append(f"🚗 Vehicle Type: {requirements['vehicle_type']}")
        
        if requirements.get("must_have_features"):
            features = ", ".join(requirements["must_have_features"])
            lines.append(f"✅ Required Features: {features}")
        
        if requirements.get("location"):
            lines.append(f"📍 Location: {requirements['location']}")
        
        return "\n".join(lines) if lines else "No specific requirements extracted"
    
    def analyze(self, query: str) -> AnalystResult:
        """
        Perform synchronous purchase analysis.
        
        Args:
            query: User's purchase-related question
            
        Returns:
            AnalystResult: Purchase recommendation with dealer info
        """
        start_time = time.time()
        
        # Extract requirements from query
        requirements = self._extract_requirements(query)
        requirements_text = self._format_requirements(requirements)
        
        # Find nearby dealers
        dealers = self._find_dealers(query)
        dealer_text = self._format_dealer_data(dealers)
        
        # Generate analysis
        analysis = self.chain.invoke({
            "requirements": requirements_text,
            "dealer_data": dealer_text,
            "query": query
        })
        
        execution_time = (time.time() - start_time) * 1000
        
        # Compile sources (dealers)
        sources = [
            {
                "type": "dealer",
                "name": d.get("name", "Unknown"),
                "address": d.get("address", "Unknown"),
                "rating": d.get("rating", "N/A")
            }
            for d in dealers
        ]
        
        return self._create_result(
            query=query,
            analysis=analysis,
            data={
                "budget": requirements.get("budget"),
                "vehicle_type": requirements.get("vehicle_type"),
                "required_features": requirements.get("must_have_features", []),
                "dealers_found": len([d for d in dealers if "failed" not in d.get("name", "").lower()]),
                "location": requirements.get("location")
            },
            confidence=0.8 if requirements.get("budget") else 0.6,
            sources=sources,
            execution_time_ms=execution_time
        )
    
    async def analyze_async(self, query: str) -> AnalystResult:
        """
        Perform asynchronous purchase analysis.
        
        Args:
            query: User's purchase-related question
            
        Returns:
            AnalystResult: Purchase recommendation with dealer info
        """
        start_time = time.time()
        
        # Extract requirements from query
        requirements = self._extract_requirements(query)
        requirements_text = self._format_requirements(requirements)
        
        # Find nearby dealers asynchronously
        dealers = await self._find_dealers_async(query)
        dealer_text = self._format_dealer_data(dealers)
        
        # Generate analysis asynchronously
        analysis = await self.chain.ainvoke({
            "requirements": requirements_text,
            "dealer_data": dealer_text,
            "query": query
        })
        
        execution_time = (time.time() - start_time) * 1000
        
        sources = [
            {
                "type": "dealer",
                "name": d.get("name", "Unknown"),
                "address": d.get("address", "Unknown"),
                "rating": d.get("rating", "N/A")
            }
            for d in dealers
        ]
        
        return self._create_result(
            query=query,
            analysis=analysis,
            data={
                "budget": requirements.get("budget"),
                "vehicle_type": requirements.get("vehicle_type"),
                "required_features": requirements.get("must_have_features", []),
                "dealers_found": len([d for d in dealers if "failed" not in d.get("name", "").lower()]),
                "location": requirements.get("location")
            },
            confidence=0.8 if requirements.get("budget") else 0.6,
            sources=sources,
            execution_time_ms=execution_time
        )
